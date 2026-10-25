"""Extract typed, timestamped observations from supplied SQLite-compatible SQL snapshots.

Physical rows prove presence, not absence. Never use user-facing sample labels.
"""
import json

COLLECTION_CATEGORIES = {
    'customer_profiles':'USER_PROFILE', 'account_profiles':'USER_PROFILE',
    'account_tombstones':'ACCOUNT_TOMBSTONE',
    'customer_search_documents':'SEARCH_INDEX_ENTRY',
    'customer_analytics_reports':'ANALYTICS_PROFILE',
    'security_audit_events':'SECURITY_AUDIT_LOG',
    'backup_catalog':'BACKUP_ARCHIVE',
    'connector_configurations':'DATA_FLOW',
    'support_tickets':'SUPPORT_MESSAGE',
    'customer_exports':'USER_EXPORT',
    'marketing_profiles':'MARKETING_PROFILE',
}

def extract_sql_row(row):
    if not isinstance(row,dict) or not row.get('record_json') or not row.get('origin_system'):
        return None
    try:
        payload=json.loads(row['record_json'])
    except (ValueError,TypeError):
        return None
    if not isinstance(payload,dict): return None
    system=str(row['origin_system']); category=COLLECTION_CATEGORIES.get(str(row.get('collection_name','')))
    if not category: return None
    resource=str(row.get('resource_id',''))
    if not resource or payload.get('resource_id')!=resource: return None
    enriched=dict(payload)
    enriched.update(system_id=system,resource_id=resource,data_category=category,
                    captured_at=row.get('updated_at',''))
    if category=='DATA_FLOW':
        if not isinstance(payload.get('enabled'),bool): return None
        state='ACTIVE' if payload['enabled'] else 'DISABLED'
    elif category=='BACKUP_ARCHIVE':
        if not isinstance(payload.get('restore_allowed'),bool): return None
        state='ACTIVE' if payload['restore_allowed'] else 'BLOCKED'
    elif category=='ANALYTICS_PROFILE':
        direct=('user_id','email','phone','email_hash')
        state='PRESENT' if any(payload.get(k) for k in direct) else 'ANONYMIZED'
    elif category=='ACCOUNT_TOMBSTONE':
        state='REDACTED' if not any(payload.get(k) for k in ('email','phone','name','email_hash')) else 'PRESENT'
    elif category=='USER_PROFILE':
        # A tombstone still stored with identifiers is not proof of erasure.
        state='PRESENT'
    else:
        state='PRESENT'
    enriched['state']=state
    return enriched
