## Folder-style component tree (top-level components first)

```
VideoNotesEditor/
└─ ChunkViewer/
├─ NoteEditor/
│ └─ TiptapMarkdownEditor/
│ └─ MenuBar (internal)
├─ AIFieldDisplay/
├─ CustomTooltip/
└─ ui/select (ui primitive)

BookNotesEditor/
└─ ChunkViewer/
├─ NoteEditor/
│ └─ TiptapMarkdownEditor/
│ └─ MenuBar (internal)
├─ AIFieldDisplay/
├─ CustomTooltip/
└─ ui/select (ui primitive)

MarkdownEditor/
└─ TiptapMarkdownEditor/
└─ MenuBar (internal)

NoteEditor/
└─ TiptapMarkdownEditor/
└─ MenuBar (internal)

ChunkViewer/
├─ TiptapMarkdownEditor/
│ └─ MenuBar (internal)
├─ NoteEditor/
│ └─ TiptapMarkdownEditor/
├─ AIFieldDisplay/
├─ CustomTooltip/
└─ ui/select (ui primitive)

TiptapMarkdownEditor/
└─ MenuBar (internal)
```

CustomTooltip/

- small Radix wrapper, used by many components

AIFieldDisplay/

- leaf component used by `ChunkViewer` and editors

Other top-level / leaf components (mostly built from `ui/*` primitives):

- BookAdd/
- BookChunkEditor/
- BookFilter/
- VideoFilter/
- CreatorNotes/
- LoginForm/

---

## Component hierarchy (frontend/components)

This file documents the hierarchy and key relationships between React components found in `frontend/components` (excluding `/ui` and `/image`). It's a quick reference for which components compose others and which are reusable/shared.

Overview (tree):

- TiptapMarkdownEditor (`tiptap-markdown-editor.tsx`)

  - MenuBar (internal to the editor)
  - Used by: `note-editor`, `chunk-viewer`, `book-notes-editor`, `video-notes-editor`, `markdown-editor`

- NoteEditor (`note-editor.tsx`)

  - Uses: `TiptapMarkdownEditor`

- AIFieldDisplay (`ai-field-display.tsx`)

  - Leaf component (used to display / edit AI-generated fields)

- ChunkViewer (`chunk-viewer.tsx`)

  - Uses: `TiptapMarkdownEditor`, `NoteEditor`, `AIFieldDisplay`, `CustomTooltip`, ui/select
  - Used by: `video-notes-editor`, `book-notes-editor`

- BookNotesEditor (`book-notes-editor.tsx`)

  - Uses: `TiptapMarkdownEditor`, `ChunkViewer`, `NoteEditor`, `CustomTooltip`

- VideoNotesEditor (`video-notes-editor.tsx`)

  - Uses: `TiptapMarkdownEditor`, `ChunkViewer`, `NoteEditor`, `CustomTooltip`

- MarkdownEditor (`markdown-editor.tsx`)

  - Uses: `TiptapMarkdownEditor`

- CustomTooltip (`custom-tooltip.tsx`)

  - Small shared tooltip wrapper (used across many components)

- Other leaf / utility components (primarily use /ui primitives):
  - `ai-field-display.tsx` (see above)
  - `book-add.tsx`
  - `book-chunk-editor.tsx`
  - `book-filter.tsx`
  - `creator-notes.tsx`
  - `login-form.tsx`
  - `video-filter.tsx`

Quick ASCII diagram:

TiptapMarkdownEditor
└─ MenuBar (internal)

NoteEditor -> TiptapMarkdownEditor

ChunkViewer -> { TiptapMarkdownEditor, NoteEditor, AIFieldDisplay, CustomTooltip }
└─ used-by -> { VideoNotesEditor, BookNotesEditor }

VideoNotesEditor -> { ChunkViewer, NoteEditor, TiptapMarkdownEditor, CustomTooltip }
BookNotesEditor -> { ChunkViewer, NoteEditor, TiptapMarkdownEditor, CustomTooltip }

Other pages/components (book-add, book-filter, book-chunk-editor, creator-notes, login-form, video-filter) are mostly leaf components built from `ui/*` primitives.

Notes

- Many components rely on shared UI primitives under `frontend/components/ui/*` (Buttons, Inputs, Cards, Popovers, etc.).
- `CustomTooltip` is a tiny, shared wrapper over Radix tooltip used across editors/viewers.
- `TiptapMarkdownEditor` is the main rich editor building block reused widely.

If you want, I can:

- Generate a visual diagram (SVG/PNG) from this tree.
- Expand the diagram to include `frontend/components/ui/*` items.

---

Generated: October 16, 2025
