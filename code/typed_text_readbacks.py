"""Parse explicit timestamped resource lookups from supplied diagnostic logs/shift handovers.

Only typed, resource-level observations are returned; never treat narrative claims as proof.
"""
import re

HANDOVER = re.compile(r'^-\s*(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)\s*\|\s*([a-z_]+)\s*\|\s*([a-z_0-9]+)\s*\|\s*([A-Z_]+)\s*\|\s*([A-Z_]+)\s*\|\s*(.+?)\s*$')
KV = re.compile(r'([a-z_]+)=(?:"([^"]*)"|([^\s]+))')
VALID_CATEGORY={'USER_PROFILE','SECONDARY_IDENTIFIER','SEARCH_INDEX_ENTRY','CACHE_ENTRY','SUPPORT_MESSAGE','SUPPORT_ATTACHMENT','ANALYTICS_PROFILE','PRODUCT_TELEMETRY','USER_EXPORT','MARKETING_PROFILE','EMAIL_DELIVERY_LOG','SECURITY_AUDIT_LOG','LEGAL_HOLD_RECORD','BACKUP_ARCHIVE','ACCOUNT_TOMBSTONE','DATA_FLOW'}
STATE={'NOT_FOUND':'ABSENT','FOUND':'PRESENT','IDENTIFIABLE':'PRESENT','ANONYMIZED':'ANONYMIZED','REDACTED':'REDACTED','ACTIVE':'ACTIVE','DISABLED':'DISABLED','BLOCKED':'BLOCKED','PRESENT':'PRESENT','ABSENT':'ABSENT'}

def extract_readbacks(path):
    for line in path.read_text(encoding='utf-8-sig',errors='replace').splitlines():
        m=HANDOVER.match(line)
        if m:
            when,system,resource,category,result,subject=m.groups()
            if category not in VALID_CATEGORY or result not in STATE: continue
            if not (subject and subject.casefold()!='no direct identifier'):
                # Cannot link records with no identity, even when state is known.
                continue
            yield {'captured_at':when,'system_id':system,'resource_id':resource,'data_category':category,
                   'state':STATE[result], 'subject_reference':subject.strip()}
            continue
        if not re.match(r'^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ\s',line):continue
        pairs={k:(quoted if quoted!='' else raw) for k,quoted,raw in KV.findall(line)}
        if pairs.get('event')!='record_lookup':continue
        category=pairs.get('record_type','');status=pairs.get('result','')
        if category not in VALID_CATEGORY or status not in STATE:continue
        if not all(pairs.get(k) for k in ('system','resource_id','subject_reference')):continue
        yield {'captured_at':line[:20],'system_id':pairs['system'],'resource_id':pairs['resource_id'],
               'data_category':category,'state':STATE[status],
               'subject_reference':pairs['subject_reference']}
