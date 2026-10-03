"""Fixed-world P continuation cases for each actually evaluated structure."""
from common import *

def main():
    cases=[]
    for task in read(ROOT/'linguistic_tasks.json'):
        base=ROOT.parent/task['study'];dest=base/'language_controls'/f"{task['model']}_{task['domain']}"
        for path in sorted(dest.glob('s*/P/trajectory_t*.jsonl')):
            rr=rows(path);world=min(r['world_id'] for r in rr)
            for trajectory in ('forward','reverse','inverse'):
                selected=[r for r in rr if r['world_id']==world and r['trajectory']==trajectory and r['step'] in (1,2)]
                assert len(selected)==6
                cases.append(dict(study=task['study'],model=task['model'],domain=task['domain'],seed=int(path.parent.parent.name[1:]),condition='P',template=rr[0]['template'],world_id=world,trajectory=trajectory,predictions=selected,source_file=str(path.relative_to(base)),source_sha256=digest(path),selection='first test world, all three trajectories and both first steps, all evaluated P structures; no success filter'))
    jsonl(ROOT/'LANGUAGE_FIXED_CONTINUATION_CASES.jsonl',cases)
    dump(ROOT/'LANGUAGE_FIXED_CONTINUATION_SELECTION.json',dict(cases=len(cases),selection_is_posthoc_but_outcome_independent=True,independent_worlds_per_domain=1,not_independent_human_labels=True))
    print('Language fixed continuation cases:',len(cases))

if __name__=='__main__':main()
