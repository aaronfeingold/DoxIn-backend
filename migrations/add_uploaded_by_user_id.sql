-- Migration: Add uploaded_by_user_id column to invoices table
-- Date: 2025-09-30

-- Add the column (nullable for now to allow existing data)
ALTER TABLE invoices
ADD COLUMN IF NOT EXISTS uploaded_by_user_id UUID REFERENCES users(id);

-- Create an index for better query performance
CREATE INDEX IF NOT EXISTS idx_invoices_uploaded_by_user_id
ON invoices(uploaded_by_user_id);

-- Optional: Set a default user for existing invoices (uncomment if needed)
-- UPDATE invoices
-- SET uploaded_by_user_id = (SELECT id FROM users WHERE role = 'admin' LIMIT 1)
-- WHERE uploaded_by_user_id IS NULL;
