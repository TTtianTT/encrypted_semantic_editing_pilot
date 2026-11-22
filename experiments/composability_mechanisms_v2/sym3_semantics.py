"""v3 gold semantics: v1 domains (unchanged), locked scrambled maps + weekday skip2, and the S1b' binding domains
(pron3, name3, bind3, bind3fix) whose primary template here is template 3. The evaluator does not import this module."""
import random
import sys
from pathlib import Path

_V1 = Path(__file__).resolve().parents[1] / 'symmetry_composability_v1'
if str(_V1) not in sys.path:
    sys.path.append(str(_V1))
import sym_semantics as S1  # noqa: E402

NAMES, OBJECTS, COLORS, STATUSES = S1.NAMES, S1.OBJECTS, S1.COLORS, S1.STATUSES
V1_DOMAINS = list(S1.DOMAINS)
S1B = ['pron3', 'name3', 'bind3', 'bind3fix']
PRON = ['me', 'you', 'them']
FIXED = ['Daniel', 'Sarah', 'Kevin']
FIX3_SEED = 2026112310
FIX3 = random.Random(FIX3_SEED).sample(NAMES, 3)          # bind3fix participant list, identical in every world
# v2 locked tables (composability_mechanisms_v1/protocol.json s1a.maps); skip2 is new (x -> x + 2 mod 7)
MAPS = {'weekday': {'scrmax': [0, 1, 6, 5, 2, 3, 4], 'skip2': [0, 2, 4, 6, 1, 3, 5]},
        'month': {'scrmax': [0, 5, 6, 8, 9, 2, 3, 1, 7, 4, 10, 11]},
        'compass': {'scrmax': [0, 3, 1, 2]}}


def states(domain):
    return [0, 1, 2] if domain in S1B else S1.states(domain)


def advance(domain, current, operation, mapping='natural'):
    assert operation in ('plus', 'minus')
    if domain in S1B:
        return (current + (1 if operation == 'plus' else -1)) % 3
    if mapping == 'natural':
        return S1.advance(domain, current, operation)
    cyc = MAPS[domain][mapping]; i = cyc.index(current)
    return cyc[(i + (1 if operation == 'plus' else -1)) % len(cyc)]


def people(world):
    return FIX3 if world['domain'] == 'bind3fix' else world['people']


def word(domain, current, world=None):
    if domain == 'pron3': return PRON[current]
    if domain == 'name3': return FIXED[current]
    if domain in ('bind3', 'bind3fix'): return people(world)[current]
    return S1.word(domain, current)


def gold(world, current, template=0):
    d = world['domain']
    if d in S1B:
        return dict(domain=d, state=current, value=word(d, current, world), people=people(world), object=world['object'],
                    color=world['color'], quantity=world['quantity'], status=world['status'], structure=template)
    return S1.gold(world, current, template)


def render(world, current, template=0):
    d = world['domain']
    if d not in S1B:
        return S1.render(world, current, template)
    p0, p1, p2 = people(world); o = world['object']; X = word(d, current, world)
    core = (f'Participants: {p0}, {p1}, {p2}. The {o} was sent to {X}.' if template == 0 else
            f'{p0}, {p1} and {p2} took part, and the {o} went to {X}.')
    return f'{core} {S1.fact(world)}'
