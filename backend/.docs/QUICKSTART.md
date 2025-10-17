# YouTube Notes Backend - Quick Reference

## Structure

```
youtube/      → Video metadata from YouTube API
subtitles/    → Subtitle extraction & chunking
openai/       → AI enrichment (parallel)
orchestrator  → Coordinates all modules
api.py        → FastAPI routes
```

## Start Server

```bash
python main.py
# or
uvicorn api:app --reload
```

## Test

```bash
python test_complete.py    # Full suite
python test_e2e.py          # Database integration
```

## Configuration

Edit `config.py` for chunk sizes, AI settings

## Database

If you see schema errors, run SQL from `db/SCHEMA_UPDATE_NEEDED.md`

## API Docs

http://localhost:8000/docs

---

See `README.md` for full documentation  
See `STATUS.md` for project status
