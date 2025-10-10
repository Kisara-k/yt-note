# 🗄️ Create Database Table

## Quick Steps:

### 1. Open Supabase SQL Editor

Go to: https://supabase.com/dashboard/project/nkuzhhpjdahuiuysemzg/editor

### 2. Copy and Paste this SQL:

```sql
-- Create the notes table
CREATE TABLE notes (
  id BIGSERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  content TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security (RLS)
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;

-- Allow all operations (for testing purposes)
CREATE POLICY "Allow all operations for testing" ON notes
FOR ALL
USING (true)
WITH CHECK (true);
```

### 3. Click "Run" or press `Ctrl+Enter`

### 4. Verify the table was created:

- Go to Table Editor: https://supabase.com/dashboard/project/nkuzhhpjdahuiuysemzg/editor
- You should see the `notes` table in the sidebar

### 5. Run your test again:

```bash
python db_crud.py
```

---

## Alternative: Use the SQL file

I've also created `create_table.sql` - you can:

1. Open the SQL Editor
2. Copy the contents from `create_table.sql`
3. Paste and run it

---

✅ **Once the table is created, your CRUD operations will work!**
