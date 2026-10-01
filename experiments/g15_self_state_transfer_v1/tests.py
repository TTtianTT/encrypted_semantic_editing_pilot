"""CPU state-flow and archive checks; no CUDA initialization or GPU model load."""
import copy, inspect, tempfile, unittest
from unittest.mock import patch
import torch
from torch import nn
from common_g15 import *
run=load_module('g15_flow_under_test',ROOT/'run.py')

WORLD = json.loads((G14/'data/history_batches.json').read_text())['worlds']['iid'][0]
class TinyEditor(nn.Module):
    def __init__(self):super().__init__();self.bias=nn.Parameter(torch.tensor(.2))
    def forward(self,h,m):return h+self.bias*m[...,None]
class FakeEngine:
    def __init__(self):
        self.model=nn.Linear(3,2,bias=False)
        self.model.weight.data.copy_(torch.tensor([[.2,.3,.5],[.8,.7,.4]]))
        for p in self.model.parameters():p.requires_grad_(False)
        self.encoded=[]
    def decode(self,h,m):return [render(WORLD,frame(WORLD,0))]*len(h),[True]*len(h),[40]*len(h),0.
    def encode(self,texts):raise AssertionError('Unexpected encoding in latent training path')
def cpu_ce(e,h,m,golds):
    logits=e.model(h).mean(1)
    labels=torch.zeros(len(h),dtype=torch.long)
    return nn.functional.cross_entropy(logits,labels),sum(len(t.split()) for t in golds)
def toy_inputs():
    state=lambda val:dict(memory=torch.full((1,2,3),val),mask=torch.tensor([[1,0]]),input_ids=torch.tensor([[5,0]]))
    cur=observation(render(WORLD,frame(WORLD,0)),True,WORLD,0)
    return dict(start=state(1.),natural=state(2.),fixed=state(3.),background=state(4.),maintenance=state(5.),worlds=[WORLD],first_gold=[render(WORLD,frame(WORLD,0))],next_gold=[render(WORLD,frame(WORLD,-1))],background_gold=['a b'],maintenance_gold=['a b c d'],fixed_current=[cur],natural_current=[cur])

class StateFlow(unittest.TestCase):
    def test_O_detach_and_first_gradient_decoder_differentiability(self):
        e=FakeEngine();T=TinyEditor();inp=toy_inputs()
        with patch.object(run,'ce',cpu_ce):loss,z=run.four_block_loss(e,T,inp,'O')
        z['h1'].retain_grad();z['losses']['D'].backward(retain_graph=True)
        self.assertIsNone(z['h1'].grad);self.assertGreater(float(T.bias.grad.abs()),0)
        T.zero_grad();z['losses']['A'].backward(retain_graph=True)
        self.assertGreater(float(z['h1'].grad.abs().sum()),0)
        self.assertTrue(all(p.grad is None for p in e.model.parameters()))
        self.assertFalse(z['D_input']['memory'].requires_grad)
    def test_four_blocks_have_equal_weights_despite_unequal_tokens(self):
        e=FakeEngine();T=TinyEditor()
        with patch.object(run,'ce',cpu_ce):loss,z=run.four_block_loss(e,T,toy_inputs(),'N')
        torch.testing.assert_close(loss,torch.stack(list(z['losses'].values())).mean())
        weighted=sum(z['losses'][k]*z['tokens'][k] for k in 'ABCD')/sum(z['tokens'].values())
        self.assertGreater(float((weighted-loss).abs()),1e-5)
    def test_F_fixed_O_refresh_N_natural_no_encoder_reset(self):
        e=FakeEngine();T=TinyEditor();inp=toy_inputs();frozen=statehash(inp['fixed'])
        with patch.object(run,'ce',cpu_ce):
            _,first=run.four_block_loss(e,T,inp,'O')
            T.bias.data.add_(.3)
            _,second=run.four_block_loss(e,T,inp,'O')
            _,fixed=run.four_block_loss(e,T,inp,'F')
            _,natural=run.four_block_loss(e,T,inp,'N')
        self.assertNotEqual(statehash(first['D_input']),statehash(second['D_input']))
        self.assertEqual(statehash(fixed['D_input']),frozen)
        self.assertIs(fixed['D_input']['memory'],inp['fixed']['memory'])
        self.assertIs(natural['D_input']['mask'],inp['natural']['mask'])
        self.assertIs(second['D_input']['mask'],inp['start']['mask'])
    def test_actual_editor_preserves_input_and_masked_positions(self):
        ed=run.Editor();h=torch.randn(2,3,768);m=torch.tensor([[1,1,0],[1,0,0]]);before=h.clone()
        out=ed(h,m);torch.testing.assert_close(h,before);torch.testing.assert_close(out[m==0],h[m==0])
    def test_checkpoint_optimizer_and_rng_resume(self):
        T=TinyEditor();opt=torch.optim.AdamW(T.parameters(),lr=.001,weight_decay=0)
        def step():
            opt.zero_grad();loss=(T.bias-torch.rand(()))**2;loss.backward();opt.step()
        step();initial='same-P';saved=statehash(T.state_dict())
        with tempfile.TemporaryDirectory() as tmp,patch.object(torch.cuda,'get_rng_state_all',return_value=[]),patch.object(torch.cuda,'set_rng_state_all'):
            path=Path(tmp)/'resume.pt';run.resume_save(path,T,opt,1,[],{},'schedule',initial)
            step();expected=statehash(T.state_dict());T2=TinyEditor();opt2=torch.optim.AdamW(T2.parameters(),lr=.001,weight_decay=0)
            z=run.resume_load(path,T2,opt2,'schedule',initial);self.assertEqual(z['completed'],1);self.assertEqual(statehash(T2.state_dict()),saved)
            self.assertNotEqual(T.bias.data_ptr(),T2.bias.data_ptr());opt2.zero_grad();loss=(T2.bias-torch.rand(()))**2;loss.backward();opt2.step()
            self.assertEqual(statehash(T2.state_dict()),expected)
    def test_U_loader_rejects_train_and_pre_final(self):
        with self.assertRaises(AssertionError):run.load_editor(42,'U')
        with self.assertRaises(AssertionError):run.load_editor(42,'U',True,True)
        self.assertNotIn("load_editor(seed,'U'",inspect.getsource(run.train_group))
        self.assertNotIn("load_editor(seed,'U'",inspect.getsource(run.diagnose))
        self.assertNotIn("load_editor(42,'U'",inspect.getsource(run.smoke))
    def test_current_gate_excludes_same_wrong_and_ignores_next(self):
        correct=observation(render(WORLD,frame(WORLD,0)),True,WORLD,0)
        wrong=observation(render(WORLD,frame(WORLD,-2)),True,WORLD,0)
        self.assertTrue(gate_current({'P':correct,'U':correct},True)['matched'])
        self.assertFalse(gate_current({'P':wrong,'U':wrong},True)['matched'])
        with self.assertRaises(TypeError):gate_current({'P':correct},True,True)
    def test_full_not_endpoint(self):
        self.assertFalse(full_success({'joint':False},{'joint':True}))
        self.assertTrue(full_success({'joint':True},{'joint':True}))
    def test_final_latent_no_reset_actual_text_only_reset_control(self):
        class Edit(nn.Module):
            def forward(self,h,m):return h+10
        class Engine:
            def __init__(self):self.encoded=[]
            def decode(self,h,m):
                text=render(WORLD,frame(WORLD,-2 if float(h[0,0,0])==11 else -1))
                return [text]*len(h),[True]*len(h),[40]*len(h),0.
            def encode(self,texts):
                self.encoded+=texts;h=torch.full((len(texts),1,1),5.)
                return h,torch.ones(len(texts),1,dtype=torch.long),0.
            def batch(self,texts):
                class Batch:pass
                b=Batch();b.input_ids=torch.full((len(texts),1),9,dtype=torch.long);return b
        e=Engine();st=lambda v:dict(memory=torch.full((1,1,1),float(v)),mask=torch.ones(1,1,dtype=torch.long),input_ids=torch.tensor([[1]]))
        correct=observation(render(WORLD,frame(WORLD,0)),True,WORLD,0);wrong=observation(render(WORLD,frame(WORLD,-2)),True,WORLD,0)
        states={n:st(v) for n,v in [('start',1),('E',2),('P',3),('G',4),('U',5)]}
        payload=dict(states=states,current={'E':[correct],'P':[correct],'G':[correct],'U':[wrong]},gates=[dict(fixed_gate=dict(matched=False,failures=['U']),natural_mask_equal=True)])
        with patch.object(run,'slice_state',side_effect=lambda state,ix:{k:v[ix] for k,v in state.items()}),patch.object(run,'atom_eval',return_value=([],0.)),patch.object(run,'old_eval',return_value=[]):
            rows=run.final_model(e,Edit(),payload,[WORLD],[WORLD],42,'O','iid')
        # Only four explicit reset controls encode: P, G, actual wrong U, actual wrong Q.
        self.assertEqual(len(e.encoded),4)
        self.assertEqual(e.encoded[-2:], [wrong['output'],wrong['output']])
        selfrow=next(r for r in rows if r['kind']=='self_second')
        self.assertTrue(selfrow['joint']);self.assertFalse(selfrow['full']);self.assertEqual(selfrow['first_failure'],1)
        self.assertFalse(next(r for r in rows if r['kind']=='reset_self')['full'])

class DataAndStats(unittest.TestCase):
    def test_locked_data_schedule_and_grouping(self):
        verify_lock();worlds=read(ROOT/'data/worlds.jsonl');self.assertEqual(len(worlds),2880);self.assertEqual(len({key(w) for w in worlds}),2880)
        by={w['record_id']:w for w in worlds};schedule=read(ROOT/'data/sample_schedule.jsonl');self.assertEqual(len(schedule),200)
        counts=collections.Counter((by[r['record_id']]['record_status'],r['offset'],r['perspective']) for b in schedule for r in b['replay'])
        self.assertEqual(len(counts),40);self.assertEqual(set(counts.values()),{40})
        src=collections.Counter(x for b in schedule for x in b['maintenance_sources']);self.assertLessEqual(max(src.values())-min(src.values()),1)
        for split,n in CFG['plan_world_counts'].items():
            ws=[w for w in worlds if w['split']==split];self.assertEqual(len(ws),n*3)
            self.assertEqual(collections.Counter(w['record_status'] for w in ws),dict(recorded_plan=n,reported_cancelled=n,reported_completed=n))
    def test_statistics_empty_and_extreme_intervals(self):
        analyze=load_module('g15_statistics_under_test',ROOT/'analyze.py')
        self.assertGreater(analyze.wilson(0,160)[1],0)
        self.assertLess(analyze.wilson(160,160)[0],1)
        self.assertEqual(analyze.wilson(0,0),(None,None))
        self.assertEqual(analyze.paired_counts([1,1,0,0],[1,0,1,0]),dict(both=1,natural_only=1,edited_only=1,neither=1))

if __name__=='__main__':unittest.main(verbosity=2)
