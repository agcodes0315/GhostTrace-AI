import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from snapshot_records import extract_snapshot_records
from engine import Observation, needs_action

class TombstoneSemanticsTests(unittest.TestCase):
    def snapshot(self, record):
        return {'snapshots':[{'data_store':'identity_service','collection':'deleted_customer_references',
                'captured_at':'2026-01-01T00:00:00Z','records':[record]}]}
    def test_clean_tombstone_is_redacted_not_deleted(self):
        rows=list(extract_snapshot_records(self.snapshot({'resource_id':'tombstone_1','subject_reference':'user_1','account_status':'DELETED','email':None,'name':None})))
        self.assertEqual(rows[0]['data_category'],'ACCOUNT_TOMBSTONE')
        self.assertEqual(rows[0]['state'],'REDACTED')
    def test_dirty_tombstone_needs_redaction(self):
        rows=list(extract_snapshot_records(self.snapshot({'resource_id':'tombstone_2','subject_reference':'user_1','account_status':'DELETED','email':'example@example.org'})))
        self.assertEqual(rows[0]['state'],'PRESENT')
    def test_owner_metadata_does_not_overrule_redaction_state(self):
        obs=Observation('support_platform','support_1','SUPPORT_MESSAGE','REDACTED','evidence_1','2026-01-01T00:00:00Z',{'subject_reference':'user_1','customer_email':'example@example.org'})
        self.assertFalse(needs_action(obs,'REDACT'))

if __name__=='__main__': unittest.main()
