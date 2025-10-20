-- Add viewed_at column to processing_jobs table
-- This allows tracking when a user has viewed/acknowledged a completed job

ALTER TABLE processing_jobs
ADD COLUMN IF NOT EXISTS viewed_at TIMESTAMP WITH TIME ZONE;

-- Create index for better query performance
CREATE INDEX IF NOT EXISTS idx_processing_jobs_viewed_at
ON processing_jobs(viewed_at);

-- Create index for unread jobs query
CREATE INDEX IF NOT EXISTS idx_processing_jobs_user_status_viewed
ON processing_jobs(user_id, status, viewed_at);
