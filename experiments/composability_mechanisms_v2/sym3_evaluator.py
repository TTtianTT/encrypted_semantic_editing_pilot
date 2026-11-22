"""Independent finite-grammar parser for the v1 domains and the S1b binding domains. Imports no semantics module.

The whole output must be consumed by one template regex (grammar); unknown attribute words are unresolved.
Returned fields match four-domain evaluator.score: success, target, preserved, scope, parseable, grammar, ended.
"""
import re

_VOCAB = {
    'weekday': 'monday tuesday wednesday thursday friday saturday sunday'.split(),
    'month': 'january february march april may june july august september october november december'.split(),
    'compass': 'north east south west'.split(),
    'egoside': 'front right back left'.split(),
}
_DAYS = {'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9}
_FACT = r' the (?P<obj2>[a-z]+) is (?P<color>blue|red|green|white|black)\. there (?:are (?P<qn>[2-9]) copies|is (?P<q1>1) copy)\.'
_STATUS = r' its status is (?P<status>planned|completed|cancelled)\.'


def normalize(text):
    return re.sub(r'\s+', ' ', text.strip().replace('’', "'")).lower()


_PRON = ['me', 'you', 'them']
_FIXED = ['daniel', 'sarah', 'kevin']
_S1B = ('pron3', 'name3', 'bind3', 'bind3fix')


def _pattern(domain, structure):
    if domain in _S1B:
        core = (r'participants: (?P<p0>[a-z]+), (?P<p1>[a-z]+), (?P<p2>[a-z]+)\. the (?P<obj>[a-z]+) was sent to (?P<x>[a-z]+)\.' if structure == 0 else
                r'(?P<p0>[a-z]+), (?P<p1>[a-z]+) and (?P<p2>[a-z]+) took part, and the (?P<obj>[a-z]+) went to (?P<x>[a-z]+)\.')
        return core + _FACT
    if domain in ('weekday', 'month'):
        core = (r'the (?P<obj>[a-z]+) event is scheduled for (?P<x>[a-z]+)\.' if structure == 0 else
                r'(?P<a>[a-z]+) noted that the (?P<obj>[a-z]+) event is scheduled for (?P<x>[a-z]+), and (?P<b>[a-z]+) agreed\.')
        return core + _STATUS + _FACT
    if domain == 'daysago':
        core = (r'the (?P<obj>[a-z]+) event is dated (?P<x>[a-z]+) days ago\.' if structure == 0 else
                r'(?P<a>[a-z]+) noted that the (?P<obj>[a-z]+) event is dated (?P<x>[a-z]+) days ago, and (?P<b>[a-z]+) agreed\.')
        return core + _STATUS + _FACT
    core = (r"in (?P<a>[a-z]+)'s report, the (?P<obj>[a-z]+) is on the (?P<x>[a-z]+) side\." if structure == 0 else
            r"according to (?P<a>[a-z]+)'s report, which (?P<b>[a-z]+) checked, the (?P<obj>[a-z]+) lies on the (?P<x>[a-z]+) side\.")
    return core + _FACT


def parse(text, domain, structure):
    t = normalize(text)
    m = re.fullmatch(_pattern(domain, structure), t)
    if not m:
        return None, False
    g = m.groupdict()
    if domain in _S1B:
        parts = [g['p0'], g['p1'], g['p2']]
        vocab = _PRON if domain == 'pron3' else _FIXED if domain == 'name3' else parts
        value = vocab.index(g['x']) if g['x'] in vocab else None
        p = dict(value=value, word=g['x'], participants=parts, object=g['obj'], fact_object=g['obj2'], color=g['color'],
                 quantity=int(g['qn'] or g['q1']), status=None, a=None, b=None)
        return p, value is not None
    if domain == 'daysago':
        value = _DAYS.get(g['x'])
    else:
        value = _VOCAB[domain].index(g['x']) if g['x'] in _VOCAB[domain] else None
    p = dict(value=value, object=g['obj'], fact_object=g['obj2'], color=g['color'], quantity=int(g['qn'] or g['q1']),
             status=g.get('status'), a=g.get('a'), b=g.get('b'))
    return p, value is not None


def score(text, gold, world, ended=True):
    d = gold['domain']; s = gold['structure']
    p, grammar = parse(text, d, s)
    target = preserved = False
    if p is not None:
        a, b = gold['people'][0].lower(), gold['people'][1].lower()
        target = p['value'] == gold['state']
        preserved = (p['object'] == gold['object'] and p['fact_object'] == gold['object'] and p['color'] == gold['color']
                     and p['quantity'] == gold['quantity'])
        if d in _S1B:
            preserved &= p['participants'] == [x.lower() for x in gold['people']]
            if d in ('bind3', 'bind3fix'):
                target = p['word'] == gold['people'][gold['state']].lower()
        elif d in ('weekday', 'month', 'daysago'):
            preserved &= p['status'] == gold['status']
        if d in ('compass', 'egoside') or (s == 3 and d not in _S1B):
            preserved &= p['a'] == a
        if s == 3 and d not in _S1B:
            preserved &= p['b'] == b
    scope = target and preserved
    return dict(success=bool(ended and grammar and scope), target=bool(target), preserved=bool(preserved), scope=bool(scope),
                parseable=p is not None, grammar=bool(grammar), ended=bool(ended))


# ---------------------------------------------------------------- A.8 decoded-state parser (v3)
_NAMES = ['alice', 'bob', 'carol', 'david', 'emma', 'frank', 'grace', 'henry']
_SLOT = {'weekday': r'scheduled for ([a-z]+)', 'month': r'scheduled for ([a-z]+)', 'daysago': r'dated ([a-z]+) days ago',
         'compass': r'on the ([a-z]+) side', 'egoside': r'on the ([a-z]+) side'}


def parse_state(text, domain, people=None):
    """Find the domain's state words in the attribute phrase; exactly one -> its state index, else None.
    Returns (state, word); for bind3/bind3fix the word is reported even when it is not in the participant list."""
    t = normalize(text); first = t.split('. ')[0]
    if domain in _S1B:
        m = re.search(r'(?:went|was sent) to ([a-z]+)', first); w = m[1] if m else None
        vocab = _PRON if domain == 'pron3' else _FIXED if domain == 'name3' else [p.lower() for p in people]
    else:
        m = re.search(_SLOT[domain], first); w = m[1] if m else None
        vocab = list(_DAYS) if domain == 'daysago' else _VOCAB[domain]
    if w is None:  # fall back: exactly one state word anywhere in the first sentence
        hits = [v for v in vocab if re.search(r'\b' + v + r'\b', first)]
        if len(hits) != 1: return None, None
        w = hits[0]
    if w not in vocab: return None, w
    return (_DAYS[w] if domain == 'daysago' else vocab.index(w)), w
