/**
 * Shared JSON parsing utilities for book and chapter data
 */

// Utility to clean JSON (remove trailing commas, comments, etc.)
export function cleanJSON(jsonStr: string): string {
  // Remove trailing commas before closing brackets/braces
  let cleaned = jsonStr.replace(/,(\s*[}\]])/g, '$1');

  // Remove single-line comments (// style)
  cleaned = cleaned.replace(/\/\/.*$/gm, '');

  // Remove multi-line comments (/* */ style)
  cleaned = cleaned.replace(/\/\*[\s\S]*?\*\//g, '');

  // Trim whitespace
  cleaned = cleaned.trim();

  return cleaned;
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
    const lines = cleaned.split('\n').filter((line) => line.trim());
    const objects = [];

    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.startsWith('{') && trimmed.endsWith('}')) {
        // Remove trailing comma if exists
        const cleanLine = trimmed.replace(/,$/, '');
        objects.push(JSON.parse(cleanLine));
      } else if (trimmed.startsWith('{')) {
        // Handle multi-line objects - collect until we find closing brace
        let objStr = trimmed;
        // This is a simplified approach - for complex cases, wrapping in [] already works
        objects.push(JSON.parse(objStr));
      }
    }

    if (objects.length > 0) {
      return objects;
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
