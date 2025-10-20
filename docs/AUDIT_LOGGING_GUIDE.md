# Audit Logging Implementation Guide

This guide shows how to add comprehensive audit logging throughout the application.

## Overview

The application now has a utility module (`app.utils.audit`) that makes it easy to add audit logging to any database operation, even when not using the `BaseModel.save()` or `BaseModel.delete()` methods.

## Quick Reference

### Import the utilities

```python
from app.utils.audit import create_audit_log, audit_bulk_operation
```

### Basic Operations

```python
# CREATE operation
create_audit_log(
    table_name='invoices',
    record_id=invoice.id,
    action='CREATE',
    new_values=invoice.to_dict(),
    reason='Invoice uploaded via API'
)

# UPDATE operation
create_audit_log(
    table_name='users',
    record_id=user.id,
    action='UPDATE',
    old_values=old_user_dict,
    new_values=user.to_dict(),
    reason='User role change'
)

# DELETE operation
create_audit_log(
    table_name='products',
    record_id=product.id,
    action='DELETE',
    old_values=product.to_dict(),
    reason='Product discontinued'
)

# BULK operations
audit_bulk_operation(
    table_name='products',
    action='BULK_IMPORT',
    record_count=150,
    summary={'source': 'Excel', 'filename': 'products.xlsx'},
    reason='Monthly catalog update'
)
```

## Real-World Examples

### Example 1: FileStorage Creation (invoices.py)

**BEFORE (No audit logging):**

```python
file_storage = FileStorage(
    user_id=user_id,
    file_name=filename,
    file_size=file_size,
    mime_type=mime_type,
    blob_url=blob_url
)
db.session.add(file_storage)
db.session.commit()
```

**AFTER (With audit logging):**

```python
from app.utils.audit import create_audit_log

file_storage = FileStorage(
    user_id=user_id,
    file_name=filename,
    file_size=file_size,
    mime_type=mime_type,
    blob_url=blob_url
)
db.session.add(file_storage)
db.session.flush()  # Get the ID

# Add audit log
create_audit_log(
    table_name='file_storage',
    record_id=file_storage.id,
    action='CREATE',
    new_values=file_storage.to_dict(),
    reason='File uploaded for processing'
)

db.session.commit()
```

### Example 2: ProcessingJob Creation (invoices.py)

**BEFORE:**

```python
processing_job = ProcessingJob(
    id=task_id,
    user_id=user_id,
    file_storage_id=file_storage.id,
    job_type='invoice_extraction',
    status='pending'
)
db.session.add(processing_job)
db.session.commit()
```

**AFTER:**

```python
from app.utils.audit import create_audit_log

processing_job = ProcessingJob(
    id=task_id,
    user_id=user_id,
    file_storage_id=file_storage.id,
    job_type='invoice_extraction',
    status='pending'
)
db.session.add(processing_job)
db.session.flush()

create_audit_log(
    table_name='processing_jobs',
    record_id=processing_job.id,
    action='CREATE',
    new_values=processing_job.to_dict(),
    reason='New processing job initiated'
)

db.session.commit()
```

### Example 3: Report Generation (reports.py)

**BEFORE:**

```python
report = Report(
    report_type=report_type,
    status='pending',
    parameters=parameters,
    user_id=current_user.id
)
db.session.add(report)
db.session.commit()
```

**AFTER:**

```python
from app.utils.audit import create_audit_log

report = Report(
    report_type=report_type,
    status='pending',
    parameters=parameters,
    user_id=current_user.id
)
db.session.add(report)
db.session.flush()

create_audit_log(
    table_name='reports',
    record_id=report.id,
    action='CREATE',
    new_values=report.to_dict(),
    user_email=current_user.email,
    reason=f'Report generation requested: {report_type}'
)

db.session.commit()
```

### Example 4: Updating ProcessingJob Status (invoices.py)

**BEFORE:**

```python
job = ProcessingJob.query.get(task_id)
job.status = 'completed'
job.result_data = result
db.session.commit()
```

**AFTER:**

```python
from app.utils.audit import create_audit_log

job = ProcessingJob.query.get(task_id)
old_values = job.to_dict()

job.status = 'completed'
job.result_data = result

create_audit_log(
    table_name='processing_jobs',
    record_id=job.id,
    action='UPDATE',
    old_values=old_values,
    new_values=job.to_dict(),
    reason='Processing job completed'
)

db.session.commit()
```

### Example 5: Bulk Import (load_excel_data.py)

**BEFORE:**

```python
# Import 150 products
for product_data in products:
    product = Product(**product_data)
    db.session.add(product)
db.session.commit()
```

**AFTER:**

```python
from app.utils.audit import audit_bulk_operation

# Import 150 products
product_count = 0
for product_data in products:
    product = Product(**product_data)
    db.session.add(product)
    product_count += 1

audit_bulk_operation(
    table_name='products',
    action='BULK_IMPORT',
    record_count=product_count,
    summary={
        'source': 'Excel import',
        'filename': excel_filename,
        'categories': ['electronics', 'accessories']
    },
    reason='Monthly product catalog update'
)

db.session.commit()
```

### Example 6: User Permission Change (admin.py)

**BEFORE:**

```python
user = User.query.get(user_id)
user.role = new_role
db.session.commit()
```

**AFTER:**

```python
from app.utils.audit import create_audit_log

user = User.query.get(user_id)
old_values = user.to_dict()

user.role = new_role

create_audit_log(
    table_name='users',
    record_id=user.id,
    action='UPDATE',
    old_values=old_values,
    new_values=user.to_dict(),
    user_email=g.current_user_email,
    reason=f'User role changed from {old_values["role"]} to {new_role}'
)

db.session.commit()
```

### Example 7: Invoice Line Item Update

**BEFORE:**

```python
line_item = InvoiceLineItem.query.get(line_item_id)
line_item.quantity = new_quantity
line_item.line_total = new_quantity * line_item.unit_price
db.session.commit()
```

**AFTER:**

```python
from app.utils.audit import create_audit_log

line_item = InvoiceLineItem.query.get(line_item_id)
old_values = line_item.to_dict()

line_item.quantity = new_quantity
line_item.line_total = new_quantity * line_item.unit_price

create_audit_log(
    table_name='invoice_line_items',
    record_id=line_item.id,
    action='UPDATE',
    old_values=old_values,
    new_values=line_item.to_dict(),
    reason='Line item quantity corrected'
)

db.session.commit()
```

## Best Practices

### 1. Always Use `db.session.flush()` for New Records

When creating new records, use `flush()` to get the ID before creating the audit log:

```python
new_record = Model(...)
db.session.add(new_record)
db.session.flush()  # This assigns the ID

create_audit_log(
    table_name='table_name',
    record_id=new_record.id,  # Now we have the ID
    action='CREATE',
    new_values=new_record.to_dict()
)

db.session.commit()
```

### 2. Capture Old Values for Updates

Always capture the old state before making changes:

```python
record = Model.query.get(id)
old_values = record.to_dict()  # Capture BEFORE changes

# Make changes
record.field = new_value

create_audit_log(
    table_name='table_name',
    record_id=record.id,
    action='UPDATE',
    old_values=old_values,  # Before state
    new_values=record.to_dict(),  # After state
    reason='Field updated'
)

db.session.commit()
```

### 3. Provide Meaningful Reasons

Use descriptive reasons that explain why the change was made:

```python
# Good
reason='User requested invoice deletion via support ticket #1234'

# Bad
reason='Deleted'
```

### 4. Use Bulk Operations for Mass Changes

For operations affecting multiple records, use `audit_bulk_operation()`:

```python
# Update 500 product prices
updated_count = Product.query.filter(
    Product.category == 'electronics'
).update({'list_price': Product.list_price * 1.1})

audit_bulk_operation(
    table_name='products',
    action='BULK_UPDATE',
    record_count=updated_count,
    summary={'category': 'electronics', 'price_increase': '10%'},
    reason='Quarterly price adjustment'
)

db.session.commit()
```

### 5. Include User Context

The `user_email` is automatically detected from `g.current_user_email`, but you can override it:

```python
create_audit_log(
    table_name='invoices',
    record_id=invoice.id,
    action='CREATE',
    new_values=invoice.to_dict(),
    user_email='system@automated.com',  # Override for system operations
    reason='Automated invoice creation from EDI'
)
```

## Action Types

Use these standard action types:

- `CREATE` - New record created
- `UPDATE` - Existing record modified
- `DELETE` - Record deleted
- `BULK_CREATE` - Multiple records created
- `BULK_UPDATE` - Multiple records updated
- `BULK_DELETE` - Multiple records deleted
- `BULK_IMPORT` - Bulk import from external source
- `RESTORE` - Soft-deleted record restored
- `ARCHIVE` - Record archived

## Routes That Need Audit Logging

### High Priority (User-facing writes)

1. **File Operations** (`app/routes/invoices.py`)

   - File upload: `POST /invoices/process-batch`
   - File deletion: N/A (add if exists)

2. **Invoice Operations** (`app/routes/invoices.py`)

   - Invoice approval: `POST /invoices/approve/<task_id>`
   - Invoice update: `PUT /invoices/<invoice_id>`
   - Invoice deletion: `DELETE /invoices/<invoice_id>`

3. **User Management** (`app/routes/admin.py`)

   - User role change: `PATCH /admin/users/<user_id>/role`
   - User activation/deactivation: `PATCH /admin/users/<user_id>/status`

4. **Report Generation** (`app/routes/reports.py`)
   - Report creation: `POST /reports/generate`
   - Report deletion: `DELETE /reports/<report_id>`

### Medium Priority (Admin operations)

5. **Access Codes** (`app/routes/admin.py`)

   - Code generation: `POST /admin/access-codes`
   - Code revocation: `DELETE /admin/access-codes/<code_id>`

6. **Company Management**

   - Company creation/update/deletion

7. **Product Management**
   - Product creation/update/deletion
   - Bulk product imports

### Low Priority (System operations)

8. **Processing Jobs**

   - Status updates
   - Error logging

9. **Document Processing Logs**
   - LLM interaction logging

## Viewing Audit Logs

### Frontend (Admin UI)

Navigate to: `/admin/audit-log`

Features:

- Paginated table view
- Filter by table name, action, or user
- View detailed before/after values
- Export capability (coming soon)

### API Endpoint

```bash
GET /api/admin/audit-log
```

Query parameters:

- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 50, max: 100)
- `table` - Filter by table name
- `action` - Filter by action type
- `changed_by` - Filter by user email

Example:

```bash
curl -H "Authorization: Bearer <token>" \
  "https://api.example.com/api/admin/audit-log?table=invoices&action=UPDATE&page=1"
```

## Testing Audit Logs

### Unit Test Example

```python
def test_audit_log_created_on_invoice_creation(client, auth_headers):
    """Test that creating an invoice creates an audit log entry"""

    # Create invoice
    response = client.post(
        '/api/admin/invoices',
        json=invoice_data,
        headers=auth_headers
    )

    assert response.status_code == 201
    invoice_id = response.json['invoice']['id']

    # Verify audit log was created
    audit_log = AuditLog.query.filter_by(
        table_name='invoices',
        record_id=invoice_id,
        action='CREATE'
    ).first()

    assert audit_log is not None
    assert audit_log.changed_by == 'admin@example.com'
    assert audit_log.new_values['invoice_number'] == invoice_data['invoice_number']
```

## Performance Considerations

### Indexing

Ensure these indexes exist for query performance:

```sql
CREATE INDEX idx_audit_log_table_name ON audit_log(table_name);
CREATE INDEX idx_audit_log_action ON audit_log(action);
CREATE INDEX idx_audit_log_changed_by ON audit_log(changed_by);
CREATE INDEX idx_audit_log_changed_at ON audit_log(changed_at DESC);
CREATE INDEX idx_audit_log_record_id ON audit_log(record_id);
```

### Data Retention

Consider implementing a retention policy:

```python
# Archive audit logs older than 2 years
old_date = datetime.utcnow() - timedelta(days=730)
AuditLog.query.filter(
    AuditLog.changed_at < old_date
).delete()
```

## Troubleshooting

### Audit log not created

1. Check that `db.session.commit()` is called
2. Verify the audit utility is imported correctly
3. Check Flask logs for audit logging errors
4. Ensure the AuditLog model is in the database

### User email showing as "system"

The user email is auto-detected from `g.current_user_email`. If showing "system":

1. Verify authentication middleware is setting `g.current_user_email`
2. Manually pass `user_email` parameter if needed
3. Check that the request context is available

### Changed fields not showing

Changed fields are only calculated for UPDATE operations when both `old_values` and `new_values` are provided.

## Migration Checklist

- [ ] Add audit logging to all file upload operations
- [ ] Add audit logging to all invoice CRUD operations
- [ ] Add audit logging to user management operations
- [ ] Add audit logging to report generation
- [ ] Add audit logging to access code operations
- [ ] Add audit logging to bulk import operations
- [ ] Create database indexes for audit_log table
- [ ] Test audit log creation in development
- [ ] Review audit logs in staging
- [ ] Deploy to production
- [ ] Set up audit log retention policy
