"""CPU state-flow/selector/statistic tests; never initialize CUDA on login."""
import copy,tempfile,unittest
from unittest.mock import patch
import torch
from common_g16 import *
import selection
runtime=load_module('g16_CPU_test_runtime',ROOT/'run.py')
stats=load_module('g16_CPU_readonly_g15_statistics',G15/'analyze.py')

def candidate(step=25):
    cells=[dict(status=s,offset=d,perspective=p,k=128,n=128) for s in ['recorded_plan','reported_cancelled','reported_completed'] for d in range(-3,5) for p in ['first','third'] if s!='reported_completed' or d<=0]
    return dict(seed=42,step=step,split='dev',method='F',atomic_cells=cells,old_k=128,old_n=128,A_k=128,A_n=128,D_k=128,D_n=128)

class Tests(unittest.TestCase):
    def test_earliest_no_step0_no_fallback(self):
        cs=[candidate(100),candidate(50),candidate(25)];self.assertEqual(selection.decision(cs)['step'],25)
        self.assertIsNone(selection.decision([candidate(0)]));bad=candidate();bad['D_k']=0;self.assertIsNone(selection.decision([bad]))
    def test_every_threshold_missing_and_forbidden(self):
        c=candidate();c['atomic_cells'][0]['k']=115;self.assertFalse(selection.qualify(c)['qualified'])
        for name in ['old_k','old_n','A_k','A_n','D_k','D_n','atomic_cells']:
            c=candidate();del c[name];self.assertFalse(selection.qualify(c)['qualified'])
        for name in ['U_rate','G_today_next','confirm_joint','self_second']:
            c=candidate();c[name]=1;self.assertFalse(selection.qualify(c)['qualified'])
        for name in ['old','D']:
            c=candidate();c[name+'_n']=63;c[name+'_k']=63;self.assertFalse(selection.qualify(c)['qualified'])
        c=candidate();c['atomic_cells']=None;self.assertFalse(selection.qualify(c)['qualified'])
    def test_selection_write_once(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'selection.json';selection.write_once(p,{'step':25});sha=digest(p);selection.write_once(p,{'step':25})
            with self.assertRaises(AssertionError):selection.write_once(p,{'step':50})
            self.assertEqual(digest(p),sha)
    def test_U_global_barrier_precedes_loader(self):
        with tempfile.TemporaryDirectory() as d,patch.object(selection,'ROOT',Path(d)),patch.object(runtime,'_original_loader',side_effect=AssertionError('must not reach fake U path')) as loader:
            with self.assertRaisesRegex(AssertionError,'forbidden'):runtime.load_editor(42,'U',final_heldout=True)
            self.assertFalse(loader.called)
        with self.assertRaises(AssertionError):runtime.load_editor(42,'G',train=True)
    def test_rng_monitor_and_optimizer_update(self):
        torch.manual_seed(42);random.seed(42);a=torch.nn.Linear(3,2);b=copy.deepcopy(a);oa=torch.optim.AdamW(a.parameters(),lr=.001,weight_decay=0);ob=torch.optim.AdamW(b.parameters(),lr=.001,weight_decay=0)
        py=random.getstate();ts=torch.get_rng_state().clone()
        with runtime.preserve_rng():random.random();torch.rand(100)
        self.assertEqual(random.getstate(),py);self.assertTrue(torch.equal(torch.get_rng_state(),ts))
        x=torch.randn(8,3);a(x).square().mean().backward();oa.step()
        random.setstate(py);torch.set_rng_state(ts);y=torch.randn(8,3);self.assertTrue(torch.equal(x,y));b(y).square().mean().backward();ob.step()
        self.assertEqual(statehash(a.state_dict()),statehash(b.state_dict()))
    def test_fixed_memory_frozen_and_differentiable(self):
        torch.manual_seed(42);P=runtime.Editor();T=copy.deepcopy(P);G=copy.deepcopy(P)
        for m in [P,G]:
            for p in m.parameters():p.requires_grad_(False)
        x=torch.randn(8,96,768);mask=torch.ones(8,96,dtype=torch.long);mask[:,60:]=0
        with torch.no_grad():fixed=P(x,mask)
        sha=statehash({'memory':fixed,'mask':mask});decoder=torch.nn.Linear(768,4)
        for p in decoder.parameters():p.requires_grad_(False)
        loss=decoder(T(fixed,mask)).square().mean();loss.backward()
        self.assertTrue(any(p.grad is not None and p.grad.abs().sum()>0 for p in T.parameters()))
        self.assertTrue(all(p.grad is None for m in [P,G,decoder] for p in m.parameters()));self.assertEqual(sha,statehash({'memory':fixed,'mask':mask}))
        self.assertTrue(all(p.data_ptr()!=q.data_ptr() for p,q in zip(T.parameters(),P.parameters())))
        self.assertIs(runtime.base.continuation_state('F',x,{'fixed':fixed}),fixed)
    def test_save_resume_counts_rng(self):
        with tempfile.TemporaryDirectory() as d,patch.object(torch.cuda,'get_rng_state_all',return_value=[]),patch.object(torch.cuda,'set_rng_state_all'):
            a=torch.nn.Linear(3,2);oa=torch.optim.AdamW(a.parameters(),lr=.001,weight_decay=0);x=torch.ones(8,3);a(x).sum().backward();oa.step()
            p=Path(d)/'resume.pt';runtime.base.resume_save(p,a,oa,1,[{'step':1}],{'instances':32},'schedule','P')
            b=torch.nn.Linear(3,2);ob=torch.optim.AdamW(b.parameters(),lr=.001,weight_decay=0);z=runtime.base.resume_load(p,b,ob,'schedule','P')
            self.assertEqual(z['completed'],1);self.assertEqual(z['counts']['instances'],32);self.assertEqual(statehash(a.state_dict()),statehash(b.state_dict()))
    def test_gate_full_and_raw_conditional(self):
        w=next(w for w in read(ROOT/'data/worlds.jsonl') if w['record_status']=='recorded_plan');o=observation(render(w,frame(w,0)),True,w,0)
        self.assertTrue(gate_current({'P':dict(o,next_joint=False)},True)['matched'])
        self.assertFalse(full_success(dict(joint=False),dict(joint=True)))
        import numpy as np
        a=np.array([1,0,1,0],bool);b=np.zeros(4,bool);mask=np.array([1,0,0,0],bool);draws=np.tile(np.arange(4),(2000,1));v,_=stats.paired_boot(a,b,mask,draws)
        self.assertEqual(v,1);self.assertEqual(a.mean(),.5)
        self.assertEqual(sum(stats.paired_counts(a,b).values()),4)
        self.assertIsNone(stats.paired_boot(a,b,np.zeros(4,bool),draws)[0])
        self.assertGreater(stats.wilson(0,160)[1],0);self.assertLess(stats.wilson(160,160)[0],1)
    def test_data_schedule_cells(self):
        ws=read(ROOT/'data/worlds.jsonl');self.assertEqual(len(ws),2880);self.assertEqual(len({key(w) for w in ws}),2880)
        old={key(w) for w in read(G15/'data/worlds.jsonl')};self.assertFalse(old & {key(w) for w in ws})
        by={w['record_id']:w for w in ws};ss=read(ROOT/'data/sample_schedule.jsonl');self.assertEqual(len(ss),200)
        cc=collections.Counter((by[r['record_id']]['record_status'],r['offset'],r['perspective']) for b in ss for r in b['replay']);self.assertEqual(len(cc),40);self.assertEqual(set(cc.values()),{40})
        for w in ws:
            for d,p in atomic_specs(w):self.assertEqual(advance(frame(w,d,p),'T_plus'),frame(w,d-1,p))
        for split,n in CFG['plan_world_counts'].items():self.assertEqual(collections.Counter(w['record_status'] for w in ws if w['split']==split),{s:n for s in ['recorded_plan','reported_cancelled','reported_completed']})
    def test_loss_equal_blocks_not_token_pooling(self):
        values=[torch.tensor(float(x),requires_grad=True) for x in [1,2,3,4]];loss=sum(values)/4;loss.backward();self.assertTrue(all(x.grad.item()==.25 for x in values))
        self.assertNotEqual(loss.item(),sum(x.item()*n for x,n in zip(values,[1,1,1,100]))/103)
    def test_actual_self_chain_no_gold_reset(self):
        w=next(w for w in read(ROOT/'data/worlds.jsonl') if w['record_status']=='recorded_plan')
        class Edit(torch.nn.Module):
            def forward(self,h,m):return h+10
        class Engine:
            def __init__(self):self.encoded=[]
            def decode(self,h,m):
                text=render(w,frame(w,-2 if float(h[0,0,0])==11 else -1));return [text]*len(h),[True]*len(h),[40]*len(h),0.
            def encode(self,texts):
                self.encoded+=texts;return torch.full((len(texts),1,1),5.),torch.ones(len(texts),1,dtype=torch.long),0.
            def batch(self,texts):
                class Batch:pass
                b=Batch();b.input_ids=torch.full((len(texts),1),9,dtype=torch.long);return b
        e=Engine();st=lambda v:dict(memory=torch.full((1,1,1),float(v)),mask=torch.ones(1,1,dtype=torch.long),input_ids=torch.tensor([[1]]))
        good=observation(render(w,frame(w,0)),True,w,0);bad=observation(render(w,frame(w,-2)),True,w,0)
        payload=dict(states={n:st(v) for n,v in [('start',1),('E',2),('P',3),('G',4),('U',5)]},current={'E':[good],'P':[good],'G':[good],'U':[bad]},gates=[dict(fixed_gate=dict(matched=False,failures=['U']),natural_mask_equal=True)])
        with patch.object(runtime.base,'slice_state',side_effect=lambda state,ix:{k:v[ix] for k,v in state.items()}),patch.object(runtime.base,'atom_eval',return_value=([],0.)),patch.object(runtime.base,'old_eval',return_value=[]):rows=runtime.base.final_model(e,Edit(),payload,[w],[w],42,'F-final','iid')
        self.assertEqual(len(e.encoded),4);self.assertEqual(e.encoded[-2:],[bad['output'],bad['output']])
        own=next(r for r in rows if r['kind']=='self_second');self.assertTrue(own['joint']);self.assertFalse(own['full']);self.assertEqual(own['first_failure'],1)

if __name__=='__main__':
    assert not torch.cuda.is_initialized();unittest.main(verbosity=2)
