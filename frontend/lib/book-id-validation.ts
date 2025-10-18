/**
 * Utility functions for book ID validation and normalization
 */

export interface BookIdValidationResult {
  isValid: boolean;
  normalized: string;
  error?: string;
}

/**
 * Validate and normalize book ID
 * - Only allows alphanumeric characters, underscores, and spaces
 * - Consecutive spaces and/or underscores are replaced with a single underscore
 * - Trims whitespace
 * - Converts to lowercase
 *
 * @param bookId - The book ID to validate and normalize
 * @returns Validation result with normalized ID or error message
 *
 * @example
 * validateAndNormalizeBookId(" Book_123 ") // { isValid: true, normalized: "book_123" }
 * validateAndNormalizeBookId("Book__123") // { isValid: true, normalized: "book_123" }
 * validateAndNormalizeBookId("Book  123") // { isValid: true, normalized: "book_123" }
 * validateAndNormalizeBookId("Book_ 123") // { isValid: true, normalized: "book_123" }
 * validateAndNormalizeBookId("My  __  Book") // { isValid: true, normalized: "my_book" }
 * validateAndNormalizeBookId("Book-123") // { isValid: false, error: "..." }
 */
export function validateAndNormalizeBookId(
  bookId: string
): BookIdValidationResult {
  // Trim whitespace
  const trimmed = bookId.trim();

  // Check if empty
  if (!trimmed) {
    return {
      isValid: false,
      normalized: '',
      error: 'Book ID cannot be empty',
    };
  }

  // Check if contains only alphanumeric, underscores, and spaces
  const validPattern = /^[a-zA-Z0-9_ ]+$/;
  if (!validPattern.test(trimmed)) {
    return {
      isValid: false,
      normalized: '',
      error:
        'Book ID can only contain letters, numbers and underscores',
    };
  }

  // Replace any consecutive combination of spaces and underscores with a single underscore
  const withoutConsecutive = trimmed.replace(/[_ ]+/g, '_');

  // Normalize to lowercase
  const normalized = withoutConsecutive.toLowerCase();

  return { isValid: true, normalized };
}
