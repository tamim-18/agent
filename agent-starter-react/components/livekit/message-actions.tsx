'use client';

import { useState } from 'react';
import { 
  CopySimpleIcon, 
  CaretUpIcon,
  CaretDownIcon,
  ShareNetworkIcon 
} from '@phosphor-icons/react/dist/ssr';
import { cn } from '@/lib/utils';

interface MessageActionsProps {
  message: string;
  className?: string;
}

export function MessageActions({ message, className }: MessageActionsProps) {
  const [copied, setCopied] = useState(false);
  const [liked, setLiked] = useState<boolean | null>(null);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleLike = () => {
    setLiked(liked === true ? null : true);
  };

  const handleDislike = () => {
    setLiked(liked === false ? null : false);
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          text: message,
        });
      } catch (err) {
        console.error('Failed to share:', err);
      }
    } else {
      // Fallback: copy to clipboard
      handleCopy();
    }
  };

  return (
    <div className={cn('flex items-center gap-1 mt-1', className)}>
      <button
        onClick={handleCopy}
        className="p-1.5 rounded-md hover:bg-muted transition-colors opacity-0 group-hover:opacity-100"
        title={copied ? 'Copied!' : 'Copy'}
      >
        <CopySimpleIcon 
          size={16} 
          weight={copied ? 'fill' : 'regular'}
          className={cn(
            'text-muted-foreground',
            copied && 'text-primary'
          )}
        />
      </button>
      
      <button
        onClick={handleLike}
        className={cn(
          'p-1.5 rounded-md hover:bg-muted transition-colors opacity-0 group-hover:opacity-100',
          liked === true && 'bg-muted opacity-100'
        )}
        title="Thumbs up"
      >
        <CaretUpIcon 
          size={16} 
          weight={liked === true ? 'fill' : 'regular'}
          className={cn(
            'text-muted-foreground',
            liked === true && 'text-primary'
          )}
        />
      </button>
      
      <button
        onClick={handleDislike}
        className={cn(
          'p-1.5 rounded-md hover:bg-muted transition-colors opacity-0 group-hover:opacity-100',
          liked === false && 'bg-muted opacity-100'
        )}
        title="Thumbs down"
      >
        <CaretDownIcon 
          size={16} 
          weight={liked === false ? 'fill' : 'regular'}
          className={cn(
            'text-muted-foreground',
            liked === false && 'text-destructive'
          )}
        />
      </button>
      
      <button
        onClick={handleShare}
        className="p-1.5 rounded-md hover:bg-muted transition-colors opacity-0 group-hover:opacity-100"
        title="Share"
      >
        <ShareNetworkIcon 
          size={16} 
          weight="regular"
          className="text-muted-foreground"
        />
      </button>
    </div>
  );
}

