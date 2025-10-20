-- Create indexes on audit_log table for better query performance
-- Using CONCURRENTLY to avoid table locking (safe for production)

-- Table name index - for filtering by table
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_log_table_name
ON audit_log(table_name);

-- Action type index - for filtering by action (CREATE, UPDATE, DELETE, etc.)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_log_action
ON audit_log(action);

-- User index - for filtering by who made the change
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_log_changed_by
ON audit_log(changed_by);

-- Timestamp index (descending) - for date range queries and sorting
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_log_changed_at
ON audit_log(changed_at DESC);

-- Record ID index - for looking up changes to specific records
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_log_record_id
ON audit_log(record_id);

-- Composite index for common query pattern (table + date)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_log_table_date
ON audit_log(table_name, changed_at DESC);

-- Composite index for another common pattern (action + date)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_log_action_date
ON audit_log(action, changed_at DESC);

