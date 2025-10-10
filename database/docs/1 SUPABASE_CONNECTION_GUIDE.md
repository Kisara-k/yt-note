# Supabase Database Connection Guide

## Overview

Supabase provides multiple methods to connect to your Postgres database. The best method depends on your use case, whether you're working on the frontend, backend, or utilizing serverless functions.

---

## Connection Methods Comparison

| Method                           | Best For              | IPv4/IPv6 Support | Use Case                                   |
| -------------------------------- | --------------------- | ----------------- | ------------------------------------------ |
| **Data API (REST/GraphQL)**      | Frontend applications | Both              | Web/mobile apps with RLS enabled           |
| **Client Libraries**             | Frontend/backend      | Both              | Developer-friendly interface with auth     |
| **Direct Connection**            | Persistent servers    | IPv6 only\*       | VMs, long-running containers               |
| **Session Mode (Supavisor)**     | Persistent backends   | Both              | Apps requiring IPv4 support                |
| **Transaction Mode (Supavisor)** | Serverless functions  | Both              | Edge/serverless with transient connections |
| **Dedicated Pooler (PgBouncer)** | High-performance apps | IPv6 only\*       | Paid tier, best performance                |

\* _IPv4 support available with IPv4 add-on_

---

## 1. Data APIs & Client Libraries (Recommended for Frontend)

### When to Use:

- **Frontend applications** (web, mobile)
- Need Row Level Security (RLS)
- Want built-in authentication handling
- REST or GraphQL queries

### Available Client Libraries:

- **Python**: `supabase-py`
- **JavaScript/TypeScript**: `@supabase/supabase-js`
- **Flutter/Dart**
- **Swift** (iOS)
- **C#**
- **Kotlin** (Android)

### Python Example:

```python
from supabase import create_client

# Initialize client
supabase = create_client(
    "https://your-project.supabase.co",
    "your-anon-key"
)

# Query data (with RLS)
response = supabase.table("notes").select("*").execute()
```

### Pros:

✅ Easy to use  
✅ Built-in authentication  
✅ Automatic RLS enforcement  
✅ Works from browsers

### Cons:

❌ Limited to CRUD operations  
❌ Cannot run custom SQL  
❌ Requires RLS policies

---

## 2. Direct Connection (Best for Persistent Servers)

### When to Use:

- **Persistent servers** (VMs, EC2, long-running containers)
- Direct access to Postgres features
- IPv6-supported environments

### Connection String:

```
postgresql://postgres:[PASSWORD]@db.project.supabase.co:5432/postgres
```

### Python Example (psycopg2):

```python
import psycopg2

conn = psycopg2.connect(
    host="db.project.supabase.co",
    port=5432,
    database="postgres",
    user="postgres",
    password="your-password"
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM notes")
results = cursor.fetchall()
```

### Pros:

✅ Full Postgres features  
✅ Best for long-lived connections  
✅ No pooler overhead

### Cons:

❌ **IPv6 only** (unless you have IPv4 add-on)  
❌ Connection limits per database size  
❌ Must manage connections carefully

---

## 3. Supavisor Session Mode (Best for IPv4 Support)

### When to Use:

- Persistent backend services
- **Need IPv4 support**
- Don't have IPv6 available

### Connection String:

```
postgres://postgres.project:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres
```

### Python Example:

```python
import psycopg2

conn = psycopg2.connect(
    host="aws-0-us-east-1.pooler.supabase.com",
    port=5432,
    database="postgres",
    user="postgres.project",
    password="your-password"
)
```

### Pros:

✅ IPv4 and IPv6 support  
✅ Free (shared pooler)  
✅ Good for persistent connections

### Cons:

❌ Slightly higher latency than direct  
❌ Shared resources (free tier)

---

## 4. Supavisor Transaction Mode (Best for Serverless)

### When to Use:

- **Serverless functions** (AWS Lambda, Vercel, Netlify)
- **Edge functions**
- Short-lived, transient connections
- Auto-scaling systems

### Connection String:

```
postgres://postgres.project:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

### Python Example (with connection pooling):

```python
import psycopg2
from psycopg2 import pool

# Create connection pool
connection_pool = pool.SimpleConnectionPool(
    1, 10,  # min and max connections
    host="aws-0-us-east-1.pooler.supabase.com",
    port=6543,  # Note: transaction mode port
    database="postgres",
    user="postgres.project",
    password="your-password"
)

def lambda_handler(event, context):
    conn = connection_pool.getconn()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notes")
        results = cursor.fetchall()
        return {"statusCode": 200, "body": results}
    finally:
        connection_pool.putconn(conn)
```

### ⚠️ Important Limitations:

- **Does NOT support prepared statements** - disable them in your library
- Connection is transaction-scoped (closed after transaction)

### Pros:

✅ Perfect for serverless  
✅ Handles many transient connections  
✅ IPv4 and IPv6 support  
✅ Free (shared pooler)

### Cons:

❌ **No prepared statements**  
❌ Not for long-lived connections  
❌ Slightly higher latency

---

## 5. Dedicated Pooler (Best Performance - Paid)

### When to Use:

- **High-performance applications** (paid tier only)
- Need best latency and performance
- Have IPv6 or IPv4 add-on

### Connection String:

```
# Get from dashboard - co-located with your database
```

### Pros:

✅ Best performance and latency  
✅ Dedicated resources  
✅ Co-located with database

### Cons:

❌ **Paid tier only**  
❌ Uses more compute resources  
❌ IPv6 required (or IPv4 add-on)

---

## Which Connection Method Should You Use?

### Decision Flow:

```
START
  ↓
  ├─ Frontend app?
  │   → YES → Use **Client Libraries** (supabase-py, supabase-js)
  │
  ├─ Backend persistent server?
  │   ├─ Have IPv6?
  │   │   → YES → Use **Direct Connection**
  │   │   → NO  → Use **Session Mode (Supavisor)**
  │
  ├─ Serverless/Edge functions?
  │   → Use **Transaction Mode (Supavisor)**
  │
  ├─ Need best performance? (Paid)
  │   → Use **Dedicated Pooler (PgBouncer)**
```

---

## Common Configuration Examples

### For your `db_crud.py` (Persistent Backend)

**Option 1: Using Client Library (Recommended)**

```python
from supabase import create_client
import os

# Best for most applications
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Simple CRUD operations
data = supabase.table("notes").select("*").execute()
```

**Option 2: Direct Connection (If you need raw SQL)**

```python
import psycopg2
import os

# For custom SQL queries
conn = psycopg2.connect(
    host="db.project.supabase.co",
    port=5432,
    database="postgres",
    user="postgres",
    password=os.getenv("DB_PASSWORD")
)
```

**Option 3: Session Mode (If no IPv6)**

```python
import psycopg2
import os

# For IPv4 support
conn = psycopg2.connect(
    host="aws-0-us-east-1.pooler.supabase.com",
    port=5432,
    database="postgres",
    user="postgres.project",
    password=os.getenv("DB_PASSWORD")
)
```

---

## Connection Limits & Best Practices

### Connection Limits by Compute Size:

- **Free tier**: 60 connections max
- **Micro**: 60 connections
- **Small**: 90 connections
- **Medium**: 120 connections
- **Large**: 160 connections
- **XL**: 240 connections
- **2XL+**: 380+ connections

### Best Practices:

1. **Use connection pooling** for persistent backends
2. **Close connections** when done
3. **Use transaction mode** for serverless
4. **Enable RLS** when using Data APIs
5. **Use environment variables** for credentials
6. **Monitor connection usage** in Supabase dashboard

### Monitor Connections:

```sql
-- Check active connections
SELECT
  count(usename),
  application_name,
  usename
FROM pg_stat_activity
GROUP BY usename, application_name;
```

---

## Security Considerations

### SSL Connections:

Always use SSL in production:

```python
import psycopg2

conn = psycopg2.connect(
    host="db.project.supabase.co",
    port=5432,
    database="postgres",
    user="postgres",
    password="your-password",
    sslmode="require"  # Enforce SSL
)
```

### Row Level Security (RLS):

- **Required** for Data API/client libraries
- Protects data at the row level
- Configure in Supabase dashboard

---

## Troubleshooting

### "Connection Refused" Error

- ✅ Check project is running
- ✅ Verify connection string
- ✅ Check firewall settings

### "Password Authentication Failed"

- ✅ Double-check password
- ✅ Reset password in dashboard if needed

### "Too Many Connections"

- ✅ Use connection pooling
- ✅ Close unused connections
- ✅ Use transaction mode for serverless
- ✅ Upgrade compute tier if needed

### IPv4 Issues

- ✅ Use Session/Transaction mode (supports IPv4)
- ✅ Or get IPv4 add-on for direct connection

---

## Quick Reference

### Get Your Connection Strings:

1. Go to your Supabase project dashboard
2. Click the **"Connect"** button at the top
3. Choose your connection method
4. Copy the appropriate connection string

### Recommended Setup for Different Scenarios:

| Scenario                      | Use This                                          |
| ----------------------------- | ------------------------------------------------- |
| React/Vue/Angular app         | Client Library (supabase-js)                      |
| Python web app (Django/Flask) | Client Library (supabase-py) OR Direct Connection |
| AWS Lambda function           | Transaction Mode (port 6543)                      |
| Vercel/Netlify function       | Transaction Mode (port 6543)                      |
| Docker container (persistent) | Direct Connection OR Session Mode                 |
| Database migration scripts    | Direct Connection                                 |
| Data analysis/ETL             | Direct Connection                                 |

---

## Summary

**For most Python applications like your `yt-note` project:**

### ✨ Recommended: Use the **Supabase Python Client Library**

```bash
pip install supabase
```

```python
from supabase import create_client

supabase = create_client(
    "https://your-project.supabase.co",
    "your-anon-key"
)

# Easy CRUD operations
response = supabase.table("notes").select("*").execute()
```

**Why?**

- ✅ Easiest to use
- ✅ Handles authentication automatically
- ✅ Built-in RLS support
- ✅ Works with both IPv4 and IPv6
- ✅ Perfect for most CRUD applications

---

## Additional Resources

- [Supabase Python Docs](https://supabase.com/docs/reference/python)
- [Connection Management Guide](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [Supabase Dashboard](https://supabase.com/dashboard)

---

_Last Updated: October 2025_
