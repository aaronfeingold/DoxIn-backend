# Database Migrations

This directory contains SQL migration scripts for database schema changes.

## How to Apply Migrations

### Local Development (Docker PostgreSQL)

```bash
cd backend

# Apply a migration
PGPASSWORD=password psql -h localhost -p 5433 -U case-study -d case-study -f migrations/your_migration.sql

# Verify the migration
PGPASSWORD=password psql -h localhost -p 5433 -U case-study -d case-study -c "\d table_name"
```

### Production (Neon PostgreSQL)

```bash
cd backend

# Set your Neon connection string
export DATABASE_URL="your_neon_connection_string"

# Apply migration
psql $DATABASE_URL -f migrations/your_migration.sql

# Verify
psql $DATABASE_URL -c "\d table_name"
```

## Migration History

### 2025-09-30: Add uploaded_by_user_id to invoices

- **File**: `add_uploaded_by_user_id.sql`
- **Purpose**: Track which user uploaded each invoice
- **Changes**:
  - Added `uploaded_by_user_id` UUID column to `invoices` table
  - Added foreign key reference to `users(id)`
  - Created index for query performance
- **Status**: ✅ Applied

## Best Practices

1. **Always create a migration file** before modifying models
2. **Test migrations locally** before applying to production
3. **Make columns nullable initially** if adding to existing tables
4. **Include rollback instructions** in migration comments
5. **Name files descriptively** with date prefix: `YYYY-MM-DD_description.sql`
