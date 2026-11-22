"""Independent finite-grammar parser for the E1 domains. Does not import sym_semantics.

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


def _pattern(domain, structure):
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
        if d in ('weekday', 'month', 'daysago'):
            preserved &= p['status'] == gold['status']
        if d in ('compass', 'egoside') or s == 3:
            preserved &= p['a'] == a
        if s == 3:
            preserved &= p['b'] == b
    scope = target and preserved
    return dict(success=bool(ended and grammar and scope), target=bool(target), preserved=bool(preserved), scope=bool(scope),
                parseable=p is not None, grammar=bool(grammar), ended=bool(ended))
