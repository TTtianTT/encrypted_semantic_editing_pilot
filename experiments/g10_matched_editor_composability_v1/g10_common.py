import csv,hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
V1=ROOT.parent/'reference_frame_pilot_v1'
V2=ROOT.parent/'reference_frame_pilot_v2'
V3=ROOT.parent/'reference_frame_pilot_v3'
G7=ROOT.parent/'repeated_intervention_stability_v1'
G8=ROOT.parent/'decoder_basin_anisotropy_v1'
G9=ROOT.parent/'semantically_matched_editors_v1'

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):
 p=Path(path);p=p if p.is_absolute() else ROOT/p
 return [json.loads(x) for x in p.read_text().splitlines() if x]
def dump(path,obj):
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.tmp');q.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n');q.replace(p)
def write(path,rows):
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
def csvwrite(path,rows):
 if not rows:return
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
