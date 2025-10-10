/**
 * File Manager for handling local markdown files
 * Uses browser's File System Access API for file operations
 */

export interface MarkdownFile {
  name: string;
  content: string;
  lastModified: Date;
}

const DRAFT_KEY = 'tiptap-draft-content';
const FILES_KEY = 'tiptap-markdown-files';

/**
 * Save draft content to localStorage
 */
export function saveDraft(content: string): void {
  try {
    localStorage.setItem(DRAFT_KEY, content);
  } catch (error) {
    console.error('Failed to save draft:', error);
  }
}

/**
 * Load draft content from localStorage
 */
export function loadDraft(): string {
  try {
    return localStorage.getItem(DRAFT_KEY) || '';
  } catch (error) {
    console.error('Failed to load draft:', error);
    return '';
  }
}

/**
 * Clear draft content
 */
export function clearDraft(): void {
  try {
    localStorage.removeItem(DRAFT_KEY);
  } catch (error) {
    console.error('Failed to clear draft:', error);
  }
}

/**
 * Get all saved markdown files from localStorage
 */
export function getAllFiles(): MarkdownFile[] {
  try {
    const filesJson = localStorage.getItem(FILES_KEY);
    if (!filesJson) return [];

    const files = JSON.parse(filesJson);
    return files.map((file: any) => ({
      ...file,
      lastModified: new Date(file.lastModified),
    }));
  } catch (error) {
    console.error('Failed to load files:', error);
    return [];
  }
}

/**
 * Save a markdown file to localStorage
 */
export function saveFile(name: string, content: string): void {
  try {
    const files = getAllFiles();
    const existingIndex = files.findIndex((f) => f.name === name);

    const newFile: MarkdownFile = {
      name,
      content,
      lastModified: new Date(),
    };

    if (existingIndex >= 0) {
      files[existingIndex] = newFile;
    } else {
      files.push(newFile);
    }

    localStorage.setItem(FILES_KEY, JSON.stringify(files));
  } catch (error) {
    console.error('Failed to save file:', error);
    throw error;
  }
}

/**
 * Load a specific markdown file
 */
export function loadFile(name: string): MarkdownFile | null {
  try {
    const files = getAllFiles();
    return files.find((f) => f.name === name) || null;
  } catch (error) {
    console.error('Failed to load file:', error);
    return null;
  }
}

/**
 * Delete a markdown file
 */
export function deleteFile(name: string): void {
  try {
    const files = getAllFiles();
    const filteredFiles = files.filter((f) => f.name !== name);
    localStorage.setItem(FILES_KEY, JSON.stringify(filteredFiles));
  } catch (error) {
    console.error('Failed to delete file:', error);
    throw error;
  }
}

/**
 * Download a markdown file to the user's computer
 */
export function downloadFile(name: string, content: string): void {
  try {
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = name.endsWith('.md') ? name : `${name}.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Failed to download file:', error);
    throw error;
  }
}

/**
 * Upload a markdown file from the user's computer
 */
export function uploadFile(): Promise<MarkdownFile> {
  return new Promise((resolve, reject) => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.md,.markdown';

    input.onchange = async (e) => {
      try {
        const file = (e.target as HTMLInputElement).files?.[0];
        if (!file) {
          reject(new Error('No file selected'));
          return;
        }

        const content = await file.text();
        const markdownFile: MarkdownFile = {
          name: file.name,
          content,
          lastModified: new Date(file.lastModified),
        };

        resolve(markdownFile);
      } catch (error) {
        reject(error);
      }
    };

    input.click();
  });
}

/**
 * Validate filename
 */
export function isValidFilename(name: string): boolean {
  // Check for invalid characters
  const invalidChars = /[<>:"/\\|?*\x00-\x1F]/;
  if (invalidChars.test(name)) return false;

  // Check for reserved names (Windows)
  const reserved = /^(con|prn|aux|nul|com[0-9]|lpt[0-9])$/i;
  if (reserved.test(name.replace(/\.[^.]*$/, ''))) return false;

  // Check length
  if (name.length === 0 || name.length > 255) return false;

  return true;
}
