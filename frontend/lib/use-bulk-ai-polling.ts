/**
 * Custom hook for polling bulk AI enrichment status (all chunks/chapters)
 * Shared between videos and books
 */

import { useEffect, useRef, useCallback } from 'react';
import { useAuth } from './auth-context';
import { API_BASE_URL } from './config';

interface AIFieldsSnapshot {
  [chunkId: number]: {
    short_title?: string;
    ai_field_1?: string;
  };
}

interface BulkPollConfig {
  resourceId: string;
  isBook: boolean;
  initialState: AIFieldsSnapshot | undefined;
  onComplete: () => void;
  onTimeout: () => void;
  onError: (error: Error) => void;
  maxPolls?: number;
  pollInterval?: number;
}

/**
 * Custom hook to poll for bulk AI enrichment completion
 * Automatically cleans up on unmount or when polling completes
 */
export function useBulkAIPolling() {
  const { getAccessToken } = useAuth();
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const isMountedRef = useRef(true);
  const isPollingRef = useRef(false);

  // Cleanup function
  const cleanup = useCallback(() => {
    console.log('[useBulkAIPolling] Cleaning up polling...');

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
      console.log('[useBulkAIPolling] Component unmounting, cleaning up...');
      isMountedRef.current = false;
      cleanup();
    };
  }, [cleanup]);

  /**
   * Load all AI fields for all chunks/chapters
   */
  const loadAllAIFields = useCallback(
    async (
      resourceId: string,
      isBook: boolean,
      signal: AbortSignal
    ): Promise<AIFieldsSnapshot | null> => {
      try {
        const token = await getAccessToken();
        if (!token) return null;

        const endpoint = isBook
          ? `${API_BASE_URL}/api/book/${resourceId}/chapters/ai-status`
          : `${API_BASE_URL}/api/chunks/${resourceId}/ai-status`;

        const response = await fetch(endpoint, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          signal,
        });

        if (!response.ok) {
          console.error(
            '[useBulkAIPolling] Failed to load AI fields:',
            response.status
          );
          return null;
        }

        const data = await response.json();
        const items = isBook ? data.chapters : data.chunks;

        if (!items || !Array.isArray(items)) {
          console.error('[useBulkAIPolling] Invalid response format');
          return null;
        }

        // Create snapshot
        const snapshot: AIFieldsSnapshot = {};
        items.forEach((item: any) => {
          const id = isBook ? item.chapter_id : item.chunk_id;
          snapshot[id] = {
            short_title: isBook ? item.chapter_title : item.short_title,
            ai_field_1: item.ai_field_1 || '',
          };
        });

        return snapshot;
      } catch (error) {
        if (error instanceof Error && error.name === 'AbortError') {
          console.log('[useBulkAIPolling] Fetch aborted');
          return null;
        }
        console.error('[useBulkAIPolling] Error loading AI fields:', error);
        return null;
      }
    },
    [getAccessToken]
  );

  /**
   * Check if any AI enrichment has completed by comparing snapshots
   */
  const checkBulkEnrichment = useCallback(
    (
      currentSnapshot: AIFieldsSnapshot | null,
      previousSnapshot: AIFieldsSnapshot | undefined
    ): boolean => {
      if (!currentSnapshot || !previousSnapshot) return false;

      // Check if any chunk/chapter has new AI content
      for (const chunkId in currentSnapshot) {
        const current = currentSnapshot[chunkId];
        const previous = previousSnapshot[parseInt(chunkId)];

        if (!previous) continue;

        const titleChanged = Boolean(
          current.short_title !== previous.short_title &&
            current.short_title &&
            current.short_title.trim().length > 0
        );

        const field1Changed = Boolean(
          current.ai_field_1 !== previous.ai_field_1 &&
            current.ai_field_1 &&
            current.ai_field_1.trim().length > 0
        );

        if (titleChanged || field1Changed) {
          console.log(
            '[useBulkAIPolling] Enrichment detected for chunk:',
            chunkId
          );
          return true;
        }
      }

      return false;
    },
    []
  );

  /**
   * Start polling for bulk AI enrichment
   */
  const startPolling = useCallback(
    (config: BulkPollConfig) => {
      // Prevent multiple polling instances
      if (isPollingRef.current) {
        console.warn(
          '[useBulkAIPolling] Polling already in progress, ignoring new request'
        );
        return;
      }

      const {
        resourceId,
        isBook,
        initialState,
        onComplete,
        onTimeout,
        onError,
        maxPolls = 180, // 3 minutes default
        pollInterval = 1000, // 1 second default
      } = config;

      console.log('[useBulkAIPolling] Starting polling...', {
        resourceId,
        isBook,
      });

      let pollCount = 0;
      let enrichmentComplete = false;
      isPollingRef.current = true;

      pollIntervalRef.current = setInterval(async () => {
        // Skip if already completed or unmounted
        if (enrichmentComplete || !isMountedRef.current) {
          cleanup();
          return;
        }

        pollCount++;
        console.log(`[useBulkAIPolling] Poll ${pollCount}/${maxPolls}`);

        try {
          // Create new abort controller for this request
          abortControllerRef.current = new AbortController();

          // Load current AI fields
          const currentSnapshot = await loadAllAIFields(
            resourceId,
            isBook,
            abortControllerRef.current.signal
          );

          // Check if component unmounted during fetch
          if (!isMountedRef.current) {
            cleanup();
            return;
          }

          // Check if enrichment completed
          if (
            currentSnapshot &&
            checkBulkEnrichment(currentSnapshot, initialState)
          ) {
            enrichmentComplete = true;
            console.log('[useBulkAIPolling] Bulk enrichment detected!');

            cleanup();
            onComplete();
          } else if (pollCount >= maxPolls) {
            // Timeout
            console.log('[useBulkAIPolling] Polling timeout');
            cleanup();
            onTimeout();
          }
        } catch (error) {
          if (error instanceof Error && error.name !== 'AbortError') {
            console.error('[useBulkAIPolling] Polling error:', error);
            cleanup();
            onError(error);
          }
        }
      }, pollInterval);
    },
    [cleanup, loadAllAIFields, checkBulkEnrichment]
  );

  /**
   * Stop polling manually
   */
  const stopPolling = useCallback(() => {
    console.log('[useBulkAIPolling] Manually stopping polling...');
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
