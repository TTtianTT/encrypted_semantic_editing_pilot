"""G4 fixed, single-seed diagnosis and one probe-subspace repair."""
import csv, hashlib, json, math, sys, time
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import numpy as np
import torch
from torch import nn
import torch.nn.functional as F
from sklearn.linear_model import RidgeClassifier
from sklearn.metrics import accuracy_score
from transformers.modeling_outputs import BaseModelOutput

HERE = Path(__file__).resolve().parent
V3 = HERE.parent / 'reference_frame_pilot_v3'
sys.path.insert(0, str(V3))
from common import advance, digest, frame, offset_at, render, score, valid  # noqa: E402
from engine import Engine, new_editors  # noqa: E402
import renderer_v1  # noqa: E402

CFG = json.loads((HERE / 'config.json').read_text())
torch.manual_seed(CFG['seed']); np.random.seed(CFG['seed'])
renderer_v1.REL[5] = 'in five days'  # Probe-only positive class; no chain uses this lexical extension.


def rows(path):
    return [json.loads(x) for x in path.read_text().splitlines()]


def write_json(name, value):
    p = HERE / name; p.parent.mkdir(exist_ok=True, parents=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def write_jsonl(name, values):
    p = HERE / name; p.parent.mkdir(exist_ok=True, parents=True)
    with p.open('w') as f:
        for value in values: f.write(json.dumps(value, ensure_ascii=False) + '\n')


def pooled(h, mask, position='mean'):
    if position == 'mean': return (h * mask[..., None]).sum(1) / mask.sum(1).clamp(min=1)[:, None]
    if position == 'bos': return h[:, 0]
    return h[torch.arange(h.size(0), device=h.device), mask.sum(1)-1]


def get_worlds(split):
    return rows(V3 / f'data/{split}_worlds.jsonl')


def eligible_worlds(split):
    worlds = get_worlds(split)
    chosen = []
    for w in worlds:
        f0 = frame(w, CFG['source_offset'])
        fs = [f0]
        for _ in range(5): fs.append(advance(fs[-1], 'T_plus'))
        if valid(w, fs): chosen.append(w)
    assert len(chosen) == CFG['eligible_worlds_per_split'], (split, len(chosen))
    return chosen


def probe_examples(worlds):
    out = []
    for w in worlds:
        for off in CFG['probe_offsets']:
            c = frame(w, off)
            if c['view_date'] < w['record_date']: continue
            for person in ('first', 'third'):
                c = dict(c, perspective=person)
                out.append(dict(world=w, frame=c, offset=off, person=person,
                                text=render(w, c)))
    return out


@torch.no_grad()
def collect_features(eng, examples):
    f = {(layer, pos): [] for layer in CFG['probe_layers'] for pos in CFG['probe_positions']}
    for i in range(0, len(examples), 32):
        x = eng.batch([z['text'] for z in examples[i:i+32]])
        h = eng.model.get_encoder()(**x, output_hidden_states=True)
        for layer in CFG['probe_layers']:
            for pos in CFG['probe_positions']:
                f[layer, pos].append(pooled(h.hidden_states[layer], x.attention_mask, pos).float().cpu().numpy())
        if i % 512 == 0: print('features', i, '/', len(examples), flush=True)
    return {k: np.concatenate(v) for k, v in f.items()}


def train_probes(eng):
    train = probe_examples(get_worlds('train'))
    dev = probe_examples(get_worlds('dev'))
    test = probe_examples(eligible_worlds('test_iid') + eligible_worlds('test_template_ood'))
    xf = collect_features(eng, train); df = collect_features(eng, dev); tf = collect_features(eng, test)
    target = {'offset': lambda z: z['offset'], 'person': lambda z: z['person']}
    for a in ['author', 'recipient', 'action', 'object', 'quantity', 'record_status', 'polarity']:
        target[a] = lambda z, a=a: z['world'][a]
    probes = {}; accuracy = []; test_predictions = {}
    for (layer, pos), x in xf.items():
        for attr, func in target.items():
            y = np.array([func(z) for z in train]); yd = np.array([func(z) for z in dev]); yt = np.array([func(z) for z in test])
            model = RidgeClassifier(alpha=10.0).fit(x, y)
            dp = model.predict(df[layer, pos]); tp = model.predict(tf[layer, pos])
            probes[layer, pos, attr] = model
            accuracy.append(dict(layer=layer, position=pos, attribute=attr, train_n=len(y), dev_n=len(yd), test_n=len(yt), dev_accuracy=float(accuracy_score(yd, dp)), test_accuracy=float(accuracy_score(yt, tp))))
            if layer == 6 and pos == 'mean': test_predictions[attr] = tp.tolist()
    write_json('probe_accuracy.json', accuracy)
    write_json('probe_split.json', dict(train_worlds=len(get_worlds('train')), dev_worlds=len(get_worlds('dev')), test_worlds=106,
                                        train_examples=len(train), dev_examples=len(dev), test_examples=len(test),
                                        train_world_ids=[w['record_id'] for w in get_worlds('train')], dev_world_ids=[w['record_id'] for w in get_worlds('dev')],
                                        test_world_ids=[w['record_id'] for w in eligible_worlds('test_iid') + eligible_worlds('test_template_ood')],
                                        no_test_chain_fit=True, probe_offsets=CFG['probe_offsets']))
    return probes, accuracy


class SubspaceEditor(nn.Module):
    def __init__(self, R, original):
        super().__init__()
        self.register_buffer('R', R)
        self.A = nn.Parameter(R @ original.u.weight @ original.v.weight @ R.T)
        self.b = nn.Parameter(R @ original.b)

    def forward(self, h, mask):
        z = h @ self.R.T
        delta = (z @ self.A.T + self.b) @ self.R
        return h + delta * mask[..., None]


def make_repair(probes, g3):
    W = torch.tensor(probes[6, 'mean', 'offset'].coef_, device='cuda', dtype=torch.float32)
    _, _, vh = torch.linalg.svd(W, full_matrices=False)
    R = vh[:CFG['repair_rank']].contiguous()
    return nn.ModuleDict({op: SubspaceEditor(R, g3[op]) for op in ['T_plus', 'T_minus']}), R


def train_repair(eng, probes, g3):
    editors, R = make_repair(probes, g3)
    train = rows(V3 / 'data/train_G1.jsonl')
    schedule = rows(V3 / 'data/sample_schedule.jsonl')
    worlds = {w['record_id']: w for w in get_worlds('train')}
    opt = torch.optim.AdamW(editors.parameters(), lr=CFG['repair_lr'], weight_decay=0)
    history = []; count = Counter(); start = time.time()
    for entry in schedule:
        indices = entry['pair_indices']; batch = [train[i] for i in indices]
        op = batch[0]['operations'][0]
        if op not in editors: continue
        assert all(r['operations'] == [op] for r in batch)
        x = eng.batch([r['source_text'] for r in batch]); mask = x.attention_mask
        with torch.no_grad(): h0 = eng.model.get_encoder()(**x).last_hidden_state
        h1 = editors[op](h0, mask)
        y1 = [r['target_text'] for r in batch]
        l1 = token_loss(eng, h1, mask, y1)
        with torch.no_grad(): g1, gm1, _ = eng.encode(y1)
        geometry = F.mse_loss(pooled(h1, mask), pooled(g1, gm1))
        inverse = torch.zeros((), device='cuda')
        if op == 'T_plus':
            ids = [i for i, v in enumerate(entry['g2_replace']) if v]
            if ids:
                m2 = mask[ids]; h2 = editors[op](h1[ids], m2)
                y2 = [render(worlds[batch[i]['record_id']], advance(batch[i]['frames'][-1], op)) for i in ids]
                l1 = .5*l1 + .5*token_loss(eng, h2, m2, y2)
                with torch.no_grad(): g2, gm2, _ = eng.encode(y2)
                geometry = .5*geometry + .5*F.mse_loss(pooled(h2, m2), pooled(g2, gm2))
            inverse = F.mse_loss(pooled(editors['T_minus'](h1, mask), mask), pooled(h0, mask))
        else:
            inverse = F.mse_loss(pooled(editors['T_plus'](h1, mask), mask), pooled(h0, mask))
        delta = h1 - h0
        orth = F.mse_loss(delta, (delta @ R.T) @ R)
        lw = CFG['repair_loss']
        loss = lw['token_ce']*l1 + lw['gold_latent']*geometry + lw['inverse']*inverse + lw['orthogonal_drift']*orth
        opt.zero_grad(set_to_none=True); loss.backward(); torch.nn.utils.clip_grad_norm_(editors.parameters(), 1.0); opt.step()
        count[op] += 1
        if count[op] % 50 == 0:
            history.append(dict(step=entry['step'], op=op, op_updates=count[op], loss=float(loss), token_ce=float(l1), gold_latent=float(geometry), inverse=float(inverse), orthogonal=float(orth)))
            print('repair', history[-1], flush=True)
        if count['T_plus'] >= CFG['repair_updates'] and count['T_minus'] >= CFG['repair_updates']: break
    assert count['T_plus'] == count['T_minus'] == CFG['repair_updates'], count
    torch.save(editors.state_dict(), HERE / 'repair.pt')
    write_json('repair_training.json', dict(count=dict(count), history=history, seconds=time.time()-start,
                                             rank=CFG['repair_rank'], losses=CFG['repair_loss'],
                                             no_three_step_training=True, source_checkpoint=str(V3 / 'checkpoints/G3/best.pt')))
    return editors, R


def token_loss(eng, h, mask, texts):
    t = eng.tok(texts, padding=True, truncation=False, return_tensors='pt').input_ids.cuda()
    t[t == eng.tok.pad_token_id] = -100
    return eng.model(encoder_outputs=BaseModelOutput(last_hidden_state=h), attention_mask=mask, labels=t, use_cache=False).loss


PATHS = {
    'plus_chain': ['T_plus']*5,
    'plus_minus': ['T_plus', 'T_minus'],
    'minus_plus': ['T_minus', 'T_plus'],
    'plus_person': ['T_plus', 'P_13'],
    'person_plus': ['P_13', 'T_plus'],
    'plus_plus_person': ['T_plus', 'T_plus', 'P_13'],
}


def active_editor(op, group, g3, repair):
    return repair[op] if group == 'repair' and op in repair else g3[op]


def features_from_h(h, mask):
    return pooled(h, mask).float().detach().cpu().numpy()


def labels_from_probe(probes, h, mask):
    x = features_from_h(h, mask)
    return {attr: model.predict(x).tolist() for (layer, pos, attr), model in probes.items() if layer == 6 and pos == 'mean'}


def vector_distance(a, b, R, train_center=None, train_basis=None):
    av = a.float(); bv = b.float(); d = av-bv
    cosine = 1-F.cosine_similarity(av, bv, dim=-1)
    l2 = d.norm(dim=-1) / bv.norm(dim=-1).clamp(min=1e-8)
    projection = (d @ R.T).norm(dim=-1) / (bv @ R.T).norm(dim=-1).clamp(min=1e-8)
    return cosine, l2, projection


@torch.no_grad()
def evaluate(eng, probes, g3, repair, R, group):
    all_rows = []; latents = {}; gold_cache = {}
    for split in ['test_iid', 'test_template_ood']:
        worlds = eligible_worlds(split)
        for path, ops in PATHS.items():
            for start in range(0, len(worlds), 8):
                ws = worlds[start:start+8]
                fs = [[frame(w, CFG['source_offset'])] for w in ws]
                texts = [render(w, f[0]) for w, f in zip(ws, fs)]
                h, mask, _ = eng.encode(texts)
                prev = None; residuals = []
                for j, op in enumerate(ops):
                    old = h; h = active_editor(op, group, g3, repair)(h, mask)
                    residual = h-old; residuals.append(residual)
                    for f in fs: f.append(advance(f[-1], op))
                    decoded, ended, _, _ = eng.decode(h, mask)
                    pred = labels_from_probe(probes, h, mask)
                    for k, w in enumerate(ws):
                        key = (w['record_id'], fs[k][-1]['view_date'], fs[k][-1]['perspective'])
                        if key not in gold_cache:
                            gh, gm, _ = eng.encode([render(w, fs[k][-1])])
                            gold_cache[key] = pooled(gh, gm)[0].detach()
                        av = pooled(h[k:k+1], mask[k:k+1])[0]
                        gv = gold_cache[key]
                        cos, nl2, proj = vector_distance(av[None], gv[None], R)
                        candidates = []
                        for off in range(-4, 6):
                            cf = frame(w, off, fs[k][-1]['perspective'])
                            if cf['view_date'] < w['record_date']: continue
                            ck = (w['record_id'], cf['view_date'], cf['perspective'])
                            if ck not in gold_cache:
                                ch, cm, _ = eng.encode([render(w, cf)])
                                gold_cache[ck] = pooled(ch, cm)[0].detach()
                            dist = 1-F.cosine_similarity(av[None], gold_cache[ck][None]).item()
                            candidates.append((dist, off))
                        nearest = min(candidates)[1]
                        s = score(decoded[k], fs[k][-1], w, ended[k]); p = s['parsed']
                        src_offset = offset_at(w, fs[k][0]); correct_offset = offset_at(w, fs[k][-1])
                        observed_offset = ((date.fromisoformat(p['event_date'])-date.fromisoformat(fs[k][-1]['view_date'])).days if p else None)
                        rnorm = float(residual[k][mask[k].bool()].float().norm() / math.sqrt(int(mask[k].sum())))
                        rcos = (float(F.cosine_similarity(residuals[-2][k:k+1].flatten(1), residual[k:k+1].flatten(1)).item()) if len(residuals)>1 else None)
                        content_attrs = ['author','recipient','action','object','quantity','record_status','polarity']
                        content_probe_ok = all(pred[a][k] == w[a] for a in content_attrs)
                        rec = dict(group=group, split=split, world_id=w['record_id'], path=path, step=j+1,
                                   operation=op, source_text=texts[k], decoded_text=decoded[k], gold_text=render(w, fs[k][-1]),
                                   gold_frame=fs[k][-1], gold_semantic_state=dict(offset=correct_offset, person=fs[k][-1]['perspective'], content={a:w[a] for a in content_attrs}),
                                   decoded_semantic_state=p, probe={a: pred[a][k] for a in pred},
                                   endpoint_success=bool(s['joint_ok']), fact_preservation=bool(s['nondate_facts_ok']),
                                   parse_unresolved=bool(s['parse_unresolved']), normal_end=bool(ended[k]),
                                   observed_offset=observed_offset, source_offset=src_offset, nearest_gold_offset=nearest,
                                   cosine_distance=float(cos), normalized_l2=float(nl2), projection_distance=float(proj),
                                   residual_norm=rnorm, residual_direction_cosine=rcos, content_probe_ok=content_probe_ok,
                                   mask_length=int(mask[k].sum()))
                        all_rows.append(rec)
                        latent_key = f'{split}/{w["record_id"]}/{path}/{j+1}'
                        latents[latent_key] = dict(latent=h[k].half().cpu(), mask=mask[k].cpu(), gold_frame=fs[k][-1])
                print('evaluated', group, split, path, start+len(ws), '/', len(worlds), flush=True)
    write_jsonl(f'{group}_trajectories.jsonl', all_rows)
    torch.save(latents, HERE / f'{group}_latents.pt')
    return all_rows


def dynamics(eng, g3, repair, R):
    worlds = eligible_worlds('test_iid')[:8]
    x = [render(w, frame(w, 1)) for w in worlds]
    h, m, _ = eng.encode(x)
    out = []
    for group in ['G3','repair']:
        ed = active_editor('T_plus', group, g3, repair)
        xh = h.detach()
        for k in range(5):
            xh = ed(xh, m).detach()
            dirs = torch.randn_like(xh)
            dirs = dirs / dirs.norm(dim=-1, keepdim=True).clamp(min=1e-8)
            _, jvp = torch.autograd.functional.jvp(lambda z: ed(z, m), xh, dirs)
            for i in range(len(worlds)):
                d = jvp[i][m[i].bool()]; v=dirs[i][m[i].bool()]
                out.append(dict(group=group, step=k+1, world_id=worlds[i]['record_id'], random_direction_gain=float(d.norm()/v.norm())))
        for zname, z in [('time_subspace', R[0]), ('orthogonal_random', torch.randn(768,device='cuda'))]:
            z = z / z.norm(); v = z[None,None,:].expand_as(h).contiguous()
            _, jv = torch.autograd.functional.jvp(lambda y: ed(y,m), h, v)
            out.append(dict(group=group, step=0, world_id=zname, directional_gain=float(jv.norm()/v.norm())))
    write_json('jvp_dynamics.json', out)


def main():
    assert digest(V3/'checkpoints/G3/best.pt') == json.loads((V3/'checkpoints/locked.json').read_text())['groups']['G3']
    write_json('provenance.json', dict(config=CFG, g3_checkpoint_sha256=digest(V3/'checkpoints/G3/best.pt'),
                                       bart_sha256=digest(V3.parent.parent/'models/bart-base/model.safetensors'),
                                       data_hashes={p.name:digest(p) for p in (V3/'data').glob('*.jsonl')}, seed=CFG['seed']))
    eng = Engine()
    g3 = new_editors(); g3.load_state_dict(torch.load(V3/'checkpoints/G3/best.pt', weights_only=True))
    probes, _ = train_probes(eng)
    _, R = make_repair(probes, g3)
    baseline = evaluate(eng, probes, g3, None, R, 'G3')
    repair, R = train_repair(eng, probes, g3)
    fixed = evaluate(eng, probes, g3, repair, R, 'repair')
    dynamics(eng, g3, repair, R)
    write_json('run_complete.json', dict(completed=True, baseline_stages=len(baseline), repair_stages=len(fixed),
                                         baseline_latents_sha256=digest(HERE/'G3_latents.pt'), repair_latents_sha256=digest(HERE/'repair_latents.pt'),
                                         repair_checkpoint_sha256=digest(HERE/'repair.pt'), peak_cuda_bytes=torch.cuda.max_memory_allocated()))


if __name__ == '__main__': main()
