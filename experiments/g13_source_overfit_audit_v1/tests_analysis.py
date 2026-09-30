"""Distinct parse/date/fact/frame/format failures and nondegenerate binary uncertainty."""
import unittest
from common_g13 import *
import importlib.util
spec=importlib.util.spec_from_file_location('g13_analysis_tests',ROOT/'analyze.py'); analysis=importlib.util.module_from_spec(spec); spec.loader.exec_module(analysis)
error_type, wilson=analysis.error_type, analysis.wilson
class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.w=next(w for w in read(ROOT/'data/worlds.jsonl') if w['record_status']=='recorded_plan'); self.c=frame(self.w,-2); self.gold=render(self.w,self.c)
    def row(self,text,ended=True): return dict(output=text,normal_end=ended,exact=text==self.gold,score=score(text,self.c,self.w,ended))
    def test_unresolved_is_not_fact_error(self):
        r=self.row('unparseable output'); self.assertEqual(error_type(r),'parse_unresolved'); self.assertFalse(r['score']['parsed_nondate_error'])
    def test_date_error(self):
        r=self.row(render(self.w,frame(self.w,0))); self.assertEqual(error_type(r),'date_error'); self.assertTrue(r['score']['nondate_facts_ok'])
    def test_fact_and_perspective_errors(self):
        w=dict(self.w,quantity=(self.w['quantity']%9)+1); self.assertEqual(error_type(self.row(render(w,self.c))),'fact_error')
        self.assertEqual(error_type(self.row(render(self.w,frame(self.w,-2,'third')))),'perspective_error')
    def test_format_and_length_limit(self):
        w=dict(self.w,template_family=(self.w['template_family']+1)%8); self.assertEqual(error_type(self.row(render(w,self.c))),'format_only')
        self.assertEqual(error_type(self.row(self.gold,False)),'length_limit'); self.assertEqual(error_type(self.row(self.gold)),'success')
    def test_extreme_binomial_has_uncertainty(self):
        self.assertGreater(wilson(0,160)[1],.02); self.assertLess(wilson(160,160)[0],.98); self.assertEqual(wilson(0,0),[None,None])
if __name__=='__main__': unittest.main()
