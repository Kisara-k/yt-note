/**
 * Shared markdown rendering styles for consistent display across components
 * Used by both ReactMarkdown (ai-field-display) and Tiptap editor
 *
 * Tiptap headings CSS is auto-generated on dev/build via predev/prebuild scripts
 */

import type { Components } from 'react-markdown';

/**
 * Centralized markdown element styles - SINGLE source of truth
 *
 * IMPORTANT: If you change h1-h6 styles here, you MUST also update
 * the corresponding .ProseMirror h1-h6 styles in app/globals.css
 * to keep the Tiptap editor in sync.
 */
export const markdownStyles = {
  h1: 'text-base font-medium mt-3 mb-2 first:mt-0',
  h2: 'text-sm font-medium mt-2.5 mb-1.5 first:mt-0',
  h3: 'text-xs font-medium mt-2 mb-1 first:mt-0',
  h4: 'text-xs font-semibold mt-2 mb-1 first:mt-0',
  h5: 'text-xs font-semibold mt-1.5 mb-0.5 first:mt-0',
  h6: 'text-xs font-semibold mt-1.5 mb-0.5 first:mt-0',
  p: 'text-xs my-1 leading-relaxed',
  ul: 'text-xs my-1 ml-4 list-disc',
  ol: 'text-xs my-1 ml-4 list-decimal',
  li: 'text-xs my-0.5',
  strong: 'font-bold',
  em: 'italic',
  code: 'text-xs bg-muted px-1 py-0.5 rounded font-mono',
  pre: 'text-xs bg-muted p-2 rounded my-2 overflow-x-auto',
  blockquote:
    'text-xs border-l-2 border-gray-300 dark:border-gray-700 pl-3 my-2 italic',
  a: 'text-xs text-blue-500 hover:underline',
  hr: 'my-2 border-gray-300 dark:border-gray-700',
  table:
    'text-xs min-w-full border-collapse border border-gray-300 dark:border-gray-700',
  thead: 'bg-gray-100 dark:bg-gray-800',
  tr: 'border-b border-gray-300 dark:border-gray-700',
  th: 'text-xs border border-gray-300 dark:border-gray-700 px-3 py-2 text-left font-semibold',
  td: 'text-xs border border-gray-300 dark:border-gray-700 px-3 py-2',
  del: 'line-through',
  img: 'max-w-full h-auto rounded-lg',
};

/**
 * ReactMarkdown component overrides for consistent styling
 * Uses the centralized markdownStyles configuration
 */
export const reactMarkdownComponents: Components = {
  h1: ({ node, ...props }) => <h1 className={markdownStyles.h1} {...props} />,
  h2: ({ node, ...props }) => <h2 className={markdownStyles.h2} {...props} />,
  h3: ({ node, ...props }) => <h3 className={markdownStyles.h3} {...props} />,
  h4: ({ node, ...props }) => <h4 className={markdownStyles.h4} {...props} />,
  h5: ({ node, ...props }) => <h5 className={markdownStyles.h5} {...props} />,
  h6: ({ node, ...props }) => <h6 className={markdownStyles.h6} {...props} />,
  p: ({ node, ...props }) => <p className={markdownStyles.p} {...props} />,
  ul: ({ node, ...props }) => <ul className={markdownStyles.ul} {...props} />,
  ol: ({ node, ...props }) => <ol className={markdownStyles.ol} {...props} />,
  li: ({ node, ...props }) => <li className={markdownStyles.li} {...props} />,
  strong: ({ node, ...props }) => (
    <strong className={markdownStyles.strong} {...props} />
  ),
  em: ({ node, ...props }) => <em className={markdownStyles.em} {...props} />,
  code: ({ node, className, ...props }) => {
    const isInline = !className?.includes('language-');
    return isInline ? (
      <code className={markdownStyles.code} {...props} />
    ) : (
      <code className={`text-xs font-mono ${className || ''}`} {...props} />
    );
  },
  pre: ({ node, ...props }) => (
    <pre className={markdownStyles.pre} {...props} />
  ),
  blockquote: ({ node, ...props }) => (
    <blockquote className={markdownStyles.blockquote} {...props} />
  ),
  a: ({ node, ...props }) => <a className={markdownStyles.a} {...props} />,
  hr: ({ node, ...props }) => <hr className={markdownStyles.hr} {...props} />,
  table: ({ node, ...props }) => (
    <div className='overflow-x-auto my-2'>
      <table className={markdownStyles.table} {...props} />
    </div>
  ),
  thead: ({ node, ...props }) => (
    <thead className={markdownStyles.thead} {...props} />
  ),
  tbody: ({ node, ...props }) => <tbody {...props} />,
  tr: ({ node, ...props }) => <tr className={markdownStyles.tr} {...props} />,
  th: ({ node, ...props }) => <th className={markdownStyles.th} {...props} />,
  td: ({ node, ...props }) => <td className={markdownStyles.td} {...props} />,
  del: ({ node, ...props }) => (
    <del className={markdownStyles.del} {...props} />
  ),
  input: ({ node, ...props }) => (
    <input className='mr-1.5 align-middle' disabled {...props} />
  ),
};
