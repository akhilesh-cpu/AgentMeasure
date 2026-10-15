"""Regression coverage for period freshness and unresolved hosted reviews."""
import datetime
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
SPEC = importlib.util.spec_from_file_location('reconcile_period', Path(__file__).resolve().parents[2] / 'scripts/reconcile_period.py')
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)
class TestPeriodReview(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.export = self.root / 'input.csv'
        self.export.write_text('reviewed export')
        self.cfg = dict(vendor='intercom', billing_period='2026-09', export='input.csv', reviewed_export_sha256=hashlib.sha256(self.export.read_bytes()).hexdigest())
    def test_previous_month_passes_scheduled_review(self):
        self.assertEqual(module.validate_config(self.cfg,self.root,True,datetime.date(2026,10,3))[1],'2026-09')
    def test_stale_period_stops_next_month(self):
        with self.assertRaisesRegex(ValueError,'Stale'):
            module.validate_config(self.cfg,self.root,True,datetime.date(2026,11,3))
    def test_year_boundary_and_manual_history(self):
        self.cfg['billing_period']='2025-12'
        module.validate_config(self.cfg,self.root,True,datetime.date(2026,1,3))
        module.validate_config(self.cfg,self.root,False)
    def test_changed_export_requires_new_review(self):
        self.export.write_text('unreviewed revision')
        with self.assertRaisesRegex(ValueError,'Review the export'):
            module.validate_config(self.cfg,self.root)
    def test_path_cannot_escape_repository(self):
        self.cfg['export']='../outside.csv'
        with self.assertRaisesRegex(ValueError,'inside this repository'):
            module.validate_config(self.cfg,self.root)
    def test_invalid_period_rejected(self):
        self.cfg['billing_period']='2026-13'
        with self.assertRaisesRegex(ValueError,'YYYY-MM'):
            module.validate_config(self.cfg,self.root)
    def test_offsetting_findings_still_need_review(self):
        self.assertTrue(module.needs_review({'variance':0,'counts':{'billed_but_not_billable':1,'billable_but_not_billed':1}}))
    def test_unknown_without_dollar_price_still_needs_review(self):
        self.assertTrue(module.needs_review({'counts':{'cannot_settle':5}}))
    def test_agreement_needs_no_issue(self):
        self.assertFalse(module.needs_review({'counts':{'agrees':5}}))
