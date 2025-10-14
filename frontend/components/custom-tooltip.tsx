'use client';

import * as React from 'react';
import * as TooltipPrimitive from '@radix-ui/react-tooltip';
import { cn } from '@/lib/utils';

interface CustomTooltipProps {
  children: React.ReactNode;
  content: React.ReactNode;
  side?: 'top' | 'right' | 'bottom' | 'left';
  sideOffset?: number;
  className?: string;
}

/**
 * A reusable tooltip component with consistent styling.
 * - Always shows at the bottom by default
 * - White background for visibility in dark mode
 * - No outline/border or arrow - clean and simple
 */
export function CustomTooltip({
  children,
  content,
  side = 'bottom',
  sideOffset = 4,
  className,
}: CustomTooltipProps) {
  return (
    <TooltipPrimitive.Provider delayDuration={0}>
      <TooltipPrimitive.Root>
        <TooltipPrimitive.Trigger asChild>{children}</TooltipPrimitive.Trigger>
        <TooltipPrimitive.Portal>
          <TooltipPrimitive.Content
            side={side}
            sideOffset={sideOffset}
            className={cn(
              'z-50 rounded-md px-3 py-1.5 text-xs',
              'bg-white text-gray-900 shadow-lg',
              'dark:bg-white dark:text-gray-900',
              'animate-in fade-in-0 zoom-in-95',
              'data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95',
              className
            )}
          >
            {content}
            {/* No arrow - clean tooltip */}
          </TooltipPrimitive.Content>
        </TooltipPrimitive.Portal>
      </TooltipPrimitive.Root>
    </TooltipPrimitive.Provider>
  );
}
