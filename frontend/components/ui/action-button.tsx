import { Button } from '@/components/ui/button';
import { Loader2, LucideIcon } from 'lucide-react';
import { ButtonHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

interface ActionButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  loading?: boolean;
  loadingText?: string;
  icon?: LucideIcon;
  children: React.ReactNode;
  disabled?: boolean;
  onClick?: () => void;
  className?: string;
  variant?:
    | 'default'
    | 'destructive'
    | 'outline'
    | 'secondary'
    | 'ghost'
    | 'link';
}

/**
 * Standardized action button used across the application
 * for primary actions like Load YT, Load Book, Subtitles, AI, AI Process
 *
 * All styling is centralized here - modify once to update all instances
 *
 * @param className - Optional additional classes to merge with default styling
 * @param variant - Optional button variant to override default 'default' variant
 */
export const ActionButton = forwardRef<HTMLButtonElement, ActionButtonProps>(
  (
    {
      loading = false,
      loadingText = 'Processing...',
      icon: Icon,
      children,
      disabled,
      onClick,
      className,
      variant = 'outline',
      ...props
    },
    ref
  ) => {
    return (
      <Button
        ref={ref}
        onClick={onClick}
        disabled={disabled || loading}
        variant={variant}
        className={cn('w-[110px] relative', className)}
        {...props}
      >
        {loading ? (
          <div className='flex items-center justify-center w-full pl-5'>
            <Loader2 className='absolute left-3 h-4 w-4 animate-spin' />
            <span>{loadingText}</span>
          </div>
        ) : (
          <div className='flex items-center justify-center w-full pl-5'>
            {Icon && <Icon className='absolute left-3 h-4 w-4' />}
            <span>{children}</span>
          </div>
        )}
      </Button>
    );
  }
);

ActionButton.displayName = 'ActionButton';
