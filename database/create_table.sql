-- ===================================================
-- Create the 'notes' table for CRUD testing
-- ===================================================

-- Create the table
CREATE TABLE notes (
  id BIGSERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  content TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security (RLS)
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;

-- Create a policy to allow all operations (for testing)
-- WARNING: In production, you should have more restrictive policies!
CREATE POLICY "Allow all operations for testing" ON notes
FOR ALL 
USING (true)
WITH CHECK (true);

-- Verify the table was created
SELECT * FROM notes;
