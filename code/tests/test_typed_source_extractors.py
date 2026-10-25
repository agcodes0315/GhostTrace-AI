import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sql_snapshot_evidence import extract_sql_row
from typed_text_readbacks import extract_readbacks

class TypedSourceTests(unittest.TestCase):
    def test_sql_nested_profile_has_resource_and_typed_state(self):
        import json
        row={'resource_id':'account_50','origin_system':'account_service','collection_name':'customer_profiles',
             'updated_at':'2026-09-01T00:00:00Z','record_json':json.dumps({'resource_id':'account_50','email':'x@example.com','user_id':'user_50'})}
        parsed=extract_sql_row(row)
        self.assertEqual(parsed['state'],'PRESENT')
        self.assertEqual(parsed['data_category'],'USER_PROFILE')
        self.assertEqual(parsed['captured_at'],row['updated_at'])
    def test_sql_no_phantom_absence(self):
        self.assertIsNone(extract_sql_row({'resource_id':'account_50','origin_system':'account_service','record_json':'{}'}))
    def test_sql_connector_disabled(self):
        import json
        row={'resource_id':'data_flow_1','origin_system':'integration_service','collection_name':'connector_configurations',
            'updated_at':'2026-09-01T00:00:00Z','record_json':json.dumps({'resource_id':'data_flow_1','subject_selector':'user_1','enabled':False})}
        self.assertEqual(extract_sql_row(row)['state'],'DISABLED')
    def test_log_requires_exact_result(self):
        text='2026-09-06T07:00:00Z INFO service=search_index_service event=record_lookup seq=8 system="account_service" resource_id="account_8473" record_type="USER_PROFILE" result="NOT_FOUND" subject_reference="x@example.com"\n'
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'test.log';p.write_text(text,encoding='utf8')
            obs=list(extract_readbacks(p))
        self.assertEqual(len(obs),1)
        self.assertEqual(obs[0]['state'],'ABSENT')
    def test_handover_identifier_required(self):
        text='- 2026-10-01T12:00:00Z | analytics_platform | analytics_6830 | ANALYTICS_PROFILE | ANONYMIZED | no direct identifier\n'
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'handover.txt';p.write_text(text,encoding='utf8')
            obs=list(extract_readbacks(p))
        self.assertEqual(obs,[])
if __name__=='__main__':unittest.main()
