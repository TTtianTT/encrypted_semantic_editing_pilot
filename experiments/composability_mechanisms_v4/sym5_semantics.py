"""v5 gold semantics: v4 semantics (v1 domains, scrambled maps, binding domains, hour / compass8 / season) plus the multi-template
domains weekday-mt, month-mt, hour-mt (PLAN 5.2, appendix B): a world carries template_id (assigned after the GR/GT gates) and a fixed
same-domain distractor state; the gold output is the rendered sentence itself. The evaluator does not import this module."""
import json
import sys
from functools import lru_cache
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_V3 = _HERE.parents[0] / 'composability_mechanisms_v2'
if str(_V3) not in sys.path:
    sys.path.append(str(_V3))
import sym3_semantics as S3  # noqa: E402

S1 = S3.S1
NAMES, OBJECTS, COLORS, STATUSES = S3.NAMES, S3.OBJECTS, S3.COLORS, S3.STATUSES
V1_DOMAINS = S3.V1_DOMAINS
S1B = S3.S1B
FIX3, FIX3_SEED, FIXED, PRON = S3.FIX3, S3.FIX3_SEED, S3.FIXED, S3.PRON
MAPS = {**S3.MAPS, 'egoside': {'scrmax': [0, 1, 3, 2]}}
NEW_WORDS = {
    'hour': ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve'],
    'compass8': ['north', 'northeast', 'east', 'southeast', 'south', 'southwest', 'west', 'northwest'],
    'season': ['spring', 'summer', 'autumn', 'winter'],
}
NEW = list(NEW_WORDS)
MT = ['weekday-mt', 'month-mt', 'hour-mt']
CYCLIC_ALL = ['weekday', 'month', 'compass', 'egoside'] + NEW
TEMPLATES_MT = _HERE / 'data/templates_mt.json'


def base(domain):
    return domain[:-3] if domain in MT else domain


@lru_cache(None)
def mt_templates():
    return json.loads(TEMPLATES_MT.read_text())['templates']


def states(domain):
    d = base(domain)
    if d in NEW_WORDS:
        return list(range(len(NEW_WORDS[d])))
    return S3.states(d)


def advance(domain, current, operation, mapping='natural'):
    assert operation in ('plus', 'minus')
    d = base(domain)
    if d in NEW_WORDS:
        assert mapping == 'natural'
        return (current + (1 if operation == 'plus' else -1)) % len(NEW_WORDS[d])
    if domain in MT: assert mapping == 'natural'
    if mapping == 'natural' or d in S1B:
        return S3.advance(d, current, operation, mapping)
    cyc = MAPS[d][mapping]; i = cyc.index(current)
    return cyc[(i + (1 if operation == 'plus' else -1)) % len(cyc)]


def people(world):
    return S3.people(world)


def word(domain, current, world=None):
    d = base(domain)
    if d in NEW_WORDS:
        return NEW_WORDS[d][current]
    return S3.word(d, current, world)


def mt_fields(world, current):
    d = world['domain']
    return dict(X=word(d, current), Y=word(d, world['distractor']), a=world['people'][0], o=world['object'], st=world['status'],
                color=world['color'], q=str(world['quantity']))


def render_mt(world, current, template_id):
    return mt_templates()[world['domain']][template_id]['text'].format(**mt_fields(world, current))


def gold(world, current, template=0):
    d = world['domain']
    if d in MT:
        tid = world['template_id']
        return dict(domain=d, state=current, template_id=tid, text=render_mt(world, current, tid), fields=mt_fields(world, current), structure='mt')
    if d in NEW_WORDS:
        assert template == 0
        return dict(domain=d, state=current, value=word(d, current), people=world['people'], object=world['object'],
                    color=world['color'], quantity=world['quantity'], status=world['status'], structure=template)
    return S3.gold(world, current, template)


def render(world, current, template=0):
    d = world['domain']
    if d in MT:
        return render_mt(world, current, world['template_id'])
    if d not in NEW_WORDS:
        return S3.render(world, current, template)
    assert template == 0
    a = world['people'][0]; o = world['object']; X = word(d, current); st = world['status']; fact = S1.fact(world)
    if d == 'hour':
        return f"The {o} event starts at {X} o'clock. Its status is {st}. {fact}"
    if d == 'season':
        return f'The {o} event is held in {X}. Its status is {st}. {fact}'
    return f"In {a}'s report, the {o} is on the {X} side. {fact}"
