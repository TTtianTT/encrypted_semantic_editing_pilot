"""v2 gold semantics. Imports v1 sym_semantics (unchanged) and adds:
- scrambled-map variants of the v1 domains (render identical; plus/minus follow a locked permutation table);
- the S1b binding-control domains pron3, name3, bind3.
The evaluator (sym2_evaluator.py) does not import this module."""
import json
import sys
from pathlib import Path

_V1 = Path(__file__).resolve().parents[1] / 'symmetry_composability_v1'
if str(_V1) not in sys.path:
    sys.path.append(str(_V1))
import sym_semantics as S1  # noqa: E402

NAMES, OBJECTS, COLORS, STATUSES = S1.NAMES, S1.OBJECTS, S1.COLORS, S1.STATUSES
V1_DOMAINS = list(S1.DOMAINS)
S1B_DOMAINS = ['pron3', 'name3', 'bind3']
PRON = ['me', 'you', 'them']
FIXED = ['Daniel', 'Sarah', 'Kevin']
assert not set(FIXED) & set(NAMES)
MAPS = {}   # {domain: {'scrmax': {...}, 'scrmed': {...}}}; filled by load_maps() from the locked protocol


def load_maps(source):
    """source: path to protocol.json (after lock) or results/s1a_selection.json (selection stage)."""
    MAPS.clear(); MAPS.update(json.loads(Path(source).read_text())['s1a']['maps'] if 'protocol' in str(source)
                              else json.loads(Path(source).read_text())['maps'])


def states(domain):
    return [0, 1, 2] if domain in S1B_DOMAINS else S1.states(domain)


def advance(domain, current, operation, mapping='natural'):
    assert operation in ('plus', 'minus')
    if domain in S1B_DOMAINS:
        return (current + (1 if operation == 'plus' else -1)) % 3
    if mapping == 'natural':
        return S1.advance(domain, current, operation)
    m = MAPS[domain][mapping]
    if domain == 'daysago':  # open path: plus = successor on the path, minus = predecessor
        path = m['path']; i = path.index(current) + (1 if operation == 'plus' else -1)
        if not 0 <= i < len(path):
            raise ValueError('Illegal boundary transition; no saturation')
        return path[i]
    cyc = m['cycle']; i = cyc.index(current)
    return cyc[(i + (1 if operation == 'plus' else -1)) % len(cyc)]


def path_order(domain, mapping='natural'):
    """daysago: state order along the path for a mapping."""
    return list(range(2, 10)) if mapping == 'natural' else list(MAPS[domain][mapping]['path'])


def word(domain, current, world=None):
    if domain == 'pron3': return PRON[current]
    if domain == 'name3': return FIXED[current]
    if domain == 'bind3': return world['people'][current]
    return S1.word(domain, current)


def gold(world, current, template=0):
    d = world['domain']
    if d in S1B_DOMAINS:
        return dict(domain=d, state=current, value=word(d, current, world), people=world['people'], object=world['object'],
                    color=world['color'], quantity=world['quantity'], status=world['status'], structure=template)
    return S1.gold(world, current, template)


def render(world, current, template=0):
    d = world['domain']
    if d not in S1B_DOMAINS:
        return S1.render(world, current, template)
    p0, p1, p2 = world['people']; o = world['object']; X = word(d, current, world)
    core = (f'Participants: {p0}, {p1}, {p2}. The {o} was sent to {X}.' if template == 0 else
            f'{p0}, {p1} and {p2} took part, and the {o} went to {X}.')
    return f'{core} {S1.fact(world)}'
