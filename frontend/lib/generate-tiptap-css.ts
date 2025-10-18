/**
 * Build script to inject Tiptap heading styles into globals.css from markdownStyles
 * Runs automatically via predev/prebuild scripts
 */

import { markdownStyles } from './markdown-styles.js';
import { readFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

const headingStyles = `/* AUTO-GENERATED Tiptap heading styles from lib/markdown-styles.tsx - DO NOT EDIT MANUALLY */
.ProseMirror h1 {
  @apply ${markdownStyles.h1};
}

.ProseMirror h2 {
  @apply ${markdownStyles.h2};
}

.ProseMirror h3 {
  @apply ${markdownStyles.h3};
}

.ProseMirror h4 {
  @apply ${markdownStyles.h4};
}

.ProseMirror h5 {
  @apply ${markdownStyles.h5};
}

.ProseMirror h6 {
  @apply ${markdownStyles.h6};
}
/* END AUTO-GENERATED */`;

const globalsPath = join(__dirname, '..', 'app', 'globals.css');
let globalsContent = readFileSync(globalsPath, 'utf-8');

// Remove old auto-generated section if exists
const startMarker = '/* AUTO-GENERATED Tiptap heading styles';
const endMarker = '/* END AUTO-GENERATED */';
const startIdx = globalsContent.indexOf(startMarker);
if (startIdx !== -1) {
  const endIdx = globalsContent.indexOf(endMarker, startIdx);
  if (endIdx !== -1) {
    // Remove the section AND any leading newlines before it
    let beforeStart = startIdx - 1;
    while (beforeStart >= 0 && globalsContent[beforeStart] === '\n') {
      beforeStart--;
    }
    beforeStart++; // Move back to the first newline (or startIdx if no newlines)

    // Remove any trailing newlines after END marker
    let afterEnd = endIdx + endMarker.length;
    while (
      afterEnd < globalsContent.length &&
      globalsContent[afterEnd] === '\n'
    ) {
      afterEnd++;
    }

    globalsContent =
      globalsContent.slice(0, beforeStart) + globalsContent.slice(afterEnd);
  }
}

// Find where to insert (after .ProseMirror hr section)
const insertAfter = '.dark .ProseMirror hr {\n  border-top-color: #4a5568;\n}';
const insertIdx = globalsContent.indexOf(insertAfter);

if (insertIdx !== -1) {
  const insertPos = insertIdx + insertAfter.length;

  // Check if there are already newlines at the insertion point
  let afterInsertPos = insertPos;
  while (
    afterInsertPos < globalsContent.length &&
    globalsContent[afterInsertPos] === '\n'
  ) {
    afterInsertPos++;
  }

  // Insert with exactly 2 newlines before the heading styles
  globalsContent =
    globalsContent.slice(0, insertPos) +
    '\n\n' +
    headingStyles +
    '\n' +
    globalsContent.slice(afterInsertPos);

  writeFileSync(globalsPath, globalsContent, 'utf-8');
  console.log(
    '✅ Injected Tiptap heading styles into globals.css from markdownStyles'
  );
} else {
  console.error('❌ Could not find insertion point in globals.css');
  process.exit(1);
}
