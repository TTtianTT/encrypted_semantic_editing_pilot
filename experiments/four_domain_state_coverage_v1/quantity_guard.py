"""Independent consistency of every unquoted exact copy-count claim."""
import re

def consistent_quantity(text,g):
    outer=re.sub(r'\s+',' ',re.sub(r'"[^"]*"','',text))
    values=[int(m) for m in re.findall(r'\bthere (?:are|is) (\d+) cop(?:y|ies)\.',outer,re.I)]
    return all(n==g['quantity'] for n in values) if values else None
