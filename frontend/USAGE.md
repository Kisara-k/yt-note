# Quick Start Guide

## Using the Markdown Editor

### Getting Started

1. **Start the Development Server**

   ```bash
   cd frontend
   pnpm install
   pnpm dev
   ```

2. **Open the Editor**
   Navigate to [http://localhost:3000](http://localhost:3000)

### Creating Your First Document

1. **Draft Mode** - The editor opens in draft mode by default

   - Start typing immediately
   - Your work is auto-saved every second to localStorage
   - The title shows "Draft" at the top

2. **Formatting Text**

   - Use the toolbar buttons for formatting
   - Or use keyboard shortcuts (Ctrl/Cmd + B for bold, etc.)
   - The editor automatically converts to markdown

3. **Save Your Document**
   - Click "Save" button to save the current draft
   - If it's a new document, enter a filename in the dialog
   - Files are saved to browser localStorage

### Managing Files

#### Create a New File

1. Click the "New" button
2. Start typing in the empty editor
3. Click "Save" or "Save As" to name it

#### Load an Existing File

1. Click the dropdown menu showing "Select a file"
2. Choose a file from the list
3. The file content loads into the editor

#### Save Changes to Existing File

1. Make your edits
2. Click "Save" (updates the current file)

#### Delete a File

1. Open the file dropdown
2. Click the trash icon next to a file name
3. Confirm deletion

### Import & Export

#### Import a Markdown File

1. Click the "Import" button
2. Select a `.md` or `.markdown` file from your computer
3. The file is added to your file list and opened

#### Download a File

1. Open the file you want to download
2. Click the "Download" button
3. The file downloads as `filename.md`

### Markdown Features

#### Text Formatting

- **Bold**: `Ctrl/Cmd + B` or `**text**`
- **Italic**: `Ctrl/Cmd + I` or `*text*`
- **Underline**: `Ctrl/Cmd + U`
- **Strikethrough**: `Ctrl/Cmd + Shift + S` or `~~text~~`
- **Code**: `Ctrl/Cmd + E` or `` `code` ``

#### Headings

```markdown
# Heading 1

## Heading 2

### Heading 3
```

#### Lists

**Bullet List:**

```markdown
- Item 1
- Item 2
  - Nested item
```

**Numbered List:**

```markdown
1. First item
2. Second item
3. Third item
```

**Task List:**

```markdown
- [ ] Unchecked task
- [x] Completed task
```

#### Links

1. Click the link icon in toolbar
2. Enter the URL
3. Click "Add Link"

Or type: `[Link Text](https://example.com)`

#### Images

1. Click the image icon in toolbar
2. Enter the image URL
3. Click "Add Image"

Or type: `![Alt Text](https://example.com/image.jpg)`

#### Blockquotes

```markdown
> This is a blockquote
> It can span multiple lines
```

#### Code Blocks

````markdown
```javascript
function hello() {
  console.log('Hello World');
}
```
````

#### Horizontal Rules

```markdown
---
```

### Tips & Tricks

1. **Auto-save**: Changes save automatically in draft mode
2. **Markdown Preview**: The editor shows rich text, but saves as markdown
3. **Copy as Markdown**: When you copy text, it copies as markdown
4. **Paste Markdown**: Paste markdown text and it converts to rich text
5. **Undo/Redo**: Use the toolbar buttons or Ctrl/Cmd + Z

### Keyboard Shortcuts

| Action    | Windows/Linux    | Mac             |
| --------- | ---------------- | --------------- |
| Bold      | Ctrl + B         | Cmd + B         |
| Italic    | Ctrl + I         | Cmd + I         |
| Underline | Ctrl + U         | Cmd + U         |
| Code      | Ctrl + E         | Cmd + E         |
| Undo      | Ctrl + Z         | Cmd + Z         |
| Redo      | Ctrl + Shift + Z | Cmd + Shift + Z |

### Storage Information

- Files are stored in your browser's localStorage
- Maximum storage: ~5-10 MB
- Data persists until you clear browser data
- Not synced across devices or browsers
- No server required - everything runs locally

### Troubleshooting

**Editor not loading?**

- Check browser console for errors
- Try refreshing the page
- Clear browser cache

**Files not saving?**

- Check if localStorage is enabled
- Check available storage space
- Try a shorter filename

**Formatting not working?**

- Make sure you're using the correct shortcuts
- Try clicking the toolbar buttons
- Check if text is selected

**Lost your draft?**

- Drafts auto-save to localStorage
- Check if browser data was cleared
- Look in the file dropdown for saved versions

### Examples

#### Writing a Blog Post

1. Start with a heading: `# My Blog Post`
2. Add some paragraphs
3. Insert an image: `![Hero Image](url)`
4. Add lists for key points
5. Save as "my-blog-post.md"
6. Download when ready to publish

#### Creating Documentation

1. Use hierarchical headings (H1, H2, H3)
2. Add code blocks for examples
3. Use task lists for TODOs
4. Save multiple related files
5. Download all files when complete

#### Note Taking

1. Start in draft mode
2. Use bullet lists for quick notes
3. Add checkboxes for tasks
4. Save with a descriptive name
5. Load previous notes to review

### Advanced Usage

#### Customizing the Editor

Edit `components/tiptap-markdown-editor.tsx` to:

- Add new extensions
- Customize toolbar
- Change keyboard shortcuts
- Modify styling

#### Adding Extensions

```bash
pnpm add @tiptap/extension-name
```

Then import and add to the extensions array.

#### Styling

Edit `app/globals.css` to customize:

- Editor appearance
- Markdown rendering
- Dark mode colors

### Getting Help

- Check `IMPLEMENTATION.md` for technical details
- Review TipTap documentation: https://tiptap.dev
- Check Next.js docs: https://nextjs.org/docs

### Contributing

Feel free to:

- Add new features
- Fix bugs
- Improve styling
- Add more extensions
- Enhance file management

Happy writing! 📝
