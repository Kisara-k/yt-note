# YouTube Notes Backend# YouTube Notes Backend# YouTube Notes Backend# YouTube Notes Backend# YouTube Notes Backend# Backend - YouTube Video Fetcher

Clean modular architecture for processing YouTube videos with AI-powered subtitle analysis.

## ArchitectureClean modular architecture for processing YouTube videos with AI-powered subtitle analysis.Clean modular architecture for processing YouTube videos with AI-powered subtitle analysis.Clean modular architecture for processing YouTube videos with AI-powered subtitle analysis.Clean modular architecture for processing YouTube videos with AI-powered subtitle analysis.This backend module fetches YouTube video details using the YouTube Data API v3 and stores them in a Supabase (PostgreSQL) database.

```````````````

backend/

├── youtube/           # Video metadata from YouTube API## Architecture## Architecture## Architecture## Architecture## Features

├── subtitles/         # Subtitle extraction & chunking

├── openai/            # AI enrichment (parallel)

├── auth/              # User authentication

├── db/                # Database operations``````````````- ✅ Fetch video details from YouTube Data API v3

├── orchestrator.py    # Module coordination

├── api.py             # FastAPI routesbackend/

├── config.py          # Configuration

└── prompts.py         # AI prompts├── youtube/           # Video metadata from YouTube APIbackend/

```````````````

├── subtitles/ # Subtitle extraction & chunking

**Key Principles:**

- No cross-module imports - modules are independent├── openai/ # AI enrichment (parallel)├── youtube/ # Video metadata from YouTube APIbackend/

- Orchestrator coordinates everything

- Parallel processing for AI enrichment├── auth/ # User authentication

- All data persisted to Supabase PostgreSQL

├── db/ # Database operations├── subtitles/ # Subtitle extraction & chunking

---

├── orchestrator.py # Module coordination

## Module Inputs & Outputs

├── api.py # FastAPI routes├── openai/ # AI enrichment (parallel)├── youtube/ # Video metadata from YouTube APIbackend/- ✅ Batch processing (up to 50 videos per API call)

### `backend/youtube/metadata.py`

├── config.py # Configuration

**Input:**

- Single video ID (string) OR multiple video IDs (list, up to 50)└── prompts.py # AI prompts├── auth/ # User authentication

- Optional: API key (defaults to env variable)

````

**Output:**

- Dictionary (or list of dictionaries) containing video metadata:├── db/                # Database operations├── subtitles/         # Subtitle extraction & chunking

  - `video_id`, `title`, `channel_title`, `channel_id`

  - `published_at`, `description`, `duration`**Key Principles:**

  - `view_count`, `like_count`, `thumbnail_url`

- No cross-module imports - modules are independent├── orchestrator.py    # Module coordination

**Functions:**

```python- Orchestrator coordinates everything

extract_video_id(url: str) -> str

fetch_video_metadata(video_id: str, api_key: str = None) -> Dict- Parallel processing for AI enrichment├── api.py             # FastAPI routes├── openai/            # AI enrichment (parallel)├── youtube/           # Video metadata from YouTube API- ✅ Extract video IDs from various YouTube URL formats

fetch_batch_metadata(video_ids: List[str], api_key: str = None) -> List[Dict]

```- All data persisted to Supabase PostgreSQL



---├── config.py          # Configuration



### `backend/subtitles/extractor.py`---



**Input:**└── prompts.py         # AI prompts├── auth/              # User authentication

- YouTube video ID (string)

- Optional: chunking parameters (target_words, max_words, overlap_words, min_final_words)## Module Inputs & Outputs



**Output:**```

- List of chunk dictionaries, each containing:

  - `text` (string): The subtitle text### `backend/youtube/metadata.py`

  - `word_count` (int): Number of words

  - `sentence_count` (int): Number of sentences├── db/                # Database operations├── subtitles/         # Subtitle extraction & chunking- ✅ Store video data in PostgreSQL with proper schema



**Functions:****Input:**

```python

extract_and_chunk_subtitles(- Single video ID (string) OR multiple video IDs (list, up to 50)**Key Principles:**

    video_id: str,

    target_words: int = 1000,- Optional: API key (defaults to env variable)

    max_words: int = 1500,

    overlap_words: int = 100,- No cross-module imports - modules are independent├── orchestrator.py    # Module coordination

    min_final_words: int = 500

) -> List[Dict]**Output:**

````

- Dictionary (or list of dictionaries) containing video metadata:- Orchestrator coordinates everything

**Example:**

```python  - `video_id`, `title`, `channel_title`, `channel_id`

chunks = extract_and_chunk_subtitles("dQw4w9WgXcQ")

# Returns: [ - `published_at`, `description`, `duration`- Parallel processing for AI enrichment├── api.py # FastAPI routes├── openai/ # AI enrichment (parallel)- ✅ Automatic timestamp tracking (created_at, updated_at)

# {'text': '...', 'word_count': 1050, 'sentence_count': 28},

# {'text': '...', 'word_count': 980, 'sentence_count': 25} - `view_count`, `like_count`, `thumbnail_url`

# ]

`````- All data persisted to Supabase PostgreSQL



---**Functions:**



### `backend/openai/enrichment.py````python├── config.py          # Configuration



**Input:**extract_video_id(url: str) -> str

- Subtitle chunk text (string) - **REQUIRED**

- Prompts dictionary (from `prompts.py`) - **REQUIRED**fetch_video_metadata(video_id: str, api_key: str = None) -> Dict---

- Optional: model, temperature, max_tokens, retry settings

fetch_batch_metadata(video_ids: List[str], api_key: str = None) -> List[Dict]

**Output:**

- Dictionary containing AI-generated fields:```└── prompts.py         # AI prompts├── auth/              # User authentication- ✅ Upsert support (update existing videos or create new ones)

  - `title` (string): Short title for the chunk

  - `field_1` (string): First AI field (e.g., summary)

  - `field_2` (string): Second AI field (e.g., key points)

  - `field_3` (string): Third AI field (e.g., topics/themes)---## Module Inputs & Outputs



**Functions:**

```python

enrich_chunk(### `backend/subtitles/extractor.py````

    text: str,                    # REQUIRED: subtitle chunk text

    prompts: Dict[str, str],      # REQUIRED: prompt templates

    model: str = "gpt-4o-mini",

    temperature: float = 0.5,**Input:**### `backend/youtube/metadata.py`

    max_tokens_title: int = 50,

    max_tokens_other: int = 200- YouTube video ID (string)

) -> Dict[str, str]

- Optional: chunking parameters (target_words, max_words, overlap_words, min_final_words)├── db/                # Database operations- ✅ PostgreSQL array support for tags

enrich_chunks_parallel(

    chunks: list,                 # List of chunk dicts with 'text' field

    prompts: Dict[str, str],      # REQUIRED: prompt templates

    max_workers: int = 5**Output:****Input:**

) -> list

```- List of chunk dictionaries, each containing:



**Example:**  - `text` (string): The subtitle text- Single video ID (string) OR multiple video IDs (list, up to 50)**Key Principles:**

```python

from prompts import PROMPTS  - `word_count` (int): Number of words



result = enrich_chunk(  - `sentence_count` (int): Number of sentences- Optional: API key (defaults to env variable)

    text="We're no strangers to love...",

    prompts={

        'title': PROMPTS['short_title']['template'],

        'field_1': PROMPTS['ai_field_1']['template'],**Functions:**- No cross-module imports - modules are independent├── orchestrator.py    # Module coordination- ✅ JSONB support for complex nested objects (thumbnails, localized content)

        'field_2': PROMPTS['ai_field_2']['template'],

        'field_3': PROMPTS['ai_field_3']['template']```python

    }

)extract_and_chunk_subtitles(**Output:**

# Returns: {

#   'title': 'Rick Astley Music Video',    video_id: str,

#   'field_1': 'A summary of the lyrics...',

#   'field_2': '• Key point 1\n• Key point 2...',    target_words: int = 1000,- Dictionary (or list of dictionaries) containing video metadata:- Orchestrator coordinates everything

#   'field_3': 'Music, Love, Relationships'

# }    max_words: int = 1500,

`````

    overlap_words: int = 100,  - `video_id`, `title`, `channel_title`, `channel_id`

---

    min_final_words: int = 500

### `backend/orchestrator.py`

) -> List[Dict] - `published_at`, `description`, `duration`- Parallel processing for AI enrichment├── api.py # FastAPI routes

Coordinates all modules and handles database operations.

````

**Functions:**

```python  - `view_count`, `like_count`, `thumbnail_url`

# Fetch metadata and save to DB

process_video_metadata(url_or_id: str) -> Dict**Example:**



# Extract subtitles, chunk, and save to DB```python- All data persisted to Supabase PostgreSQL

process_video_subtitles(video_id: str) -> List[Dict]

chunks = extract_and_chunk_subtitles("dQw4w9WgXcQ")

# Enrich chunks with AI in parallel

process_chunks_enrichment_parallel(chunks: list) -> list# Returns: [**Functions:**



# Full pipeline: metadata → subtitles → chunks → AI → DB#   {'text': '...', 'word_count': 1050, 'sentence_count': 28},

process_full_video(url_or_id: str, save_to_db: bool = True) -> Dict

```#   {'text': '...', 'word_count': 980, 'sentence_count': 25}```python├── config.py          # Configuration## Setup



**Example:**# ]

```python

from orchestrator import process_full_video```extract_video_id(url: str) -> str



# Complete pipeline

result = process_full_video("dQw4w9WgXcQ")

# Returns: {---fetch_video_metadata(video_id: str, api_key: str = None) -> Dict## Module Inputs & Outputs

#   'video_id': 'dQw4w9WgXcQ',

#   'metadata': {...},

#   'chunks': [{...}, {...}],

#   'enriched_chunks': [{...}, {...}]### `backend/openai/enrichment.py`fetch_batch_metadata(video_ids: List[str], api_key: str = None) -> List[Dict]

# }

````

---**Input:**```└── prompts.py # AI prompts

## Quick Start- Subtitle chunk text (string) - **REQUIRED**

```bash- Prompts dictionary (from `prompts.py`) - **REQUIRED**

# Install dependencies

pip install -r requirements.txt- Optional: model, temperature, max_tokens, retry settings

# Configure environment (.env file)---### `backend/youtube/metadata.py`

YOUTUBE_API_KEY=your_youtube_api_key

OPENAI_API_KEY=your_openai_api_key**Output:**

SUPABASE_URL=your_supabase_url

SUPABASE_KEY=your_supabase_key- Dictionary containing AI-generated fields:

# Setup database - `title` (string): Short title for the chunk

cd db

python create_table.py - `field_1` (string): First AI field (e.g., summary)### `backend/subtitles/extractor.py````### 1. Install Dependencies

# Run server - `field_2` (string): Second AI field (e.g., key points)

cd ..

python main.py - `field_3` (string): Third AI field (e.g., topics/themes)

````



**API Documentation:** http://localhost:8000/docs

**Functions:****Input:****Input:**

---

```python

## Testing

enrich_chunk(- YouTube video ID (string)

```bash

python test_complete.py    # Full suite (6/6 tests)    text: str,                    # REQUIRED: subtitle chunk text

python test_e2e.py         # End-to-end with DB (5/5 tests)

```    prompts: Dict[str, str],      # REQUIRED: prompt templates- Optional: chunking parameters (target_words, max_words, overlap_words, min_final_words)- Single video ID (string) OR multiple video IDs (list, up to 50)



---    model: str = "gpt-4o-mini",



## Usage Examples    temperature: float = 0.5,



### Process a Single Video    max_tokens_title: int = 50,



```python    max_tokens_other: int = 200**Output:**- Optional: API key (defaults to env variable)

from orchestrator import process_full_video

) -> Dict[str, str]

# Full pipeline with DB save

result = process_full_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")- List of chunk dictionaries, each containing:



# Process without DB save (for testing)enrich_chunks_parallel(

result = process_full_video("dQw4w9WgXcQ", save_to_db=False)

```    chunks: list,                 # List of chunk dicts with 'text' field  - `text` (string): The subtitle text**Key Principles:**```bash



### Fetch Metadata Only    prompts: Dict[str, str],      # REQUIRED: prompt templates



```python    max_workers: int = 5  - `word_count` (int): Number of words

from youtube.metadata import fetch_video_metadata

) -> list

metadata = fetch_video_metadata("dQw4w9WgXcQ")

print(metadata['title'])```  - `sentence_count` (int): Number of sentences**Output:**

print(metadata['view_count'])

````

### Extract Subtitles Only**Example:**

`python`python

from subtitles.extractor import extract_and_chunk_subtitles

from prompts import PROMPTS**Functions:**- Dictionary (or list of dictionaries) containing video metadata:- No cross-module imports - modules are independentcd backend/db

chunks = extract_and_chunk_subtitles("dQw4w9WgXcQ")

for i, chunk in enumerate(chunks):

    print(f"Chunk {i}: {chunk['word_count']} words")

`result = enrich_chunk(`python

### Enrich Chunks with AI text="We're no strangers to love...",

```python    prompts={extract_and_chunk_subtitles(  - `video_id`, `title`, `channel_title`, `channel_id`

from openai.enrichment import enrich_chunks_parallel

from prompts import PROMPTS 'title': PROMPTS['short_title']['template'],

from config import OPENAI_MODEL, OPENAI_TEMPERATURE

        'field_1': PROMPTS['ai_field_1']['template'],    video_id: str,

# Prepare prompts

prompt_dict = { 'field_2': PROMPTS['ai_field_2']['template'],

    'title': PROMPTS['short_title']['template'],

    'field_1': PROMPTS['ai_field_1']['template'],        'field_3': PROMPTS['ai_field_3']['template']    target_words: int = 1000,  - `published_at`, `description`, `duration`- Orchestrator coordinates everythingpip install -r requirements.txt

    'field_2': PROMPTS['ai_field_2']['template'],

    'field_3': PROMPTS['ai_field_3']['template']    }

}

) max_words: int = 1500,

# Enrich in parallel (5 workers by default)

enriched = enrich_chunks_parallel(# Returns: {

    chunks=chunks,

    prompts=prompt_dict,#   'title': 'Rick Astley Music Video',    overlap_words: int = 100,  - `view_count`, `like_count`, `thumbnail_url`

    model=OPENAI_MODEL,

    temperature=OPENAI_TEMPERATURE#   'field_1': 'A summary of the lyrics...',

)

```````# 'field_2': '• Key point 1\n• Key point 2...',    min_final_words: int = 500



---#   'field_3': 'Music, Love, Relationships'



## Configuration# }) -> List[Dict]- Parallel processing for AI enrichment```



Edit `config.py` to customize:```



```python```

# Chunking (word-based)

CHUNK_TARGET_WORDS = 1000      # Target words per chunk---

CHUNK_MAX_WORDS = 1500         # Maximum words per chunk

CHUNK_OVERLAP_WORDS = 100      # Overlap between chunks**Functions:**

CHUNK_MIN_FINAL_WORDS = 500    # Min words for final chunk

### `backend/orchestrator.py`

# OpenAI

OPENAI_MODEL = "gpt-4o-mini"**Example:**

OPENAI_TEMPERATURE = 0.5

OPENAI_MAX_TOKENS_TITLE = 50Coordinates all modules and handles database operations.

OPENAI_MAX_TOKENS_OTHER = 200

``````python```python- All data persisted to Supabase PostgreSQL



---**Functions:**



## API Endpoints```pythonchunks = extract_and_chunk_subtitles("dQw4w9WgXcQ")



All endpoints maintain 100% frontend compatibility:# Fetch metadata and save to DB



```process_video_metadata(url_or_id: str) -> Dict# Returns: [extract_video_id(url: str) -> str

POST   /api/video              # Fetch video metadata

POST   /api/note               # Create/update note

GET    /api/chunks/{video_id}  # Get chunks for video

POST   /api/jobs/process-video # Full pipeline processing# Extract subtitles, chunk, and save to DB#   {'text': '...', 'word_count': 1050, 'sentence_count': 28},

```````

process_video_subtitles(video_id: str) -> List[Dict]

---

# {'text': '...', 'word_count': 980, 'sentence_count': 25}fetch_video_metadata(video_id: str, api_key: str = None) -> Dict### 2. Set Up Environment Variables

## Database Schema

# Enrich chunks with AI in parallel

### Tables

- `youtube_videos` - Video metadataprocess_chunks_enrichment_parallel(chunks: list) -> list# ]

- `subtitle_chunks` - Chunked subtitles with AI enrichment

- `video_notes` - User notes for videos

- `job_queue` - Background job processing

# Full pipeline: metadata → subtitles → chunks → AI → DB```fetch_batch_metadata(video_ids: List[str], api_key: str = None) -> List[Dict]

### Key Features

- Word-based chunks (not time-based)process_full_video(url_or_id: str, save_to_db: bool = True) -> Dict

- Automatic timestamps (created_at, updated_at)

- Full CRUD operations```

- Upsert support

---

**Example:**---```## Quick Start

## Features

`````python

✅ Modular architecture (no cross-imports)

✅ YouTube Data API v3 integration  from orchestrator import process_full_video

✅ Subtitle extraction via yt-dlp

✅ Word-based chunking (configurable)

✅ Parallel AI enrichment (5x faster)

✅ Supabase PostgreSQL integration  # Complete pipeline### `backend/openai/enrichment.py`

✅ FastAPI REST endpoints

✅ Comprehensive test suite (11/11 passing)  result = process_full_video("dQw4w9WgXcQ")

✅ 100% frontend compatible

# Returns: {

---

#   'video_id': 'dQw4w9WgXcQ',

## Documentation

#   'metadata': {...},**Input:**---Create a `.env` file in the root directory with:

- `README.md` - This file (setup & module reference)

- `STATUS.md` - Current project status#   'chunks': [{...}, {...}],

- `QUICKSTART.md` - Quick command reference

- `REFACTORING_COMPLETE.md` - Refactoring summary#   'enriched_chunks': [{...}, {...}]- Subtitle chunk text (string) - **REQUIRED**



---# }



## Troubleshooting```- Prompts dictionary (from `prompts.py`) - **REQUIRED**



### "YOUTUBE_API_KEY not found"

Create `.env` file with your API key.

---- Optional: model, temperature, max_tokens, retry settings

### "Table does not exist"

Run `python db/create_table.py` to create tables.



### "OPENAI_API_KEY not found"## Quick Start### `backend/subtitles/extractor.py````bash

Add OpenAI API key to `.env` file.



### Tests failing

Make sure all environment variables are set and database is accessible.```bash**Output:**



---# Install dependencies



## Production Ready ✅pip install -r requirements.txt- Dictionary containing AI-generated fields:



- ✅ All tests passing (11/11)

- ✅ Database integration verified

- ✅ API endpoints working# Configure environment (.env file)  - `title` (string): Short title for the chunk

- ✅ Frontend compatible

- ✅ Error handling implementedYOUTUBE_API_KEY=your_youtube_api_key

- ✅ Documentation complete

OPENAI_API_KEY=your_openai_api_key  - `field_1` (string): First AI field (e.g., summary)**Input:**# Install```env

SUPABASE_URL=your_supabase_url

SUPABASE_KEY=your_supabase_key  - `field_2` (string): Second AI field (e.g., key points)



# Setup database  - `field_3` (string): Third AI field (e.g., topics/themes)- YouTube video ID (string)

cd db

python create_table.py



# Run server**Functions:**- Optional: chunking parameters (target_words, max_words, overlap_words, min_final_words)pip install -r requirements.txt# YouTube API

cd ..

python main.py```python

`````

enrich_chunk(

**API Documentation:** http://localhost:8000/docs

    text: str,                    # REQUIRED: subtitle chunk text

---

    prompts: Dict[str, str],      # REQUIRED: prompt templates**Output:**YOUTUBE_API_KEY=your_youtube_api_key_here

## Testing

    model: str = "gpt-4o-mini",

````bash

python test_complete.py    # Full suite (6/6 tests)    temperature: float = 0.5,- List of chunk dictionaries, each containing:

python test_e2e.py         # End-to-end with DB (5/5 tests)

```    max_tokens_title: int = 50,



---    max_tokens_other: int = 200  - `text` (string): The subtitle text# Configure .env



## Usage Examples) -> Dict[str, str]



### Process a Single Video  - `word_count` (int): Number of words



```pythonenrich_chunks_parallel(

from orchestrator import process_full_video

    chunks: list,                 # List of chunk dicts with 'text' field  - `sentence_count` (int): Number of sentencesYOUTUBE_API_KEY=...# Supabase

# Full pipeline with DB save

result = process_full_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")    prompts: Dict[str, str],      # REQUIRED: prompt templates



# Process without DB save (for testing)    max_workers: int = 5

result = process_full_video("dQw4w9WgXcQ", save_to_db=False)

```) -> list



### Fetch Metadata Only```**Functions:**OPENAI_API_KEY=...SUPABASE_URL=your_supabase_url



```python

from youtube.metadata import fetch_video_metadata

**Example:**```python

metadata = fetch_video_metadata("dQw4w9WgXcQ")

print(metadata['title'])```python

print(metadata['view_count'])

```from prompts import PROMPTSextract_and_chunk_subtitles(SUPABASE_URL=...SUPABASE_KEY=your_supabase_anon_key



### Extract Subtitles Only



```pythonresult = enrich_chunk(    video_id: str,

from subtitles.extractor import extract_and_chunk_subtitles

    text="We're no strangers to love...",

chunks = extract_and_chunk_subtitles("dQw4w9WgXcQ")

for i, chunk in enumerate(chunks):    prompts={    target_words: int = 1000,SUPABASE_KEY=...

    print(f"Chunk {i}: {chunk['word_count']} words")

```        'title': PROMPTS['short_title']['template'],



### Enrich Chunks with AI        'field_1': PROMPTS['ai_field_1']['template'],    max_words: int = 1500,



```python        'field_2': PROMPTS['ai_field_2']['template'],

from openai.enrichment import enrich_chunks_parallel

from prompts import PROMPTS        'field_3': PROMPTS['ai_field_3']['template']    overlap_words: int = 100,# Database (for direct psycopg2 connection)

from config import OPENAI_MODEL, OPENAI_TEMPERATURE

    }

# Prepare prompts

prompt_dict = {)    min_final_words: int = 500

    'title': PROMPTS['short_title']['template'],

    'field_1': PROMPTS['ai_field_1']['template'],# Returns: {

    'field_2': PROMPTS['ai_field_2']['template'],

    'field_3': PROMPTS['ai_field_3']['template']#   'title': 'Rick Astley Music Video',) -> List[Dict]# Setup databaseDB_PASSWORD=your_db_password

}

#   'field_1': 'A summary of the lyrics...',

# Enrich in parallel (5 workers by default)

enriched = enrich_chunks_parallel(#   'field_2': '• Key point 1\n• Key point 2...',```

    chunks=chunks,

    prompts=prompt_dict,#   'field_3': 'Music, Love, Relationships'

    model=OPENAI_MODEL,

    temperature=OPENAI_TEMPERATURE# }cd db```

)

````

---**Example:**

## Configuration---

Edit `config.py` to customize:```pythonpsql -U user -d db -f create_table.sql

```python### `backend/orchestrator.py`

# Chunking (word-based)

CHUNK_TARGET_WORDS = 1000 # Target words per chunkchunks = extract_and_chunk_subtitles("dQw4w9WgXcQ")

CHUNK_MAX_WORDS = 1500 # Maximum words per chunk

CHUNK_OVERLAP_WORDS = 100 # Overlap between chunksCoordinates all modules and handles database operations.

CHUNK_MIN_FINAL_WORDS = 500 # Min words for final chunk

# Returns: [psql -U user -d db -f schema_updates.sql### 3. Create Database Tables

# OpenAI

OPENAI_MODEL = "gpt-4o-mini"**Functions:**

OPENAI_TEMPERATURE = 0.5

OPENAI_MAX_TOKENS_TITLE = 50```python# {'text': '...', 'word_count': 1050, 'sentence_count': 28},

OPENAI_MAX_TOKENS_OTHER = 200

````# Fetch metadata and save to DB



---process_video_metadata(url_or_id: str) -> Dict#   {'text': '...', 'word_count': 980, 'sentence_count': 25}



## API Endpoints



All endpoints maintain 100% frontend compatibility:# Extract subtitles, chunk, and save to DB# ]



```process_video_subtitles(video_id: str) -> List[Dict]

POST   /api/video              # Fetch video metadata

POST   /api/note               # Create/update note```# RunRun the table creation script:

GET    /api/chunks/{video_id}  # Get chunks for video

POST   /api/jobs/process-video # Full pipeline processing# Enrich chunks with AI in parallel

````

process_chunks_enrichment_parallel(chunks: list) -> list

---

## Database Schema

# Full pipeline: metadata → subtitles → chunks → AI → DB---python main.py

### Tables

- `youtube_videos` - Video metadataprocess_full_video(url_or_id: str, save_to_db: bool = True) -> Dict

- `subtitle_chunks` - Chunked subtitles with AI enrichment

- `video_notes` - User notes for videos```

- `job_queue` - Background job processing

### Key Features

- Word-based chunks (not time-based)**Example:**### `backend/openai/enrichment.py```````bash

- Automatic timestamps (created_at, updated_at)

- Full CRUD operations```python

- Upsert support

from orchestrator import process_full_video

---

## Features

# Complete pipeline**Input:**cd backend/db

✅ Modular architecture (no cross-imports)

✅ YouTube Data API v3 integration result = process_full_video("dQw4w9WgXcQ")

✅ Subtitle extraction via yt-dlp

✅ Word-based chunking (configurable) # Returns: {- Subtitle chunk text (string) - **REQUIRED**

✅ Parallel AI enrichment (5x faster)

✅ Supabase PostgreSQL integration # 'video_id': 'dQw4w9WgXcQ',

✅ FastAPI REST endpoints

✅ Comprehensive test suite (11/11 passing) # 'metadata': {...},- Prompts dictionary (from `prompts.py`) - **REQUIRED**API: http://localhost:8000/docspython create_table.py

✅ 100% frontend compatible

# 'chunks': [{...}, {...}],

---

# 'enriched_chunks': [{...}, {...}]- Optional: model, temperature, max_tokens, retry settings

## Documentation

# }

- `README.md` - This file (setup & module reference)

- `STATUS.md` - Current project status``````````

- `QUICKSTART.md` - Quick command reference

- `REFACTORING_COMPLETE.md` - Refactoring summary

------**Output:**

## Troubleshooting

### "YOUTUBE_API_KEY not found"## Quick Start- Dictionary containing AI-generated fields:## Testing

Create `.env` file with your API key.

### "Table does not exist"

Run `python db/create_table.py` to create tables.```bash  - `title` (string): Short title for the chunk

### "OPENAI_API_KEY not found"# Install dependencies

Add OpenAI API key to `.env` file.

pip install -r requirements.txt - `field_1` (string): First AI field (e.g., summary)This will create:

### Tests failing

Make sure all environment variables are set and database is accessible.

---# Configure environment (.env file) - `field_2` (string): Second AI field (e.g., key points)

## Production Ready ✅YOUTUBE_API_KEY=...

- ✅ All tests passing (11/11)OPENAI_API_KEY=... - `field_3` (string): Third AI field (e.g., topics/themes)````bash

- ✅ Database integration verified

- ✅ API endpoints workingSUPABASE_URL=...

- ✅ Frontend compatible

- ✅ Error handling implementedSUPABASE_KEY=...

- ✅ Documentation complete

# Setup database**Functions:**python test_refactor.py # Module tests- `youtube_videos` table with all required fields

cd db

python create_table.py```python

# Run serverenrich_chunk(python test_complete.py # Full suite- Automatic triggers for `updated_at` timestamp

cd ..

python main.py text: str, # REQUIRED: subtitle chunk text

````

    prompts: Dict[str, str],      # REQUIRED: prompt templatespython test_e2e.py         # End-to-end with DB- Indexes for common queries

**API Documentation:** http://localhost:8000/docs

    model: str = "gpt-4o-mini",

---

    temperature: float = 0.5,```- Row Level Security policies

## Testing

    max_tokens_title: int = 50,

```bash

python test_complete.py    # Full suite (6/6 tests)    max_tokens_other: int = 200

python test_e2e.py         # End-to-end with DB (5/5 tests)

```) -> Dict[str, str]



---## Usage## Database Schema



## Usage Examplesenrich_chunks_parallel(



### Process a Single Video    chunks: list,                 # List of chunk dicts with 'text' field



```python    prompts: Dict[str, str],      # REQUIRED: prompt templates

from orchestrator import process_full_video

    max_workers: int = 5```python### YouTube Videos Table

# Full pipeline with DB save

result = process_full_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")) -> list



# Process without DB save (for testing)```from orchestrator import process_full_video

result = process_full_video("dQw4w9WgXcQ", save_to_db=False)

````

### Fetch Metadata Only**Example:**```sql

`python`python

from youtube.metadata import fetch_video_metadata

from prompts import PROMPTS# Extract → Chunk → AI Enrich → Save to DBCREATE TABLE youtube_videos (

metadata = fetch_video_metadata("dQw4w9WgXcQ")

print(metadata['title'])

print(metadata['view_count'])

````result = enrich_chunk(process_full_video("dQw4w9WgXcQ")    -- Primary identifier



### Extract Subtitles Only    text="We're no strangers to love...",



```python    prompts={```    id VARCHAR(20) PRIMARY KEY,

from subtitles.extractor import extract_and_chunk_subtitles

        'title': PROMPTS['short_title']['template'],

chunks = extract_and_chunk_subtitles("dQw4w9WgXcQ")

for i, chunk in enumerate(chunks):        'field_1': PROMPTS['ai_field_1']['template'],

    print(f"Chunk {i}: {chunk['word_count']} words")

```        'field_2': PROMPTS['ai_field_2']['template'],



### Enrich Chunks with AI        'field_3': PROMPTS['ai_field_3']['template']## Configuration    -- Top-level fields



```python    }

from openai.enrichment import enrich_chunks_parallel

from prompts import PROMPTS)    kind VARCHAR(50),

from config import OPENAI_MODEL, OPENAI_TEMPERATURE

# Returns: {

# Prepare prompts

prompt_dict = {#   'title': 'Rick Astley Music Video',Edit `config.py`:    etag VARCHAR(100),

    'title': PROMPTS['short_title']['template'],

    'field_1': PROMPTS['ai_field_1']['template'],#   'field_1': 'A summary of the lyrics...',

    'field_2': PROMPTS['ai_field_2']['template'],

    'field_3': PROMPTS['ai_field_3']['template']#   'field_2': '• Key point 1\n• Key point 2...',- `CHUNK_TARGET_WORDS = 1000` - Words per chunk

}

#   'field_3': 'Music, Love, Relationships'

# Enrich in parallel (5 workers by default)

enriched = enrich_chunks_parallel(# }- `OPENAI_MODEL = "gpt-4o-mini"` - AI model    -- Snippet fields (flattened)

    chunks=chunks,

    prompts=prompt_dict,```

    model=OPENAI_MODEL,

    temperature=OPENAI_TEMPERATURE    published_at TIMESTAMPTZ,

)

```---



---See full documentation in README.md (detailed version)    channel_id VARCHAR(50),



## Configuration### `backend/orchestrator.py`



Edit `config.py` to customize:    title TEXT,



```pythonCoordinates all modules and handles database operations.    description TEXT,

# Chunking (word-based)

CHUNK_TARGET_WORDS = 1000      # Target words per chunk    channel_title VARCHAR(255),

CHUNK_MAX_WORDS = 1500         # Maximum words per chunk

CHUNK_OVERLAP_WORDS = 100      # Overlap between chunks**Functions:**    category_id VARCHAR(10),

CHUNK_MIN_FINAL_WORDS = 500    # Min words for final chunk

```python    live_broadcast_content VARCHAR(20),

# OpenAI

OPENAI_MODEL = "gpt-4o-mini"# Fetch metadata and save to DB    default_language VARCHAR(10),

OPENAI_TEMPERATURE = 0.5

OPENAI_MAX_TOKENS_TITLE = 50process_video_metadata(url_or_id: str) -> Dict    default_audio_language VARCHAR(10),

OPENAI_MAX_TOKENS_OTHER = 200

````

---# Extract subtitles, chunk, and save to DB -- Tags stored as PostgreSQL array

## API Endpointsprocess_video_subtitles(video_id: str) -> List[Dict] tags TEXT[],

All endpoints maintain 100% frontend compatibility:

```# Enrich chunks with AI in parallel    -- Complex nested objects stored as JSONB

POST   /api/video              # Fetch video metadata

POST   /api/note               # Create/update noteprocess_chunks_enrichment_parallel(chunks: list) -> list    thumbnails JSONB,

GET    /api/chunks/{video_id}  # Get chunks for video

POST   /api/jobs/process-video # Full pipeline processing    localized JSONB,  -- Only stored if default_language is not 'en'

```

# Full pipeline: metadata → subtitles → chunks → AI → DB

---

process_full_video(url_or_id: str, save_to_db: bool = True) -> Dict -- Content details

## Database Schema

`````duration VARCHAR(20),

### Tables

- `youtube_videos` - Video metadata    dimension VARCHAR(10),

- `subtitle_chunks` - Chunked subtitles with AI enrichment

- `video_notes` - User notes for videos**Example:**    definition VARCHAR(10),

- `job_queue` - Background job processing

```python    caption BOOLEAN,

### Key Features

- Word-based chunks (not time-based)from orchestrator import process_full_video    licensed_content BOOLEAN,

- Automatic timestamps (created_at, updated_at)

- Full CRUD operations    content_rating JSONB,

- Upsert support

# Complete pipeline    projection VARCHAR(20),

---

result = process_full_video("dQw4w9WgXcQ")

## Features

# Returns: {    -- Status fields

✅ Modular architecture (no cross-imports)

✅ YouTube Data API v3 integration  #   'video_id': 'dQw4w9WgXcQ',    upload_status VARCHAR(20),

✅ Subtitle extraction via yt-dlp

✅ Word-based chunking (configurable)  #   'metadata': {...},    privacy_status VARCHAR(20),

✅ Parallel AI enrichment (5x faster)

✅ Supabase PostgreSQL integration  #   'chunks': [{...}, {...}],    license VARCHAR(20),

✅ FastAPI REST endpoints

✅ Comprehensive test suite (11/11 passing)  #   'enriched_chunks': [{...}, {...}]    embeddable BOOLEAN,

✅ 100% frontend compatible

# }    public_stats_viewable BOOLEAN,

---

```    made_for_kids BOOLEAN,

## Documentation



- `README.md` - This file (setup & module reference)

- `STATUS.md` - Current project status---    -- Statistics

- `QUICKSTART.md` - Quick command reference

- `REFACTORING_COMPLETE.md` - Refactoring summary    view_count BIGINT,



---## Quick Start    like_count BIGINT,



## Troubleshooting    favorite_count INTEGER,



### "YOUTUBE_API_KEY not found"```bash    comment_count BIGINT,

Create `.env` file with your API key.

# Install

### "Table does not exist"

Run `python db/create_table.py` to create tables.pip install -r requirements.txt    -- Automatic timestamps



### "OPENAI_API_KEY not found"    created_at TIMESTAMPTZ DEFAULT NOW(),

Add OpenAI API key to `.env` file.

# Configure .env    updated_at TIMESTAMPTZ DEFAULT NOW()  -- Auto-updated via trigger

### Tests failing

Make sure all environment variables are set and database is accessible.YOUTUBE_API_KEY=...);



---OPENAI_API_KEY=...````



## Production Ready ✅SUPABASE_URL=...



- ✅ All tests passing (11/11)SUPABASE_KEY=...### Indexes

- ✅ Database integration verified

- ✅ API endpoints working

- ✅ Frontend compatible

- ✅ Error handling implemented# Setup database- `idx_channel_id` - For filtering by channel

- ✅ Documentation complete

cd db- `idx_published_at` - For sorting by publish date

python create_table.py- `idx_tags` - GIN index for array tag searches

- `idx_updated_at` - For finding recently updated videos

# Run- `idx_created_at` - For finding recently added videos

cd ..

python main.py## Usage

`````

### Start the Backend API Server

API: http://localhost:8000/docs

The simplest way to start the backend:

## Testing

````bash

```bashcd backend

python test_complete.py    # Full suite (6/6 tests)python main.py

python test_e2e.py         # End-to-end with DB (5/5 tests)```

````

This will start the FastAPI server at http://localhost:8000 with:

## Usage Examples

- **API endpoints**: http://localhost:8000/api/\*

### Process a Single Video- **Interactive documentation**: http://localhost:8000/docs

- **Auto-reload enabled** for development

````python

from orchestrator import process_full_video#### Alternative: Direct uvicorn command



# Full pipeline with DB save```bash

result = process_full_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")cd backend

python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Process without DB save (for testing)```

result = process_full_video("dQw4w9WgXcQ", save_to_db=False)

```#### Environment Variables (Optional)



### Fetch Metadata OnlyYou can customize the server by setting environment variables in `backend/db/.env`:



```python```env

from youtube.metadata import fetch_video_metadataAPI_HOST=0.0.0.0

API_PORT=8000

metadata = fetch_video_metadata("dQw4w9WgXcQ")API_RELOAD=true

print(metadata['title'])```

print(metadata['view_count'])

```### Run Demo/Test Script



### Extract Subtitles OnlyTo test the YouTube video fetching functionality:



```python```bash

from subtitles.extractor import extract_and_chunk_subtitlescd backend

python demo.py

chunks = extract_and_chunk_subtitles("dQw4w9WgXcQ")```

for i, chunk in enumerate(chunks):

    print(f"Chunk {i}: {chunk['word_count']} words")This runs a demonstration that:

````

1. Fetches example videos from YouTube

### Enrich Chunks with AI2. Stores them in the database

3. Queries and displays the results

````python

from openai.enrichment import enrich_chunks_parallel#### Demo Options

from prompts import PROMPTS

from config import OPENAI_MODEL, OPENAI_TEMPERATURE```bash

# Run with demo videos

# Prepare promptspython demo.py --demo

prompt_dict = {

    'title': PROMPTS['short_title']['template'],# Interactive mode (enter your own URLs)

    'field_1': PROMPTS['ai_field_1']['template'],python demo.py --interactive

    'field_2': PROMPTS['ai_field_2']['template'],

    'field_3': PROMPTS['ai_field_3']['template']# Fetch specific URLs

}python demo.py URL1 URL2 URL3

````

# Enrich in parallel (5 workers by default)

enriched = enrich_chunks_parallel(### Fetch Videos from Python Script

    chunks=chunks,

    prompts=prompt_dict,```python

    model=OPENAI_MODEL,from backend.fetch_youtube_videos import fetch_and_store_videos, fetch_single_video

    temperature=OPENAI_TEMPERATURE

)# Fetch multiple videos

````urls = [

    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",

## Configuration    "https://youtu.be/9bZkp7q19f0",

    "dQw4w9WgXcQ",  # Plain video ID also works

Edit `config.py` to customize:]



```pythonresults = fetch_and_store_videos(urls)

# Chunking (word-based)print(f"Successfully stored: {results['success']} videos")

CHUNK_TARGET_WORDS = 1000      # Target words per chunk

CHUNK_MAX_WORDS = 1500         # Maximum words per chunk# Fetch a single video

CHUNK_OVERLAP_WORDS = 100      # Overlap between chunksvideo = fetch_single_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

CHUNK_MIN_FINAL_WORDS = 500    # Min words for final chunk```



# OpenAI### CRUD Operations

OPENAI_MODEL = "gpt-4o-mini"

OPENAI_TEMPERATURE = 0.5```python

OPENAI_MAX_TOKENS_TITLE = 50from backend.db.youtube_crud import (

OPENAI_MAX_TOKENS_OTHER = 200    get_video_by_id,

```    get_all_videos,

    get_videos_by_channel,

## API Endpoints    search_videos_by_tags,

    get_recently_updated_videos

All endpoints maintain 100% frontend compatibility:)



```# Get a specific video

POST   /api/video              # Fetch video metadatavideo = get_video_by_id("dQw4w9WgXcQ")

POST   /api/note               # Create/update note

GET    /api/chunks/{video_id}  # Get chunks for video# Get all videos (with limit)

POST   /api/jobs/process-video # Full pipeline processingvideos = get_all_videos(limit=50)

````

# Get videos from a channel

## Database Schemachannel_videos = get_videos_by_channel("UCuAXFkgsw1L7xaCfnd5JJOw")

### Tables# Search by tags

- `youtube_videos` - Video metadatatagged_videos = search_videos_by_tags(["rickroll", "music"])

- `subtitle_chunks` - Chunked subtitles with AI enrichment

- `video_notes` - User notes for videos# Get recently updated videos (last 24 hours)

- `job_queue` - Background job processingrecent = get_recently_updated_videos(hours=24)

````

### Key Features

- Word-based chunks (not time-based)### Run Tests

- Automatic timestamps (created_at, updated_at)

- Full CRUD operations```bash

- Upsert support# Test database connection and table creation

cd backend/db

## Featurespython create_table.py



✅ Modular architecture (no cross-imports)  # Test YouTube video CRUD operations

✅ YouTube Data API v3 integration  python youtube_crud.py

✅ Subtitle extraction via yt-dlp

✅ Word-based chunking (configurable)  # Test YouTube API fetching and database storage (demo)

✅ Parallel AI enrichment (5x faster)  cd ..

✅ Supabase PostgreSQL integration  python demo.py --demo

✅ FastAPI REST endpoints

✅ Comprehensive test suite (11/11 passing)  # Test the backend API

✅ 100% frontend compatible  python quick_test.py

````

## Documentation

## Supported URL Formats

- `README.md` - This file (setup & module reference)

- `STATUS.md` - Current project statusThe system can extract video IDs from:

- `QUICKSTART.md` - Quick command reference

- `REFACTORING_COMPLETE.md` - Refactoring summary- `https://www.youtube.com/watch?v=VIDEO_ID`

- `https://youtu.be/VIDEO_ID`

## Troubleshooting- `https://www.youtube.com/embed/VIDEO_ID`

- `https://www.youtube.com/v/VIDEO_ID`

### "YOUTUBE_API_KEY not found"- `VIDEO_ID` (plain 11-character video ID)

Create `.env` file with your API key.

## Features Explained

### "Table does not exist"

Run `python db/create_table.py` to create tables.### Automatic Timestamp Tracking

### "OPENAI_API_KEY not found"- `created_at`: Set automatically when a video is first inserted

Add OpenAI API key to `.env` file.- `updated_at`: Automatically updated whenever the row is modified (via database trigger)

### Tests failingThis allows you to:

Make sure all environment variables are set and database is accessible.

- Track when videos were first added to your database

## Production Ready ✅- Track when video statistics (views, likes) were last refreshed

- Query recently updated videos

- ✅ All tests passing (11/11)

- ✅ Database integration verified### Upsert (Insert or Update)

- ✅ API endpoints working

- ✅ Frontend compatibleThe system uses PostgreSQL's `upsert` functionality:

- ✅ Error handling implemented

- ✅ Documentation complete- If a video doesn't exist, it's created

- If a video already exists (same ID), it's updated
- The `updated_at` timestamp is automatically refreshed on updates

### Tag Storage

Tags are stored as PostgreSQL arrays (`TEXT[]`), allowing:

- Efficient storage
- Fast searching with GIN indexes
- Array overlap queries (`&&` operator)
- Individual element searches (`= ANY(tags)`)

### JSONB Storage

Complex nested objects like thumbnails and localized content are stored as JSONB:

- Preserves original structure
- Allows JSON queries if needed
- More flexible than flattening all fields

### Conditional Localized Storage

The `localized` field is only stored if `default_language` is NOT 'en', following the task requirement to save space for English-language videos.

## API Rate Limits

YouTube Data API v3 has quota limits:

- Default quota: 10,000 units per day
- Each `videos.list` request costs 1 unit per video (approximately)
- Batch requests (up to 50 videos) are more efficient

## Error Handling

The system handles:

- Invalid YouTube URLs
- API errors (network issues, invalid API key)
- Database connection errors
- Missing environment variables

## Next Steps

1. ✅ Database schema created
2. ✅ CRUD operations implemented
3. ✅ YouTube API integration
4. ✅ Batch processing
5. ⏳ Frontend integration
6. ⏳ Scheduled updates for video statistics
7. ⏳ Search and filtering UI

## Troubleshooting

### "YOUTUBE_API_KEY not found"

Make sure you have created a `.env` file with your YouTube API key.

### "Table does not exist"

Run `python backend/db/create_table.py` to create the required tables.

### "Connection refused"

Check your Supabase credentials in the `.env` file.

### "Quota exceeded"

You've hit YouTube API's daily quota limit. Wait until the next day or request a quota increase.

```

```
