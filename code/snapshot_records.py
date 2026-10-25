"""Strict extraction of timestamped record snapshots; no absence inferred from missing rows."""
from __future__ import annotations

CATEGORIES = {
    ('account_service','customer_profiles'): 'USER_PROFILE',
    ('identity_service','deleted_customer_references'): 'USER_PROFILE',
    ('analytics_platform','customer_analytics_reports'): 'ANALYTICS_PROFILE',
    ('backup_service','backup_catalog'): 'BACKUP_ARCHIVE',
    ('export_service','customer_export_jobs'): 'USER_EXPORT',
    ('integration_service','connector_configurations'): 'DATA_FLOW',
    ('search_service','customer_search_documents'): 'SEARCH_INDEX_ENTRY',
    ('security_service','security_audit_events'): 'SECURITY_AUDIT_LOG',
    ('support_platform','support_conversations'): 'SUPPORT_MESSAGE',
    ('support_platform','ticket_attachments'): 'SUPPORT_ATTACHMENT',
    ('legal_service','retained_order_records'): 'LEGAL_HOLD_RECORD',
}

def extract_snapshot_records(document):
    if not isinstance(document,dict): return
    for snapshot in document.get('snapshots',[]):
        if not isinstance(snapshot,dict): continue
        captured=snapshot.get('captured_at')
        system=snapshot.get('data_store')
        collection=snapshot.get('collection')
        if not isinstance(captured,str) or not isinstance(system,str): continue
        records=snapshot.get('records')
        if not isinstance(records,list): continue
        for record in records:
            if not isinstance(record,dict) or not isinstance(record.get('resource_id'),str): continue
            row=dict(record)
            row['system_id']=str(record.get('system') or system)
            row['captured_at']=str(record.get('recorded_at') or captured)
            row['data_category']=str(record.get('record_type') or CATEGORIES.get((system,collection)) or '')
            # Emit only clear record states; presence in a listing is not proof of deletion.
            if collection=='operational_record_history':
                row['state']=record.get('result') or ''
            elif collection=='deleted_customer_references':
                row['state']='ABSENT' if str(record.get('account_status','')).upper()=='DELETED' else ''
            elif collection=='customer_profiles':
                row['state']='PRESENT' if record.get('account_status')=='ACTIVE' else ''
            elif collection=='backup_catalog' and isinstance(record.get('restore_allowed'),bool):
                row['state']='ACTIVE' if record['restore_allowed'] else 'BLOCKED'
            elif collection=='connector_configurations' and isinstance(record.get('enabled'),bool):
                row['state']='ACTIVE' if record['enabled'] else 'DISABLED'
            elif collection=='customer_analytics_reports':
                # Named report still exists; identifier means it must be anonymized.
                row['state']='PRESENT'
            elif collection in ('customer_search_documents','security_audit_events','support_conversations','ticket_attachments','customer_export_jobs','retained_order_records'):
                row['state']='PRESENT'
            else: continue
            if row['state']: yield row
