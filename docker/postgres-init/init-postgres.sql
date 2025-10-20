-- PostgreSQL initialization script for Case Study Invoice App
-- This script runs automatically when the Docker container starts for the first time

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Log extension status
DO $$
BEGIN
    RAISE NOTICE 'PostgreSQL initialization complete';
    RAISE NOTICE 'Available extensions:';
    RAISE NOTICE 'vector: %', (SELECT CASE WHEN EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN 'ENABLED' ELSE 'NOT ENABLED' END);
    RAISE NOTICE 'uuid-ossp: %', (SELECT CASE WHEN EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'uuid-ossp') THEN 'ENABLED' ELSE 'NOT ENABLED' END);
END $$;

-- Verify extensions are available and working
SELECT
    name,
    default_version,
    installed_version,
    CASE WHEN installed_version IS NOT NULL THEN 'ENABLED' ELSE 'AVAILABLE' END as status
FROM pg_available_extensions
WHERE name IN ('vector', 'uuid-ossp')
ORDER BY name;
