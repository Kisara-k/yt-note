YouTube Notes — Software Requirements Specification (SRS)

2. Overall System Description

2.1 Components

Frontend: Next.js application. Pages include: Video view, Video-chunk inspector, Notes editor/viewer, Video filter page, Creator notes page.

Backend DB: Supabase PostgreSQL for structured data and Supabase Storage for subtitle large objects.

Background Worker(s): Worker(s) (e.g., Cloud Run / managed VM / container) running yt-dlp, chunking logic, OpenAI calls, and writing results to DB/storage. Jobs are queued (Redis + BullMQ, or Supabase-compatible job queue) to allow controlled parallelism.

External APIs: YouTube Data API (metadata), OpenAI API (chunk processing), yt-dlp (subtitle extraction).

Authentication: Supabase email-based auth. Only authorised users can create/edit notes.

2.2 Context and Data Flow (high level)

User submits YouTube URL via Next.js UI.

Frontend extracts video ID and queries backend (DB) to check existence.

If missing, backend fetches metadata via YouTube Data API and creates videos record (synchronous) and enqueues a background job to extract subtitles and run AI processing.

Background worker runs yt-dlp to fetch subtitles (if present), stores subtitle text chunks in Supabase Storage and chunk metadata + AI outputs in subtitle_chunks table.

When the user opens a video page:

If processing is incomplete, show metadata and a processing status; allow viewing of already-computed chunks.

If processing is complete, load the chunk index (index, short title) into a dropdown; selecting a chunk displays the three other AI fields in scrollable boxes and the subtitle text.

Authorized users can open the TipTap editor to add or edit notes. TipTap <-> Markdown conversion occurs on save, and Markdown is stored in video_notes table.

3. Functional Requirements (FR)

Each requirement below has an ID (FR-*) for traceability.

FR-01: Video ingestion

FR-01.1: When a user submits a YouTube URL, extract the canonical video_id and return existing video info if present.

FR-01.2: If video_id does not exist, fetch metadata from YouTube Data API (title, description, channel/creator, thumbnails, duration, tags, viewCount, publishedAt) and insert into videos table.

FR-01.3: Immediately show stored video info to the user after insertion; subtitle/AI processing happens asynchronously.

FR-02: Notes (primary focus)

FR-02.1: Authorized users can create, edit, and delete notes for a video. Notes are saved as Markdown in the video_notes table.

FR-02.2: Notes are shared across authorized users. The video_notes table MUST NOT store created_by or updated_by user IDs. It may store created_at and updated_at timestamps.

FR-02.3: The TipTap editor must convert rich text <-> Markdown on save/load; the DB content is Markdown.

FR-02.4: Notes displayed in the creator-notes route must show the YouTube video title and video ID for each note and be sorted in ascending order by day.

FR-03: Subtitle extraction and chunking

FR-03.1: When a background job runs for a video, use yt-dlp to download/ extract subtitles (prefer user language or automatically detect language). If no subtitles available, record this state and set processing status to no_subtitles.

FR-03.2: Break subtitles into hierarchical chunks for long videos. Each final chunk is independently addressable and stored as a large text object file in Supabase Storage.

FR-03.3: Each stored chunk must map to a row in subtitle_chunks with a compound primary key (video_id, chunk_id).

FR-03.4: Each chunk record also stores metadata: start_time, end_time (seconds), parent_chunk_id (nullable for hierarchy), storage_path, size_bytes, and ai-derived fields (see FR-04).

FR-04: OpenAI AI enrichment per chunk

FR-04.1: For each chunk, call OpenAI API ("gpt-4.1-nano", using OPENAI_API_KEY from .env), to compute four fields. One of these fields is the short title; the other three are configurable semantic fields (example names: high_level_summary, key_points, topics but field names must be configurable via prompts_config).

FR-04.2: The prompts/templates used to produce the four fields must be editable and stored in a prompts_config table (or equivalent config store).

FR-04.3: These four fields must be stored with the chunk row (so each chunk row contains short_title, ai_field_1, ai_field_2, ai_field_3).

FR-04.4: When a video is loaded and has these properties computed, the frontend must fetch and display them for each chunk.

FR-05: UI - chunk selection and display

FR-05.1: When a user opens a video page, a dropdown (or similar) must show a chunk index list: index | short_title for each chunk.

FR-05.2: Selecting a chunk loads three other AI fields into separate scrollable boxes (each box scrollable independently) and also loads and displays the subtitle text.

FR-05.3: Subtitle text display may be fetched on-demand from Supabase Storage to keep initial responses fast.

FR-06: Videos filtering route

FR-06.1: Provide a separate route/page to filter and browse videos by available metadata: creator (channel name), duration range, auto-downloaded YouTube tags, and custom tags.

FR-06.2: The videos table must store: youtube_tags (auto), and custom_tag_keys (array of tag keys). Filtering by custom_tag_keys must be supported (multi-select).

FR-06.3: Custom tag keys map to editable words via a tag_keys table. The UI shows mapped human-readable tag words.

FR-07: Creator-notes route

FR-07.1: Provide a route to display notes for all videos by a specific creator. Input is the creator/channel name or channel ID.

FR-07.2: Results are notes formatted as rendered Markdown, sorted ascending by day (by created_at date), and must include video title and video ID alongside each note.

FR-08: Performance and parallel processing

FR-08.1: Background processing steps (yt-dlp, chunking, multiple OpenAI calls) must be parallelized within safe concurrency limits.

FR-08.2: The system must support incremental processing: partial results must be usable and viewable (e.g., if first N chunks processed, they appear immediately).

FR-08.3: Large operations must be idempotent: repeated ingestion of the same video_id must not duplicate chunks or AI fields.