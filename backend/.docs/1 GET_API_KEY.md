# 🔑 How to Get Your Supabase Anon Key

## Steps:

1. **Go to your Supabase Project Settings:**

   ```
   https://supabase.com/dashboard/project/nkuzhhpjdahuiuysemzg/settings/api
   ```

2. **Find the "Project API keys" section**

3. **Copy the `anon` / `public` key** (NOT the `service_role` key)

   - ✅ The **anon key** starts with: `eyJ...` (it's a long JWT token)
   - ❌ Don't use the service*role key (starts with `sbp*...`)

4. **Paste it in your `.env` file:**
   ```
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3M...
   ```

## Why anon key?

- ✅ **Safe for client-side use**
- ✅ **Respects Row Level Security (RLS)**
- ✅ **Recommended for most applications**

## Screenshot Reference:

Look for the section that says:

```
anon public
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Copy the entire long string!

---

**After updating `.env`, run again:**

```bash
python db_crud.py
```
