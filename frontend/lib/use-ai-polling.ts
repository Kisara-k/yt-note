/**
 * Custom hook for polling AI enrichment status with proper cleanup
 * Shared between videos and books
 */

import { useEffect, useRef, useCallback } from 'react';
import { useAuth } from './auth-context';
import { API_BASE_URL } from './config';

interface AIFields {
  short_title?: string;
  ai_field_1?: string;
  ai_field_2?: string;
  ai_field_3?: string;
}

interface PollConfig {
  resourceId: string;
  chunkId: number;
  isBook: boolean;
  initialState: {
    short_title?: string;
    ai_field_1?: string;
  };
  onComplete: (fields: AIFields) => void;
  onTimeout: () => void;
  onError: (error: Error) => void;
  maxPolls?: number;
  pollInterval?: number;
}

/**
 * Custom hook to poll for AI enrichment completion
 * Automatically cleans up on unmount or when polling completes
 */
export function useAIPolling() {
  const { getAccessToken } = useAuth();
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const isMountedRef = useRef(true);
  const isPollingRef = useRef(false);

  // Cleanup function
  const cleanup = useCallback(() => {
    console.log('[useAIPolling] Cleaning up polling...');

    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }

    isPollingRef.current = false;
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    isMountedRef.current = true;

    return () => {
      console.log('[useAIPolling] Component unmounting, cleaning up...');
      isMountedRef.current = false;
      cleanup();
    };
  }, [cleanup]);

  /**
   * Load lightweight AI fields for polling check
   */
  const loadAIFields = useCallback(
    async (
      resourceId: string,
      chunkId: number,
      isBook: boolean,
      signal: AbortSignal
    ): Promise<AIFields | null> => {
      try {
        const token = await getAccessToken();
        if (!token) return null;

        const endpoint = isBook
          ? `${API_BASE_URL}/api/book/${resourceId}/chapters/ai-status?chapter_id=${chunkId}`
          : `${API_BASE_URL}/api/chunks/${resourceId}/ai-status?chunk_id=${chunkId}`;

        const response = await fetch(endpoint, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          signal,
        });

        if (!response.ok) {
          console.error(
            '[useAIPolling] Failed to load AI fields:',
            response.status
          );
          return null;
        }

        const data = await response.json();

        return {
          short_title: isBook ? data.chapter_title : data.short_title,
          ai_field_1: data.ai_field_1 || '',
          ai_field_2: '',
          ai_field_3: '',
        };
      } catch (error) {
        if (error instanceof Error && error.name === 'AbortError') {
          console.log('[useAIPolling] Fetch aborted');
          return null;
        }
        console.error('[useAIPolling] Error loading AI fields:', error);
        return null;
      }
    },
    [getAccessToken]
  );

  /**
   * Load complete AI fields after enrichment is detected
   */
  const loadCompleteAIFields = useCallback(
    async (
      resourceId: string,
      chunkId: number,
      isBook: boolean,
      signal: AbortSignal
    ): Promise<AIFields | null> => {
      try {
        const token = await getAccessToken();
        if (!token) {
          console.error('[useAIPolling] No access token');
          return null;
        }

        const endpoint = isBook
          ? `${API_BASE_URL}/api/book/${resourceId}/chapters`
          : `${API_BASE_URL}/api/chunks/${resourceId}`;

        console.log(
          '[useAIPolling] Loading complete AI fields from:',
          endpoint
        );

        const response = await fetch(endpoint, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          signal,
        });

        if (!response.ok) {
          console.error(
            '[useAIPolling] Failed to load complete AI fields:',
            response.status
          );
          return null;
        }

        const data = await response.json();
        console.log('[useAIPolling] Response data:', {
          hasChapters: !!data.chapters,
          hasChunks: !!data.chunks,
          chaptersLength: data.chapters?.length,
          chunksLength: data.chunks?.length,
          chunkId,
          isBook,
        });

        const items = isBook ? data.chapters : data.chunks;

        if (!items || !Array.isArray(items)) {
          console.error('[useAIPolling] Invalid response format:', {
            dataKeys: Object.keys(data),
            itemsType: typeof items,
            isArray: Array.isArray(items),
          });
          return null;
        }

        const item = isBook
          ? items.find((ch: any) => ch.chapter_id === chunkId)
          : items.find((ch: any) => ch.chunk_id === chunkId);

        if (!item) {
          console.error('[useAIPolling] Item not found in list:', {
            chunkId,
            itemIds: items.map((i: any) =>
              isBook ? i.chapter_id : i.chunk_id
            ),
          });
          return null;
        }

        console.log('[useAIPolling] Found item:', {
          chunkId: item.chunk_id || item.chapter_id,
          hasTitle: !!(isBook ? item.chapter_title : item.short_title),
          hasField1: !!item.ai_field_1,
          hasField2: !!item.ai_field_2,
          hasField3: !!item.ai_field_3,
        });

        return {
          short_title: isBook ? item.chapter_title : item.short_title,
          ai_field_1: item.ai_field_1 || '',
          ai_field_2: item.ai_field_2 || '',
          ai_field_3: item.ai_field_3 || '',
        };
      } catch (error) {
        if (error instanceof Error && error.name === 'AbortError') {
          console.log('[useAIPolling] Fetch aborted');
          return null;
        }
        console.error(
          '[useAIPolling] Error loading complete AI fields:',
          error
        );
        return null;
      }
    },
    [getAccessToken]
  );

  /**
   * Check if AI enrichment has completed by comparing fields
   */
  const checkEnrichment = useCallback(
    (
      currentFields: AIFields | null,
      previousState: { short_title?: string; ai_field_1?: string }
    ): boolean => {
      if (!currentFields) return false;

      const titleChanged = Boolean(
        currentFields.short_title !== previousState.short_title &&
          currentFields.short_title &&
          currentFields.short_title.trim().length > 0
      );

      const field1Changed = Boolean(
        currentFields.ai_field_1 !== previousState.ai_field_1 &&
          currentFields.ai_field_1 &&
          currentFields.ai_field_1.trim().length > 0
      );

      const hasNewData = titleChanged || field1Changed;

      console.log('[useAIPolling] Checking enrichment:', {
        titleChanged,
        field1Changed,
        hasNewData,
      });

      return hasNewData;
    },
    []
  );

  /**
   * Start polling for AI enrichment
   */
  const startPolling = useCallback(
    (config: PollConfig) => {
      // Prevent multiple polling instances
      if (isPollingRef.current) {
        console.warn(
          '[useAIPolling] Polling already in progress, ignoring new request'
        );
        return;
      }

      const {
        resourceId,
        chunkId,
        isBook,
        initialState,
        onComplete,
        onTimeout,
        onError,
        maxPolls = 180, // 3 minutes default
        pollInterval = 1000, // 1 second default
      } = config;

      console.log('[useAIPolling] Starting polling...', {
        resourceId,
        chunkId,
        isBook,
      });

      let pollCount = 0;
      let enrichmentComplete = false;
      isPollingRef.current = true;

      pollIntervalRef.current = setInterval(async () => {
        // Skip if already completed or unmounted
        if (enrichmentComplete || !isMountedRef.current) {
          // Don't cleanup here - let the completion handler do it
          return;
        }

        pollCount++;
        console.log(`[useAIPolling] Poll ${pollCount}/${maxPolls}`);

        try {
          // Create new abort controller for this request
          abortControllerRef.current = new AbortController();

          // Load current AI fields
          const currentFields = await loadAIFields(
            resourceId,
            chunkId,
            isBook,
            abortControllerRef.current.signal
          );

          // Check if component unmounted during fetch
          if (!isMountedRef.current) {
            cleanup();
            return;
          }

          // Check if enrichment completed
          if (currentFields && checkEnrichment(currentFields, initialState)) {
            enrichmentComplete = true;
            console.log('[useAIPolling] Enrichment detected!');

            // Clear interval IMMEDIATELY to prevent another tick
            if (pollIntervalRef.current) {
              clearInterval(pollIntervalRef.current);
              pollIntervalRef.current = null;
            }

            // Wait for database write to complete
            await new Promise((resolve) => setTimeout(resolve, 500));

            // Check if still mounted after delay
            if (!isMountedRef.current) {
              cleanup();
              return;
            }

            // Create a NEW abort controller for loading complete fields
            const completeFieldsController = new AbortController();
            abortControllerRef.current = completeFieldsController;

            // Load complete AI fields
            const completeFields = await loadCompleteAIFields(
              resourceId,
              chunkId,
              isBook,
              completeFieldsController.signal
            );

            // Check if component still mounted
            if (!isMountedRef.current) {
              cleanup();
              return;
            }

            // Final cleanup (just abort controller now, interval already cleared)
            if (abortControllerRef.current) {
              abortControllerRef.current = null;
            }
            isPollingRef.current = false;

            if (completeFields) {
              console.log(
                '[useAIPolling] Successfully loaded complete fields, calling onComplete'
              );
              onComplete(completeFields);
            } else {
              console.error('[useAIPolling] Failed to load complete fields');
              onError(new Error('Failed to load complete AI fields'));
            }
          } else if (pollCount >= maxPolls) {
            // Timeout
            console.log('[useAIPolling] Polling timeout');
            cleanup();
            onTimeout();
          }
        } catch (error) {
          if (error instanceof Error && error.name !== 'AbortError') {
            console.error('[useAIPolling] Polling error:', error);
            cleanup();
            onError(error);
          }
        }
      }, pollInterval);
    },
    [cleanup, loadAIFields, loadCompleteAIFields, checkEnrichment]
  );

  /**
   * Stop polling manually
   */
  const stopPolling = useCallback(() => {
    console.log('[useAIPolling] Manually stopping polling...');
    cleanup();
  }, [cleanup]);

  /**
   * Check if currently polling
   */
  const isPolling = useCallback(() => {
    return isPollingRef.current;
  }, []);

  return {
    startPolling,
    stopPolling,
    isPolling,
  };
}
