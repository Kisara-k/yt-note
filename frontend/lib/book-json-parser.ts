/**
 * Shared JSON parsing utilities for book and chapter data
 */

// Utility to clean JSON (remove trailing commas, comments, etc.)
export function cleanJSON(jsonStr: string): string {
  // Remove trailing commas before closing brackets/braces
  let cleaned = jsonStr.replace(/,(\s*[}\]])/g, '$1');

  // Remove comments (both // and /* */) but respect string literals.
  // Use a state machine to avoid stripping '//' sequences inside strings
  let out = '';
  let inString = false;
  let esc = false;
  for (let i = 0; i < cleaned.length; i++) {
    const ch = cleaned[i];

    if (inString) {
      out += ch;
      if (esc) {
        esc = false;
      } else if (ch === '\\') {
        esc = true;
      } else if (ch === '"') {
        inString = false;
      }
      continue;
    }

    // not in string
    if (ch === '"') {
      inString = true;
      out += ch;
      continue;
    }

    // single-line comment
    if (ch === '/' && cleaned[i + 1] === '/') {
      // skip until end of line
      i += 2;
      while (i < cleaned.length && cleaned[i] !== '\n') i++;
      continue;
    }

    // multi-line comment
    if (ch === '/' && cleaned[i + 1] === '*') {
      i += 2;
      while (
        i < cleaned.length &&
        !(cleaned[i] === '*' && cleaned[i + 1] === '/')
      )
        i++;
      i++; // skip the '/'
      continue;
    }

    out += ch;
  }

  cleaned = out.trim();

  return cleaned;
}

// Escape literal newlines inside JSON string literals so that JSON.parse
// doesn't fail on files that contain unescaped newlines inside quoted values.
function escapeNewlinesInStrings(src: string): string {
  let out = '';
  let inString = false;
  let esc = false;

  for (let i = 0; i < src.length; i++) {
    const ch = src[i];

    if (!inString) {
      if (ch === '"') {
        inString = true;
        out += ch;
        esc = false;
        continue;
      }
      out += ch;
      continue;
    }

    // inString === true
    if (esc) {
      // previous char was backslash, keep both
      out += ch;
      esc = false;
      continue;
    }

    if (ch === '\\') {
      out += ch;
      esc = true;
      continue;
    }

    if (ch === '"') {
      inString = false;
      out += ch;
      continue;
    }

    // Replace raw CR/LF inside string with \n escape so JSON.parse accepts it
    if (ch === '\n') {
      out += '\\n';
      continue;
    }
    if (ch === '\r') {
      // skip CR (will be handled by LF or add explicit \n)
      out += '\\r';
      continue;
    }

    out += ch;
  }

  return out;
}

// Extract top-level JSON objects by matching braces while respecting strings.
function extractTopLevelObjects(text: string): string[] {
  const objects: string[] = [];
  let depth = 0;
  let inString = false;
  let esc = false;
  let start = -1;

  for (let i = 0; i < text.length; i++) {
    const ch = text[i];

    if (inString) {
      if (esc) {
        esc = false;
      } else if (ch === '\\') {
        esc = true;
      } else if (ch === '"') {
        inString = false;
      }
      continue;
    }

    if (ch === '"') {
      inString = true;
      continue;
    }

    if (ch === '{') {
      if (depth === 0) start = i;
      depth++;
      continue;
    }

    if (ch === '}') {
      depth--;
      if (depth === 0 && start !== -1) {
        objects.push(text.slice(start, i + 1));
        start = -1;
      }
      continue;
    }
  }

  return objects;
}

// Parse JSON that may or may not be wrapped in an array
export function parseFlexibleJSON(jsonStr: string): any[] {
  let cleaned = cleanJSON(jsonStr);

  // Remove trailing comma at the very end (for formats like: {...}, {...},)
  cleaned = cleaned.replace(/,\s*$/, '');

  // Try parsing as-is first
  try {
    const parsed = JSON.parse(cleaned);
    if (Array.isArray(parsed)) {
      return parsed;
    }
    // If it's a single object, wrap it in an array
    if (typeof parsed === 'object' && parsed !== null) {
      return [parsed];
    }
  } catch (e) {
    // If parsing fails, it might be multiple objects separated by commas or newlines
  }

  // Try escaping literal newlines inside string literals and parse again
  try {
    const sanitized = escapeNewlinesInStrings(cleaned);
    const parsed = JSON.parse(sanitized);
    if (Array.isArray(parsed)) return parsed;
    if (typeof parsed === 'object' && parsed !== null) return [parsed];
  } catch (e) {
    // fall through to other strategies
  }

  // Try wrapping in array brackets (for formats like: {...}, {...})
  if (!cleaned.startsWith('[')) {
    try {
      const wrapped = `[${cleaned}]`;
      const parsed = JSON.parse(wrapped);
      if (Array.isArray(parsed)) {
        return parsed;
      }
    } catch (e) {
      // Still failed, try line-separated approach
    }
  }

  // Try parsing as newline-separated JSON objects (for formats like: {...}\n{...}\n)
  try {
    // Use a robust top-level object extractor that matches braces while
    // respecting string literals. This works for large, multi-line objects.
    const objs = extractTopLevelObjects(cleaned);
    if (objs.length > 0) {
      const parsedObjs: any[] = [];
      for (const o of objs) {
        // sanitize each object's strings as well
        const sanitized = escapeNewlinesInStrings(o);
        parsedObjs.push(JSON.parse(sanitized));
      }
      return parsedObjs;
    }
  } catch (e) {
    // Failed
  }

  // Last resort: throw original error
  throw new Error(
    'Unable to parse JSON. Try wrapping in [] or ensure valid JSON format.'
  );
}

// Normalize chapter data (handle different field names)
export function normalizeChapters(
  chapters: any[]
): Array<{ title: string; content: string }> {
  return chapters
    .map((ch, idx) => {
      // Handle different field name variations
      const title =
        ch.title ||
        ch.chapter_title ||
        ch.name ||
        ch.heading ||
        `Chapter ${idx + 1}`;
      const content = ch.content || ch.chapter_text || ch.text || ch.body || '';

      return {
        title: String(title).trim(),
        content: String(content).trim(),
      };
    })
    .filter((ch) => ch.content); // Only keep chapters with actual content
}

/**
 * Parse and normalize chapters from JSON string
 * Throws error with descriptive message if parsing fails
 */
export function parseAndNormalizeChapters(
  chaptersJson: string
): Array<{ title: string; content: string }> {
  let chaptersData;
  try {
    // Use flexible parser that handles both formats:
    // - [{...}, {...}]
    // - {...}, {...}
    // - {...}\n{...}
    chaptersData = parseFlexibleJSON(chaptersJson);

    if (!Array.isArray(chaptersData)) {
      throw new Error('Unable to parse as array of chapters');
    }
  } catch (err) {
    const errMsg = err instanceof Error ? err.message : 'Unknown error';
    throw new Error(
      `Invalid JSON format: ${errMsg}\n\nAccepted formats:\n` +
        `1. Array: [{"title": "...", "content": "..."}, ...]\n` +
        `2. Comma-separated: {...}, {...}, {...}\n` +
        `3. Line-separated: {...}\\n{...}\\n{...}`
    );
  }

  // Normalize chapters (handle different field names, remove empty ones)
  const normalizedChapters = normalizeChapters(chaptersData);

  if (normalizedChapters.length === 0) {
    throw new Error(
      'No valid chapters found. Each chapter must have content (fields: content, chapter_text, text, or body).'
    );
  }

  // Validate each chapter has both title and content
  const missingFields = [];
  for (let i = 0; i < normalizedChapters.length; i++) {
    const chapter = normalizedChapters[i];
    const chapterNum = i + 1;

    if (!chapter.title || !chapter.title.trim()) {
      missingFields.push(`Chapter ${chapterNum}: empty title`);
    }
    if (!chapter.content || !chapter.content.trim()) {
      missingFields.push(`Chapter ${chapterNum}: empty content`);
    }
  }

  if (missingFields.length > 0) {
    throw new Error(`Invalid chapters:\n${missingFields.join('\n')}`);
  }

  return normalizedChapters;
}
