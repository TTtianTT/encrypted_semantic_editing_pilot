"""v4 gold semantics: v3 semantics (v1 domains, scrambled maps, binding domains) plus three new cyclic domains
(hour Z12, compass8 Z8, season Z4; template 0, PLAN section 5.1). The evaluator does not import this module."""
import sys
from pathlib import Path

_V3 = Path(__file__).resolve().parents[1] / 'composability_mechanisms_v2'
if str(_V3) not in sys.path:
    sys.path.append(str(_V3))
import sym3_semantics as S3  # noqa: E402

S1 = S3.S1
NAMES, OBJECTS, COLORS, STATUSES = S3.NAMES, S3.OBJECTS, S3.COLORS, S3.STATUSES
V1_DOMAINS = S3.V1_DOMAINS
S1B = S3.S1B
FIX3, FIX3_SEED, FIXED, PRON = S3.FIX3, S3.FIX3_SEED, S3.FIXED, S3.PRON
# v2 locked sigma_max tables (composability_mechanisms_v1/protocol.json s1a.maps) as used in v3, plus egoside sigma_max from the same
# table (used only by the exploratory P4 per-plane criterion over v2/v3 operators); weekday skip2 from v3
MAPS = {**S3.MAPS, 'egoside': {'scrmax': [0, 1, 3, 2]}}
NEW_WORDS = {
    'hour': ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve'],
    'compass8': ['north', 'northeast', 'east', 'southeast', 'south', 'southwest', 'west', 'northwest'],
    'season': ['spring', 'summer', 'autumn', 'winter'],
}
NEW = list(NEW_WORDS)
CYCLIC_ALL = ['weekday', 'month', 'compass', 'egoside'] + NEW


def states(domain):
    if domain in NEW_WORDS:
        return list(range(len(NEW_WORDS[domain])))
    return S3.states(domain)


def advance(domain, current, operation, mapping='natural'):
    assert operation in ('plus', 'minus')
    if domain in NEW_WORDS:
        assert mapping == 'natural'
        return (current + (1 if operation == 'plus' else -1)) % len(NEW_WORDS[domain])
    if mapping == 'natural' or domain in S1B:
        return S3.advance(domain, current, operation, mapping)
    cyc = MAPS[domain][mapping]; i = cyc.index(current)
    return cyc[(i + (1 if operation == 'plus' else -1)) % len(cyc)]


def people(world):
    return S3.people(world)


def word(domain, current, world=None):
    if domain in NEW_WORDS:
        return NEW_WORDS[domain][current]
    return S3.word(domain, current, world)


def gold(world, current, template=0):
    d = world['domain']
    if d in NEW_WORDS:
        assert template == 0
        return dict(domain=d, state=current, value=word(d, current), people=world['people'], object=world['object'],
                    color=world['color'], quantity=world['quantity'], status=world['status'], structure=template)
    return S3.gold(world, current, template)


def render(world, current, template=0):
    d = world['domain']
    if d not in NEW_WORDS:
        return S3.render(world, current, template)
    assert template == 0
    a = world['people'][0]; o = world['object']; X = word(d, current); st = world['status']; fact = S1.fact(world)
    if d == 'hour':
        return f"The {o} event starts at {X} o'clock. Its status is {st}. {fact}"
    if d == 'season':
        return f'The {o} event is held in {X}. Its status is {st}. {fact}'
    return f"In {a}'s report, the {o} is on the {X} side. {fact}"
