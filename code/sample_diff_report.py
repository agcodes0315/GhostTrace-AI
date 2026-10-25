"""Diagnostic only. Sample labels NEVER influence full-dataset predictions."""
import csv, json
from collections import Counter
from pathlib import Path
from engine import EvidenceStore,audit_case,read_csv
from inspector import IdentityResolver

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'dataset'

def main():
    store=EvidenceStore(DATA)
    ids=IdentityResolver(read_csv(DATA/'user_identities.csv'), read_csv(DATA/'user_audit_log.csv'))
    rules=read_csv(DATA/'deletion_rules.csv')
    labels={x['case_id']:x for x in read_csv(DATA/'sample_output.csv')}
    failures=[]; tallies=Counter()
    for request in read_csv(DATA/'sample_deletion_requests.csv'):
        cid=request['case_id']; expected=labels[cid]
        pred, reasons=audit_case(request,ids.resolve(request['email']),store,rules)
        gold=json.loads(expected['steps_json']); got=pred['steps_json'] if pred else []
        if pred is None:
            kind='NO_EVIDENCE_BACKED_PREDICTION'
        elif pred['deletion_status']!=expected['deletion_status']:
            kind='STATUS_MISMATCH'
        elif got!=gold:
            kind='STEPS_MISMATCH'
        else:
            kind='EXACT_MATCH'
        tallies[kind]+=1
        exp_ops=[(x['operation'],x['system_id'],x['resource_id']) for x in gold]
        act_ops=[(x['operation'],x['system_id'],x['resource_id']) for x in got]
        missing=list((Counter(exp_ops)-Counter(act_ops)).elements())
        extra=list((Counter(act_ops)-Counter(exp_ops)).elements())
        failures.append({'case_id':cid,'class':kind,
           'expected_status':expected['deletion_status'],
           'predicted_status': pred['deletion_status'] if pred else None,
           'review_reasons':reasons,
           'missing_operations':missing,'extra_operations':extra,
           'operations_same':exp_ops==act_ops,
           'exact_steps_same':got==gold})
    (ROOT/'sample_diff_diagnostic.json').write_text(json.dumps({'summary':dict(tallies),'cases':failures},indent=2),encoding='utf-8')
    print('Diagnostic only; labels are never used in submission predictions.')
    print(json.dumps(dict(tallies),indent=2))
    print('Saved sample_diff_diagnostic.json')

if __name__=='__main__':main()
