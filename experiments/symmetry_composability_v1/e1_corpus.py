"""E1.1 corpus symmetry (CPU): PPMI context vectors of each domain's attribute words in wikitext-103 train,
group-averaged R^2 of the cosine-distance matrix, label-permutation null, and a variant without member-member counts."""
import re
import time
from collections import Counter, defaultdict
import pyarrow.parquet as pq
from symutil import *
import sym_semantics as S

WINDOW = 5
VOCAB = 50000
MIN_PHRASE = 200
DL = ROOT / 'local/corpus_download'
TOKEN = re.compile(r'[A-Za-z]+')
NUMW = [S.NUMBERS[k] for k in range(2, 10)]


def targets():
    t = {d: list(S.WORDS[d]) for d in ('weekday', 'month', 'compass', 'egoside')}  # case-sensitive surface forms
    return t


def main():
    require_slurm(); t0 = time.time()
    files = sorted(DL.glob('train-*.parquet')); assert len(files) == 2, files
    T = targets(); member = {w: d for d, ws in T.items() for w in ws}
    num_member = set(NUMW)
    uni = Counter(); co = defaultdict(Counter); co_mem = defaultdict(Counter); occ = Counter()
    phrase = defaultdict(Counter); phrase_mem = defaultdict(Counter); pocc = Counter()   # daysago phrases
    numw = defaultdict(Counter); numw_mem = defaultdict(Counter); nocc = Counter()         # fallback number words
    lines = 0; tokens = 0
    for f in files:
        for batch in pq.ParquetFile(f).iter_batches(columns=['text'], batch_size=20000):
            for text in batch.column(0).to_pylist():
                toks = TOKEN.findall(text)
                if not toks:
                    continue
                low = [x.lower() for x in toks]; uni.update(low); lines += 1; tokens += len(toks); L = len(toks)
                for i, w in enumerate(toks):
                    d = member.get(w)
                    if d is not None:
                        occ[w] += 1
                        for j in range(max(0, i - WINDOW), min(L, i + WINDOW + 1)):
                            if j == i: continue
                            co[w][low[j]] += 1
                            if member.get(toks[j]) == d: co_mem[w][low[j]] += 1
                    lw = low[i]
                    if lw in num_member:
                        nocc[lw] += 1
                        for j in range(max(0, i - WINDOW), min(L, i + WINDOW + 1)):
                            if j == i: continue
                            numw[lw][low[j]] += 1
                            if low[j] in num_member: numw_mem[lw][low[j]] += 1
                        if i + 2 < L and low[i + 1] == 'days' and low[i + 2] == 'ago':
                            pocc[lw] += 1
                            for j in list(range(max(0, i - WINDOW), i)) + list(range(i + 3, min(L, i + 3 + WINDOW))):
                                phrase[lw][low[j]] += 1
                                if low[j] in num_member: phrase_mem[lw][low[j]] += 1
    vocab = [w for w, _ in uni.most_common(VOCAB)]; vix = {w: i for i, w in enumerate(vocab)}
    pc = np.array([uni[w] for w in vocab], float) ** .75; pc /= pc.sum()

    def ppmi(counter):
        v = np.zeros(len(vocab))
        for c, k in counter.items():
            if c in vix: v[vix[c]] = k
        if v.sum() == 0: return v
        return np.maximum(0, np.log(np.maximum(v / v.sum(), 1e-300) / pc)) * (v > 0)

    def analyze(words, counts, mem, kind, name, drop=None):
        idx = [i for i in range(len(words)) if drop is None or words[i] != drop]
        out = {}
        for variant in ('all', 'no_member_contexts'):
            M = np.stack([ppmi(counts[words[i]] - (mem[words[i]] if variant != 'all' else Counter())) for i in idx])
            U = M / np.maximum(np.linalg.norm(M, axis=1, keepdims=True), 1e-12)
            D = 2 * (1 - U @ U.T)   # squared distance between unit PPMI vectors
            base = orbit_key(kind, len(words)); key = lambda a, b: base(idx[a], idx[b])
            r2 = group_r2(D, key); nr = [group_r2(D[np.ix_(p, p)], key) for p in permutations_for(len(idx))]
            out[variant] = dict(R2_G=r2, null=quantile_of(r2, nr), above_null_q95=bool(r2 > np.quantile(nr, .95)), distance=D.tolist())
        return dict(name=name, words=[words[i] for i in idx], kind=kind, **out)

    res = dict(corpus='wikitext-103-raw-v1 train', files={f.name: sha(f) for f in files}, lines=lines, tokens=tokens, window=WINDOW,
               context_vocab=VOCAB, smoothing=0.75, distance='2(1-cos) of PPMI vectors',
               casing='weekday/month capitalized surface forms; compass/egoside lowercase surface forms (case-sensitive match)',
               domains={})
    for d in ('weekday', 'month', 'compass', 'egoside'):
        kind = 'cyclic'; ws = T[d]
        res['domains'][d] = dict(occurrences={w: occ[w] for w in ws}, **analyze(ws, co, co_mem, kind, d))
    res['domains']['month_without_May'] = dict(**analyze(T['month'], co, co_mem, 'cyclic', 'month_without_May', drop='May'))
    counts = {w: pocc[w] for w in NUMW}
    use_phrase = min(counts.values()) >= MIN_PHRASE
    src, mem = (phrase, phrase_mem) if use_phrase else (numw, numw_mem)
    res['domains']['daysago'] = dict(phrase_occurrences=counts, number_word_occurrences={w: nocc[w] for w in NUMW},
                                     unit='phrase "<n> days ago"' if use_phrase else f'number words two..nine (a phrase had < {MIN_PHRASE} occurrences)',
                                     **analyze(NUMW, src, mem, 'open', 'daysago'))
    res['seconds'] = time.time() - t0
    dump('results/e1_corpus.json', res)
    for k, v in res['domains'].items():
        print(k, {x: round(v[x]['R2_G'], 3) for x in ('all', 'no_member_contexts')}, {x: round(v[x]['null']['frac_le'], 3) for x in ('all', 'no_member_contexts')}, flush=True)


if __name__ == '__main__':
    main()
