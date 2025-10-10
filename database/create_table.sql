-- ===================================================
-- Create the 'notes' table for CRUD testing
-- ===================================================

-- Create the table
CREATE TABLE IF NOT EXISTS notes (
  id BIGSERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  content TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security (RLS)
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;

-- Drop existing policy if it exists
DROP POLICY IF EXISTS "Allow all operations for testing" ON notes;

-- Create a policy to allow all operations (for testing)
-- WARNING: In production, you should have more restrictive policies!
CREATE POLICY "Allow all operations for testing" ON notes
FOR ALL 
USING (true)
WITH CHECK (true);
