"""E1 gold state operations and rendering. The evaluator (sym_evaluator.py) does not import this module."""

NAMES = ['Alice', 'Bob', 'Carol', 'David', 'Emma', 'Frank', 'Grace', 'Henry']
OBJECTS = ['book', 'lamp', 'ticket', 'parcel', 'sensor', 'cup', 'box', 'key']
COLORS = ['blue', 'red', 'green', 'white', 'black']
STATUSES = ['planned', 'completed', 'cancelled']
DOMAINS = ['weekday', 'month', 'compass', 'egoside', 'daysago']

WORDS = {
    'weekday': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
    'month': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
    'compass': ['north', 'east', 'south', 'west'],       # plus = clockwise 90 degrees
    'egoside': ['front', 'right', 'back', 'left'],       # plus = front -> right -> back -> left -> front
}
NUMBERS = {2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine'}
CYCLIC = {'weekday': 7, 'month': 12, 'compass': 4, 'egoside': 4}
GROUP = {'weekday': 'Z7', 'month': 'Z12', 'compass': 'Z4', 'egoside': 'Z4', 'daysago': 'open8'}


def states(domain):
    return list(range(2, 10)) if domain == 'daysago' else list(range(CYCLIC[domain]))


def advance(domain, current, operation):
    assert operation in ('plus', 'minus')
    delta = 1 if operation == 'plus' else -1
    if domain == 'daysago':
        result = current + delta  # plus = one more day ago; nine is the boundary
        if result not in states(domain):
            raise ValueError('Illegal boundary transition; no saturation')
        return result
    return (current + delta) % CYCLIC[domain]


def word(domain, current):
    return f'{NUMBERS[current]} days ago' if domain == 'daysago' else WORDS[domain][current]


def gold(world, current, template=0):
    d = world['domain']
    return dict(domain=d, state=current, value=word(d, current), people=world['people'], object=world['object'],
                color=world['color'], quantity=world['quantity'], status=world['status'], structure=template)


def fact(world):
    o, col, q = world['object'], world['color'], world['quantity']
    return f'The {o} is {col}. ' + ('There is 1 copy.' if q == 1 else f'There are {q} copies.')


def render(world, current, template=0):
    d = world['domain']; a, b, _ = world['people']; o = world['object']; X = word(d, current); st = world['status']
    if d in ('weekday', 'month'):
        core = f'The {o} event is scheduled for {X}.' if template == 0 else f'{a} noted that the {o} event is scheduled for {X}, and {b} agreed.'
        return f'{core} Its status is {st}. {fact(world)}'
    if d == 'daysago':
        core = f'The {o} event is dated {X}.' if template == 0 else f'{a} noted that the {o} event is dated {X}, and {b} agreed.'
        return f'{core} Its status is {st}. {fact(world)}'
    core = f"In {a}'s report, the {o} is on the {X} side." if template == 0 else f"According to {a}'s report, which {b} checked, the {o} lies on the {X} side."
    return f'{core} {fact(world)}'
