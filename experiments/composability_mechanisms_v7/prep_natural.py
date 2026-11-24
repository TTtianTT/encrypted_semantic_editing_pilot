"""v8 preparation (CPU; PLAN v7 C2, appendix B.1 steps 1-6 and 8; step 7, the reconstruction gate, needs the models and is part of v8's
pre-lock GPU work). Source: WikiText-103 raw (HF Salesforce/wikitext, wikitext-103-raw-v1), the train parquet files downloaded in v1
(experiments/symmetry_composability_v1/local/corpus_download; SHA256 recorded). Steps: articles = blocks under level-1 headings ' = T = ';
random 60/15/25 split of articles into train / dev / confirm8 pools (seed 3101); WikiText detokenisation; sentence split; 8-35 words,
ASCII; exactly one month word in one of the forms 'in <Month>', 'in <Month> <Year>', '<Month> <Year>' (year 1000-2099), month != May in
the original, no other month or weekday word, no day number next to the month; the month (with a leading space) a single token in both
backbones' tokenizers; text-level dedupe against every historical render and among sentences. Output: local/natural_candidates.jsonl,
local/natural_candidates_summary.json."""
import hashlib
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path
import pandas as pd
from transformers import AutoTokenizer

HERE = Path(__file__).resolve().parent; REPO = HERE.parents[1]; EXP = REPO / 'experiments'
SRC = sorted((EXP / 'symmetry_composability_v1/local/corpus_download').glob('train-*.parquet'))
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
M = '|'.join(MONTHS); YEAR = r'(1\d{3}|20\d{2})'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def detok(s):
    s = s.replace(' @-@ ', '-').replace(' @,@ ', ',').replace(' @.@ ', '.')
    s = re.sub(r' ([.,;:!?%)])', r'\1', s); s = re.sub(r'\( ', '(', s); s = re.sub(r" (n't|'s|'re|'ve|'ll|'d|'m)\b", r'\1', s)
    s = re.sub(r' " ([^"]*?) "', r' "\1"', s)
    return s.strip()


def match(sent):
    words = re.findall(r"[A-Za-z]+", sent)
    if sum(w in MONTHS for w in words) != 1 or any(w in DAYS for w in words): return None
    mo = next(w for w in words if w in MONTHS)
    if mo == 'May': return None
    i = sent.index(mo)
    if re.search(r'\d\s*$', sent[:i]) or re.match(r'\s*\d{1,2}\b(?!\d)', sent[i + len(mo):]) and not re.match(r'\s+' + YEAR + r'\b', sent[i + len(mo):]): return None
    forms = [(r'\bin ' + mo + r' ' + YEAR + r'\b', 'in M Y'), (r'\bin ' + mo + r'\b', 'in M'), (r'\b' + mo + r' ' + YEAR + r'\b', 'M Y')]
    for pat, form in forms:
        if re.search(pat, sent): return dict(month=mo, form=form, char=i)
    return None


def history_texts():
    seen = set()
    for D in sorted(EXP.iterdir()):
        for f in sorted((D / 'data').glob('*/renders.jsonl')) if (D / 'data').exists() else []:
            for line in f.read_text().split('\n'):
                if line.strip(): seen.add(json.loads(line).get('text', ''))
    return seen


def main():
    assert __import__('os').environ.get('SLURM_JOB_ID'), 'run via sbatch'
    lines = [l for f in SRC for l in pd.read_parquet(f)['text'].tolist()]
    arts = []; cur = None
    for l in lines:
        if re.match(r'^ = [^=].* = \n?$', l): cur = dict(title=l.strip(' =\n'), lines=[]); arts.append(cur)
        elif cur is not None: cur['lines'].append(l)
    rng = random.Random(3101); order = list(range(len(arts))); rng.shuffle(order); n = len(arts)
    pool = {}
    for r, i in enumerate(order): pool[i] = 'train' if r < .60 * n else 'dev' if r < .75 * n else 'confirm8'
    tb = AutoTokenizer.from_pretrained(str(REPO / 'models/bart-base'), local_files_only=True)
    tg = AutoTokenizer.from_pretrained('/dataset1/zailong/models/reference-frame-cross-backbone/t5gemma-2b-2b-ul2-it', local_files_only=True)
    single = {m: len(tb(' ' + m, add_special_tokens=False)['input_ids']) == 1 and len(tg(' ' + m, add_special_tokens=False)['input_ids']) == 1 for m in MONTHS}
    hist = history_texts(); seen = set(); out = []; cnt = Counter()
    for ai, a in enumerate(arts):
        for l in a['lines']:
            if not l.strip() or '=' in l: continue
            for s in re.split(r'(?<=[.!?])\s+(?=[A-Z"])', detok(l)):
                cnt['sentences'] += 1
                if '[' in s or ']' in s or not s.isascii(): cnt['non_ascii_or_bracket'] += 1; continue
                nw = len(s.split())
                if not 8 <= nw <= 35: cnt['length'] += 1; continue
                mt = match(s)
                if mt is None: continue
                cnt['month_pattern'] += 1
                if not all(single.values()): cnt['tokenizer'] += 1; continue
                if s in hist or s in seen: cnt['duplicate'] += 1; continue
                seen.add(s); out.append(dict(pool=pool[ai], article=ai, title=a['title'], text=s, **mt))
    (HERE / 'local').mkdir(exist_ok=True)
    with open(HERE / 'local/natural_candidates.jsonl', 'w') as f:
        for r in out: f.write(json.dumps(r) + '\n')
    summ = dict(source={str(p.relative_to(REPO)): sha(p) for p in SRC}, articles=n, pools={p: sum(1 for v in pool.values() if v == p) for p in ('train', 'dev', 'confirm8')},
                months_single_token=single, counts=dict(cnt), candidates={p: sum(1 for r in out if r['pool'] == p) for p in ('train', 'dev', 'confirm8')},
                forms=dict(Counter(r['form'] for r in out)), months=dict(Counter(r['month'] for r in out)),
                note='WikiText-103 train split only (the files available on the cluster); valid / test not used')
    (HERE / 'local/natural_candidates_summary.json').write_text(json.dumps(summ, indent=1)); print(json.dumps(summ), flush=True)


if __name__ == '__main__':
    main()
