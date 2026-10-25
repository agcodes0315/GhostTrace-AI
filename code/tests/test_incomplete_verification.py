"""Keep verified/compliant resources in a proposed remediation verification plan."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import Observation, audit_case

class IncompleteVerificationTests(unittest.TestCase):
    def test_existing_absent_copy_remains_in_final_verification_plan(self):
        class Store:
            observations = [
                Observation('account_service', 'account_a', 'USER_PROFILE', 'ABSENT', 'evidence_account', '2026-05-01T00:00:00Z', {'user_id': 'user_a'}),
                Observation('search_service', 'search_b', 'SEARCH_INDEX_ENTRY', 'PRESENT', 'evidence_search', '2026-05-01T00:00:00Z', {'user_id': 'user_a'}),
            ]
        case = {'case_id': 'synthetic', 'request_text': 'Delete my personal data', 'audit_at': '2026-05-02T00:00:00Z'}
        identity = {'resolution': 'EXACT', 'identifiers': {'user_id': ['user_a']}}
        rules = [{'data_category': 'USER_PROFILE', 'required_action': 'DELETE'}, {'data_category': 'SEARCH_INDEX_ENTRY', 'required_action': 'DELETE'}]
        result, reasons = audit_case(case, identity, Store(), rules)
        self.assertEqual(reasons, [])
        self.assertEqual(result['deletion_status'], 'INCOMPLETE')
        steps = result['steps_json']
        self.assertIn(('VERIFY_RECORD_ABSENT', 'account_a'), {(s['operation'], s['resource_id']) for s in steps})
        self.assertIn(('VERIFY_RECORD_ABSENT', 'search_b'), {(s['operation'], s['resource_id']) for s in steps})
        self.assertTrue(all(s['evidence_id'] == '' for s in steps if s['phase']=='VERIFICATION'))

if __name__ == '__main__': unittest.main()
