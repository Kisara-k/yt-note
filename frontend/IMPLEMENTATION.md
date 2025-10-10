# TipTap Markdown Editor Implementation Guide

## Overview

This project implements a full-featured markdown editor using TipTap in a Next.js application. The editor supports rich text editing with automatic markdown conversion, file management, and persistent storage.

## Architecture

### Component Structure

```
┌─────────────────────────────────────────┐
│         MarkdownEditor (Main)           │
│  - File management UI                   │
│  - Toolbar with save/load/download      │
│  - Draft auto-save logic                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│    TiptapMarkdownEditor (Editor)        │
│  - TipTap editor instance               │
│  - Markdown extensions                  │
│  - Rich text toolbar                    │
│  - Markdown ↔ Rich Text conversion      │
└─────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      File Manager (lib/file-manager)    │
│  - localStorage operations              │
│  - File CRUD operations                 │
│  - Import/Export utilities              │
└─────────────────────────────────────────┘
```

## Key Features Implementation

### 1. Markdown Conversion

We use the `tiptap-markdown` extension to handle bidirectional conversion between markdown and rich text:

```typescript
import { Markdown } from 'tiptap-markdown';

const editor = useEditor({
  extensions: [
    StarterKit,
    Markdown.configure({
      html: true, // Allow HTML in markdown
      tightLists: true, // No <p> tags in list items
      bulletListMarker: '-', // Use - for bullets
      linkify: true, // Auto-detect URLs
      breaks: false, // Don't convert \n to <br>
      transformPastedText: true, // Parse pasted markdown
      transformCopiedText: true, // Copy as markdown
    }),
  ],
});
```

**Getting Markdown from Editor:**

```typescript
const markdown = (editor.storage.markdown as MarkdownStorage).getMarkdown();
```

**Setting Content from Markdown:**

```typescript
editor.commands.setContent(markdownString);
```

### 2. Auto-save Implementation

The draft auto-saves to localStorage with a 1-second debounce:

```typescript
useEffect(() => {
  if (isDraft) {
    const timer = setTimeout(() => {
      saveDraft(content);
    }, 1000);
    return () => clearTimeout(timer);
  }
}, [content, isDraft]);
```

### 3. File Management

All files are stored in localStorage as JSON:

```typescript
interface MarkdownFile {
  name: string;
  content: string;
  lastModified: Date;
}

// Storage structure
localStorage.setItem(FILES_KEY, JSON.stringify(files));
```

**Key Operations:**

- `getAllFiles()`: Retrieves all saved files
- `saveFile(name, content)`: Saves or updates a file
- `loadFile(name)`: Loads a specific file
- `deleteFile(name)`: Removes a file
- `downloadFile(name, content)`: Downloads as .md file

### 4. Import/Export

**Import:**

```typescript
export function uploadFile(): Promise<MarkdownFile> {
  return new Promise((resolve, reject) => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.md,.markdown';

    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      const content = await file.text();
      resolve({ name: file.name, content, lastModified: new Date() });
    };

    input.click();
  });
}
```

**Export:**

```typescript
export function downloadFile(name: string, content: string): void {
  const blob = new Blob([content], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = name.endsWith('.md') ? name : `${name}.md`;
  link.click();
  URL.revokeObjectURL(url);
}
```

### 5. SSR Compatibility

TipTap requires special handling for Next.js SSR:

```typescript
const editor = useEditor({
  immediatelyRender: false,  // Prevents hydration mismatch
  extensions: [...],
});
```

### 6. Rich Text Toolbar

The toolbar provides buttons for common markdown formatting:

- **Text Formatting**: Bold, Italic, Underline, Strikethrough, Code
- **Headings**: H1, H2, H3
- **Lists**: Bullet, Numbered, Task lists
- **Blocks**: Blockquote, Code block
- **Media**: Links, Images
- **History**: Undo, Redo

Each button uses TipTap's chainable commands:

```typescript
<Toggle
  pressed={editor.isActive('bold')}
  onPressedChange={() => editor.chain().focus().toggleBold().run()}
>
  <Bold className='h-4 w-4' />
</Toggle>
```

## Extensions Used

### Core Extensions

1. **StarterKit**: Bundle of essential extensions

   - Document, Paragraph, Text
   - Bold, Italic, Strike, Code
   - Heading, Blockquote
   - BulletList, OrderedList, ListItem
   - HorizontalRule, HardBreak
   - History (Undo/Redo)

2. **Markdown**: Bidirectional markdown conversion
3. **Link**: Hyperlink support
4. **Image**: Image insertion via URL
5. **Underline**: Underline text
6. **TaskList & TaskItem**: Checkbox lists

## Styling

### Editor Styles

The editor uses a combination of:

- Tailwind CSS utilities
- Custom ProseMirror styles in `globals.css`
- shadcn/ui component styling

**Key Style Classes:**

```css
.ProseMirror {
  /* Base editor styles */
}

.ProseMirror h1,
h2,
h3 {
  /* Heading styles */
}

.ProseMirror ul[data-type='taskList'] {
  /* Task list specific styles */
}
```

### Dark Mode

All styles support dark mode through Tailwind's dark variant:

```css
.dark .ProseMirror code {
  background-color: #2d3748;
}
```

## Data Flow

### Loading a File

```
User selects file from dropdown
       ↓
loadFile(fileName) retrieves from localStorage
       ↓
setContent(file.content)
       ↓
Editor updates via useEffect
       ↓
TipTap parses markdown to rich text
```

### Saving Changes

```
User types in editor
       ↓
onUpdate callback fires
       ↓
getMarkdown() converts to markdown
       ↓
onChange(markdown) updates state
       ↓
Auto-save timer triggers
       ↓
saveDraft() or saveFile() to localStorage
```

## Error Handling

### Filename Validation

```typescript
export function isValidFilename(name: string): boolean {
  const invalidChars = /[<>:"/\\|?*\x00-\x1F]/;
  if (invalidChars.test(name)) return false;

  const reserved = /^(con|prn|aux|nul|com[0-9]|lpt[0-9])$/i;
  if (reserved.test(name.replace(/\.[^.]*$/, ''))) return false;

  return name.length > 0 && name.length <= 255;
}
```

### Storage Errors

All file operations are wrapped in try-catch blocks with toast notifications:

```typescript
try {
  saveFile(fileName, content);
  toast.success(`Saved: ${fileName}`);
} catch (error) {
  toast.error('Failed to save file');
}
```

## Performance Optimizations

1. **Debounced Auto-save**: 1-second delay prevents excessive writes
2. **Lazy Editor Initialization**: `immediatelyRender: false`
3. **Memoized File List**: useCallback for loadFiles()
4. **Efficient Updates**: Only update editor when value actually changes

## Limitations & Considerations

### LocalStorage Limits

- Maximum ~5-10MB per domain
- Synchronous operations
- Cleared with browser data
- Not shared across devices

### Markdown Support

- Uses GitHub Flavored Markdown (GFM)
- Some complex tables may not convert perfectly
- HTML passthrough enabled for flexibility

### Browser Compatibility

- Requires modern browser with ES6+ support
- File System Access API for native file dialogs (progressive enhancement)
- LocalStorage must be enabled

## Future Enhancements

Potential improvements:

1. **Cloud Storage**: Sync files to a backend server
2. **Collaborative Editing**: Real-time collaboration with TipTap Collab
3. **Export Formats**: PDF, DOCX export using TipTap extensions
4. **Syntax Highlighting**: Code block language detection with lowlight
5. **Image Upload**: Upload images instead of URLs only
6. **Version History**: Track file versions and allow restoration
7. **Search**: Full-text search across all files
8. **Tags & Folders**: Organize files with metadata
9. **Keyboard Shortcuts**: More customizable shortcuts
10. **Mobile Support**: Touch-friendly interface

## Troubleshooting

### Editor Not Rendering

- Check `immediatelyRender: false` is set
- Verify all extensions are properly imported
- Check console for extension conflicts

### Markdown Not Converting

- Verify `tiptap-markdown` is installed
- Check markdown extension configuration
- Ensure proper type casting for storage access

### Files Not Saving

- Check localStorage is enabled
- Verify quota not exceeded
- Check filename validation

### Styling Issues

- Import `globals.css` in layout
- Verify Tailwind config includes component paths
- Check for CSS specificity conflicts

## Testing Recommendations

1. **Unit Tests**: File manager functions
2. **Integration Tests**: Editor component with markdown conversion
3. **E2E Tests**: Complete user workflows (create, save, load, delete)
4. **Accessibility Tests**: Keyboard navigation, screen readers
5. **Performance Tests**: Large file handling, many files in list

## Deployment

For production deployment:

1. Run type checking: `pnpm tsc --noEmit`
2. Build the application: `pnpm build`
3. Test production build: `pnpm start`
4. Deploy to Vercel or other Next.js hosting

**Environment Variables:**
None required for basic functionality. Add if implementing cloud storage.

## Resources

- [TipTap Documentation](https://tiptap.dev/)
- [tiptap-markdown GitHub](https://github.com/aguingand/tiptap-markdown)
- [Next.js Documentation](https://nextjs.org/docs)
- [shadcn/ui](https://ui.shadcn.com/)
