# Quick Setup Instructions

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

## 2. Configure .env file

Edit `.env` and add your Supabase credentials:

- Get your project URL and anon key from: https://supabase.com/dashboard/project/nkuzhhpjdahuiuysemzg/settings/api-keys

## 3. Create a test table in Supabase

Run this SQL in Supabase SQL Editor:

```sql
CREATE TABLE notes (
  id BIGSERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  content TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Optional: Enable RLS (Row Level Security)
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;

-- Allow all operations for testing (adjust for production)
CREATE POLICY "Allow all operations" ON notes
FOR ALL USING (true);
```

## 4. Run the test

```bash
python db_crud.py
```

## Connection Method Used

✅ **Supabase Python Client Library** - Best for your use case because:

- Simple and clean API
- Handles authentication automatically
- Perfect for persistent applications
- No need to manage connection strings or pooling
- Works with both IPv4 and IPv6
