import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name('map_to_fmt002.py')
class MappingTests(unittest.TestCase):
    def run_sample(self, rows, identity=True):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            cfg={'envelope':dict(experiment_id='e',harness_id='h',task_id='t',variant_id='v',replicate=1,subject_id='s',rules_version='r'),'event_rules':[{'event':'attempt','map':{k:k for k in ['operation_index','attempt_index','outcome','steps','latency_ms','cost_units']}}]}
            if identity: cfg['identity_field']='session_id'
            (p/'map').write_text(json.dumps(cfg));(p/'in').write_text('\n'.join(json.dumps(r) for r in rows));(p/'out').write_text('previous')
            result=subprocess.run([sys.executable,str(SCRIPT),'--mapping',str(p/'map'),'--input',str(p/'in'),'--out',str(p/'out')],capture_output=True,text=True)
            return result.returncode,(p/'out').read_text()
    def row(self, scope='one', **kw):
        return dict(session_id=scope,operation_index=1,attempt_index=1,outcome='success',steps=1,latency_ms=2,cost_units=0.03,**kw)
    def test_separate_sessions_preserve_cost(self):
        code,out=self.run_sample([self.row(),self.row('two')]);self.assertEqual(code,0)
        rows=list(map(json.loads,out.splitlines()));self.assertEqual([r['assignment_id'] for r in rows],['one','two']);self.assertEqual(rows[0]['cost_units'],0.03)
    def test_duplicate_is_refused_atomically(self):
        self.assertEqual(self.run_sample([self.row(),self.row()]),(2,'previous'))
    def test_missing_identity(self):
        self.assertEqual(self.run_sample([self.row()],False),(2,'previous'))
    def test_invalid_rows_leave_existing_output(self):
        for key,value in [('outcome','unknown'),('steps',None),('cost_units',float('nan')),('session_id','')]:
            with self.subTest(key=key):
                bad=self.row('two');bad[key]=value
                self.assertEqual(self.run_sample([self.row(),bad]),(2,'previous'))
if __name__=='__main__': unittest.main()
