"""Unit D (exploratory; PLAN v7 C4, appendix B.2): the decoder-only interface for Gemma 2 2B IT.
Prompt: the chat template with the user message "Repeat this sentence exactly: {S}" and the generation prompt; the model should output S.
Latent: the residual stream after layer l (hidden_states[l] of the HF forward, l = 1..26) at the month token of the user message.
Edit: the latent is replaced during the prefill by a forward hook on layer l (0-based index l - 1); every later position is recomputed
causally from layer l + 1; greedy generation; success = the output equals the target sentence (whitespace-normalised) and generation
ended (end-of-turn or EOS). Chains compose in latent space only (the slot vector); each step is decoded once, only to score it."""
import torch
import torch.nn.functional as Fn
from symutil import *
import sym5_semantics as S
import sym5_evaluator as Ev

GEMMA = '/dataset1/zailong/models/gemma-2-2b-it'
DMODELS = {'gemma': dict(path=GEMMA, eot='<end_of_turn>', attn='eager'),                              # v9: model-generic interface
           'qwen': dict(path='/dataset1/zailong/models/Qwen2.5-1.5B-Instruct', eot='<|im_end|>', attn='sdpa')}
PROMPT = 'Repeat this sentence exactly: {}'


class DEngine:
    def __init__(self, max_new_tokens=64, model='gemma'):
        require_slurm(); cfg = DMODELS[model]; self.name = model; self.eot = cfg['eot']
        from transformers import AutoTokenizer, AutoModelForCausalLM
        self.tok = AutoTokenizer.from_pretrained(cfg['path'], local_files_only=True); self.tok.padding_side = 'left'
        if self.tok.pad_token_id is None: self.tok.pad_token = self.tok.eos_token
        torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False
        if model == 'qwen': torch.backends.cuda.enable_cudnn_sdp(False)              # B300: cuDNN SDPA has no execution plan (DEVIATIONS 4)
        self.model = AutoModelForCausalLM.from_pretrained(cfg['path'], local_files_only=True, dtype=torch.bfloat16, attn_implementation=cfg['attn']).cuda().eval()
        for p in self.model.parameters(): p.requires_grad_(False)
        self.layers = self.model.model.layers; self.L = len(self.layers); self.d = self.model.config.hidden_size
        self.stop = {self.tok.eos_token_id, self.tok.convert_tokens_to_ids(self.eot)}; self.max_new = max_new_tokens
        if model == 'gemma': self.revision = read(EXP / 'composability_mechanisms_v7/data/model_manifest_v8.json')['D']['revision']
        else: self.revision = next(v['revision'] for k, v in read(ROOT / 'data/model_manifest_v9.json').items() if isinstance(v, dict) and v.get('directory') == cfg['path'])

    def prompt(self, text):
        return self.tok.apply_chat_template([dict(role='user', content=PROMPT.format(text))], tokenize=False, add_generation_prompt=True)

    def ids(self, text):
        return self.tok(self.prompt(text), add_special_tokens=False)['input_ids']

    def batch(self, texts):
        b = self.tok([self.prompt(t) for t in texts], add_special_tokens=False, return_tensors='pt', padding=True)
        return b['input_ids'].cuda(), b['attention_mask'].cuda()

    @torch.no_grad()
    def latents(self, texts, pos, layers):
        """Slot vectors after each layer in layers: {l: (B, d) float32}; pos: slot index in the unpadded prompt (per text)."""
        ids, am = self.batch(texts); off = ids.shape[1] - am.sum(1); p = (torch.as_tensor(pos, device='cuda') + off).long(); ar = torch.arange(len(texts), device='cuda')
        hs = self.model(input_ids=ids, attention_mask=am, output_hidden_states=True).hidden_states
        return {l: hs[l][ar, p].float().cpu() for l in layers}

    def _hook(self, l, p, vec):
        ar = torch.arange(len(p), device='cuda')
        def f(mod, args, out):
            h = out[0] if isinstance(out, tuple) else out
            if h.shape[1] == 1: return out                                  # cached generation step: nothing to replace
            h = h.clone(); h[ar, p] = vec.to(h.dtype)
            return (h,) + tuple(out[1:]) if isinstance(out, tuple) else h
        return self.layers[l - 1].register_forward_hook(f)

    @torch.no_grad()
    def generate(self, texts, pos=None, layer=None, vec=None):
        """Greedy outputs [{text, ended}] for the prompts of texts, optionally with the slot latent after layer replaced by vec (B, d)."""
        ids, am = self.batch(texts); hk = None
        if vec is not None:
            off = ids.shape[1] - am.sum(1); p = (torch.as_tensor(pos, device='cuda') + off).long(); hk = self._hook(layer, p, vec.cuda())
        try:
            out = self.model.generate(input_ids=ids, attention_mask=am, max_new_tokens=self.max_new, do_sample=False, num_beams=1,
                                      eos_token_id=list(self.stop), pad_token_id=self.tok.pad_token_id)
        finally:
            if hk is not None: hk.remove()
        res = []
        for row in out[:, ids.shape[1]:].tolist():
            ended = any(t in self.stop for t in row); row = row[:next((i for i, t in enumerate(row) if t in self.stop), len(row))]
            res.append(dict(text=self.tok.decode(row, skip_special_tokens=True).strip(), ended=ended))
        return res

    def ce(self, texts, targets, pos, layer, vec):
        """Teacher-forced CE of the target sentences (+ end of turn) given the prompts with the slot latent replaced by vec (grad flows to vec)."""
        P = [self.ids(t) for t in texts]; T = [self.tok(y, add_special_tokens=False)['input_ids'] + [self.tok.convert_tokens_to_ids(self.eot)] for y in targets]
        n = max(len(a) + len(b) for a, b in zip(P, T)); pad = self.tok.pad_token_id
        ids = torch.full((len(P), n), pad, dtype=torch.long); am = torch.zeros((len(P), n), dtype=torch.long); lab = torch.full((len(P), n), -100, dtype=torch.long); p = []
        for i, (a, b) in enumerate(zip(P, T)):
            o = n - len(a) - len(b); ids[i, o:] = torch.tensor(a + b); am[i, o:] = 1; lab[i, o + len(a):] = torch.tensor(b); p.append(o + pos[i])
        hk = self._hook(layer, torch.tensor(p, device='cuda'), vec)
        try: logits = self.model(input_ids=ids.cuda(), attention_mask=am.cuda()).logits.float()
        finally: hk.remove()
        return Fn.cross_entropy(logits[:, :-1].reshape(-1, logits.shape[-1]), lab[:, 1:].cuda().reshape(-1), ignore_index=-100, reduction='mean')

    def resources(self):
        return dict(max_memory_gb=torch.cuda.max_memory_allocated() / 1e9, device=torch.cuda.get_device_name(0))


def slot_position(eng, w, d='month', t=0):
    """Index of the single token that differs across the N state variants of world w (None if not single-token)."""
    seqs = [eng.ids(S.render(w, s, t)) for s in S.states(d)]
    if len({len(x) for x in seqs}) != 1: return None
    diff = sorted({i for x in seqs for i in range(len(x)) if x[i] != seqs[0][i]}); return diff[0] if len(diff) == 1 else None


def success(out, w, s, d='month', t=0):
    return bool(out['ended'] and Ev.ws_norm(out['text']) == Ev.ws_norm(S.render(w, s, t)))
