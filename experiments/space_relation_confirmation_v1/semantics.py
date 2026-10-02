"""Gold state operations and rendering; the evaluator does not import this module."""
from datetime import date, timedelta

NAMES = ['Alice', 'Bob', 'Carol', 'David', 'Emma', 'Frank', 'Grace', 'Henry']
OBJECTS = ['book', 'lamp', 'ticket', 'parcel', 'sensor', 'cup', 'box', 'key']
COLORS = ['blue', 'red', 'green', 'white', 'black']
RELATIVE = {-3:'three days ago', -2:'two days ago', -1:'yesterday', 0:'today', 1:'tomorrow', 2:'two days from now', 3:'three days from now'}
EVAL = ['strongly dislikes', 'dislikes', 'is neutral about', 'likes', 'strongly likes']
EVAL_OOD = ['detests', 'has a negative opinion of', 'has no preference about', 'has a positive opinion of', 'adores']
HEADINGS = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # north, east, south, west

def states(domain):
    return list(range(-3, 4)) if domain == 'time' else list(range(5)) if domain == 'emotion' else list(range(4 if domain == 'space' else 3))

def advance(domain, current, operation):
    assert operation in ('plus', 'minus')
    delta = 1 if operation == 'plus' else -1
    if domain == 'time':
        result = current - delta  # E-C, forward C lowers relative date
    elif domain == 'space':
        result = (current - delta) % 4  # CW facing rotation reduces relative bearing
    elif domain == 'emotion':
        result = current + delta
    else:
        result = (current + delta) % (4 if domain == 'space' else 3)
    if result not in states(domain):
        raise ValueError('Illegal boundary transition; no saturation')
    return result

def relation(world, heading):
    x, y = world['object_xy']
    ox, oy = world['observer_xy']
    dx, dy = x-ox, y-oy
    fx, fy = HEADINGS[heading]
    forward = dx*fx+dy*fy
    right = dx*fy-dy*fx
    assert (forward == 0) != (right == 0), 'core object lies on one cardinal ray'
    return ('front' if forward > 0 else 'back') if right == 0 else ('right' if right > 0 else 'left')

def reference(name, role, speaker, listener):
    if name == speaker:
        return dict(subject='I', object='me', owner='my', reflexive='myself')[role]
    if name == listener:
        return dict(subject='you', object='you', owner='your', reflexive='yourself')[role]
    # Proper names make third-person binding reversible, avoiding gender ambiguity.
    return name + "'s" if role == 'owner' else ('herself' if name in ('Alice','Carol','Emma','Grace') else 'himself') if role == 'reflexive' else name

def gold(world, current, template=0, symbolic=False):
    d = world['domain']; a,b,c = world['people']; obj=world['object']; color=world['color']
    out = dict(domain=d, state=current, people=world['people'], object=obj, color=color,quantity=world['quantity'],
               structure=template, symbolic=symbolic)
    if d == 'time':
        out.update(event_date=world['event_date'], anchor=(date.fromisoformat(world['event_date'])-timedelta(days=current)).isoformat(), status=world['status'], relative=current)
    if d == 'space':
        dx=world['object_xy'][0]-world['observer_xy'][0]
        dy=world['object_xy'][1]-world['observer_xy'][1]
        ray_heading=0 if dy>0 else 2 if dy<0 else 1 if dx>0 else 3
        heading=(ray_heading-current)%4
        bearing=['front','right','back','left'][current]
        assert relation(world,heading)==bearing
        out.update(relation=bearing, heading=heading, object_xy=world['object_xy'], observer_xy=world['observer_xy'],secondary_observer_xy=world['observer_xy'],marker_xy=[world['object_xy'][0],world['object_xy'][1]-1], fixed_heading=world['fixed_heading'], fixed_relation=relation(world,world['fixed_heading']))
    if d == 'emotion':
        out.update(target_evaluator=world['focus'], target_object=obj, target_level=current, other_level=world['other_level'], other_object=world['other_object'])
    if d == 'person':
        out.update(speaker=world['people'][current], listener=world['people'][(current+1)%3], agent=a, patient=b, owner=c, quote_speaker=b, quote_listener=c)
    return out

def render(world, current, template=0, symbolic=False):
    g = gold(world,current,template,symbolic);d=g['domain'];a,b,c=g['people'];o=g['object'];col=g['color']
    if symbolic:
        if d=='time': return f"event={g['event_date']}; anchor={g['anchor']}; relative={current}; status={g['status']}; object={o}; color={col}; copies={world['quantity']}."
        if d=='space': return f"observer={a}; heading={g['heading']}; relation={g['relation']}; object={o}; color={col}; fixed_observer={b}; fixed_relation={g['fixed_relation']}; observer_x={world['observer_xy'][0]}; observer_y={world['observer_xy'][1]}; object_x={world['object_xy'][0]}; object_y={world['object_xy'][1]}; copies={world['quantity']}."
        if d=='emotion': return f"focus={world['focus']}; object={o}; level={current}; other={b if world['focus']==a else a}; other_level={g['other_level']}; color={col}; copies={world['quantity']}."
        return f"speaker={g['speaker']}; listener={g['listener']}; agent={a}; patient={b}; owner={c}; object={o}; color={col}; copies={world['quantity']}."
    fact=f"The {o} is {col}. "+('There is 1 copy.' if world['quantity']==1 else f"There are {world['quantity']} copies.")
    if d=='time':
        r=RELATIVE[current]
        if template==2: r={-1:'one day before this anchor',0:'on this day',1:'one day after this anchor'}.get(current,r.replace('from now','after this anchor').replace('ago','before this anchor'))
        core=f"The {o} event is dated {r}." if template!=1 else f"The date of the {o} event is {r}."
        status=f"Its status is {world['status']}."
        extras=''
        if template>=3: extras+=f" Its absolute date is {g['event_date']}."
        if template==4: extras+=" It is two days after the fixed launch."
        if template==5: extras+=f' On {world["quote_date"]}, {b} said to {c}, "The event is tomorrow."'
        return f"{core} {status} {fact}{extras}"
    if d=='space':
        r=g['relation']; words={'front':'in front of me','right':'to my right','back':'behind me','left':'to my left'}
        if template==1: core=f"From {a}'s viewpoint, the {o} is on the {r} side."
        elif template==2: core=f"Observer: {a}. I see the {o} {'ahead' if r=='front' else 'behind' if r=='back' else 'on my '+r}."
        else: core=f"Observer: {a}. The {o} is {words[r]}."
        extras=''
        if template>=3:
            x,y=world['object_xy'];ox,oy=world['observer_xy'];direction='east' if x>ox else 'west' if x<ox else 'north' if y>oy else 'south'
            extras+=f" Its world direction is {direction}."
        if template==4: extras+=f" From {b}'s viewpoint, it is on the {g['fixed_relation']} side."
        if template==5: extras+=f" The {o} is north of the marker."
        return f"{core} {fact}{extras}"
    if d=='emotion':
        focus=world['focus'];other=b if focus==a else a
        terms=EVAL_OOD if template==2 else EVAL
        target=f"{focus} {terms[current]} the {o}.";non=f"{other} {terms[world['other_level']]} the {o}."
        if template==1: target=f"As for the {o}, {focus} {terms[current]} it.";non=f"As for the {o}, {other} {terms[world['other_level']]} it."
        if template==3:
            negative='does not like' if current<2 else 'neither likes nor dislikes' if current==2 else 'does not dislike'
            # Negation alone would not distinguish neutral from positive.
            # Explicit stance supplies an unambiguous answer at every level.
            target=f"{focus} {negative} the {o}; {focus} {EVAL[current]} the {o}."
        extras=''
        if template==4: extras+=f" {focus} dislikes the {world['other_object']}."
        if template==5: extras+=f' {c} said, "I dislike the {o}."'
        return f"Focus: {focus}'s view of the {o}. {target} {non} {fact}{extras}"
    s,l=g['speaker'],g['listener'];r=lambda n,k:reference(n,k,s,l)
    agent=r(a,'subject');verb='give' if agent in ('I','you') else 'gives'
    transfer=f"{agent} {verb} {r(b,'object')} {r(c,'owner')} {o}."
    if template==1: transfer=f"{r(c,'owner').capitalize()} {o} is what {agent} {verb} {r(b,'object')}."
    if template==2:
        receiver=r(b,'subject'); rv='receive' if receiver in ('I','you') else 'receives'
        transfer=f"{receiver.capitalize()} {rv} {r(c,'owner')} {o} from {r(a,'object')}."
    extras=''
    if template==3:
        own=r(a,'owner');ref=r(a,'reflexive');extras=f" {agent} {'keep' if agent in ('I','you') else 'keeps'} {own} key for {ref}."
    if template==4: extras=f' {b} said to {c}, "I give you my key."'
    if template==5: extras=f" {c} sees {a} and {b}."
    if template==6:
        third=c if current==0 else a if current==1 else b
        female=third in ('Alice','Carol','Emma','Grace')
        if current==0:
            binder=f'The owner is {c}.';transfer=f"I give you {'her' if female else 'his'} {o}."
        elif current==1:
            binder=f'The giver is {a}.';transfer=f"{'She' if female else 'He'} gives me your {o}."
        else:
            binder=f'The recipient is {b}.';transfer=f"You give {'her' if female else 'him'} my {o}."
        transfer=binder+' '+transfer
    return f"Speaker: {s}. Listener: {l}. {transfer} {fact}{extras}"
