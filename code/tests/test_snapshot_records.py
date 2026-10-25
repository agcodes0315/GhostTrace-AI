import unittest
from snapshot_records import extract_snapshot_records

class SnapshotRecordsTests(unittest.TestCase):
    def test_nested_record_uses_actual_capture_time(self):
        d={'snapshots':[{'captured_at':'2026-01-01T00:00:00Z','data_store':'account_service','collection':'customer_profiles','records':[{'resource_id':'a1','user_id':'u1','account_status':'ACTIVE'}]}]}
        row=list(extract_snapshot_records(d))[0]
        self.assertEqual((row['system_id'],row['state'],row['captured_at']),('account_service','PRESENT','2026-01-01T00:00:00Z'))
    def test_empty_snapshot_is_not_absence(self):
        d={'snapshots':[{'captured_at':'2026-01-01T00:00:00Z','data_store':'account_service','collection':'customer_profiles','records':[]}]}
        self.assertEqual(list(extract_snapshot_records(d)),[])
    def test_restore_gate(self):
        d={'snapshots':[{'captured_at':'2026-01-01T00:00:00Z','data_store':'backup_service','collection':'backup_catalog','records':[{'resource_id':'a1','subject_reference':'user_id:u1','restore_allowed':True}]}]}
        self.assertEqual(list(extract_snapshot_records(d))[0]['state'],'ACTIVE')
    def test_unknown_state_is_rejected(self):
        d={'snapshots':[{'captured_at':'2026-01-01T00:00:00Z','data_store':'account_service','collection':'customer_profiles','records':[{'resource_id':'a1','account_status':'PENDING'}]}]}
        self.assertEqual(list(extract_snapshot_records(d)),[])
