"""CPU evaluation helpers with explicit missingness and valid-token rules."""
import math

def effective_ids(ids,eos):
    out=[]
    for token in ids[1:]:
        out.append(token)
        if token in eos:return out,True
    return out,False

def proportion(n,d):return None if d==0 else n/d

def joint(s):return bool(s['target'] and s['preserved'] and s['parseable'] and s['grammar'] and s['ended'])

def wilson(n,d,z=1.959963984540054):
    if not d:return None
    p=n/d;den=1+z*z/d;c=(p+z*z/(2*d))/den;rad=z*math.sqrt(p*(1-p)/d+z*z/(4*d*d))/den
    return [max(0,c-rad),min(1,c+rad)]

def masked_squared_norm(values,mask):
    return sum(sum(v*v for v in row) for row,valid in zip(values,mask) if valid)
