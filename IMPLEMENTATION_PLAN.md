# Implementation Plan: GPT Realtime-Style Chat UI

## Overview
Transform the chat UI to match GPT Realtime style with:
- User messages (transcriptions) on the right side
- AI messages (replies) on the left side  
- Action buttons (copy, thumbs up/down, share) on AI messages
- Modern, polished styling

## Visual Layout

```
┌─────────────────────────────────────────┐
│                                         │
│  [AI Message Bubble]                    │  ← Left side
│  [Copy] [👍] [👎] [Share]               │  ← Action buttons
│                                         │
│                    [User Message Bubble]│  ← Right side
│                                         │
│  [AI Message Bubble]                    │
│  [Copy] [👍] [👎] [Share]               │
│                                         │
└─────────────────────────────────────────┘
```

---

## Step 1: Create MessageActions Component

**File:** `components/livekit/message-actions.tsx`

This component will show action buttons below AI messages.

```tsx
'use client';

import { useState } from 'react';
import { 
  CopySimpleIcon, 
  CaretUpIcon,    // For thumbs up (simpler alternative)
  CaretDownIcon,  // For thumbs down (simpler alternative)
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
```

---

## Step 2: Update ChatEntry Component

**File:** `components/livekit/chat-entry.tsx`

Transform this component with:
- Better bubble styling (darker for user, lighter for AI)
- Action buttons for AI messages
- Improved spacing and typography
- Hide timestamps by default

```tsx
import * as React from 'react';
import { cn } from '@/lib/utils';
import { MessageActions } from './message-actions';

export interface ChatEntryProps extends React.HTMLAttributes<HTMLLIElement> {
  /** The locale to use for the timestamp. */
  locale: string;
  /** The timestamp of the message. */
  timestamp: number;
  /** The message to display. */
  message: string;
  /** The origin of the message. */
  messageOrigin: 'local' | 'remote';
  /** The sender's name. */
  name?: string;
  /** Whether the message has been edited. */
  hasBeenEdited?: boolean;
}

export const ChatEntry = ({
  name,
  locale,
  timestamp,
  message,
  messageOrigin,
  hasBeenEdited = false,
  className,
  ...props
}: ChatEntryProps) => {
  const time = new Date(timestamp);
  const title = time.toLocaleTimeString(locale, { timeStyle: 'full' });
  const isUser = messageOrigin === 'local';
  const isAI = messageOrigin === 'remote';

  return (
    <li
      title={title}
      data-lk-message-origin={messageOrigin}
      className={cn(
        'group flex w-full flex-col gap-1.5 mb-4',
        isUser ? 'items-end' : 'items-start',
        className
      )}
      {...props}
    >
      {/* Message Bubble */}
      <div
        className={cn(
          'relative max-w-[85%] md:max-w-[75%] rounded-2xl px-4 py-2.5',
          'transition-all duration-200',
          isUser
            ? // User message (right side) - dark grey bubble
              'bg-[#2f2f2f] dark:bg-[#1f1f1f] text-white ml-auto'
            : // AI message (left side) - lighter bubble
              'bg-muted dark:bg-[#2a2a2a] text-foreground mr-auto'
        )}
      >
        {/* Message Text */}
        <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">
          {message}
        </p>

        {/* Action Buttons - Only for AI messages */}
        {isAI && <MessageActions message={message} />}
      </div>

      {/* Timestamp - Hidden by default, shown on hover */}
      <span
        className={cn(
          'font-mono text-xs text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity',
          isUser ? 'mr-2' : 'ml-2'
        )}
      >
        {hasBeenEdited && '*'}
        {time.toLocaleTimeString(locale, { timeStyle: 'short' })}
      </span>
    </li>
  );
};
```

---

## Step 3: Update ChatTranscript Component

**File:** `components/app/chat-transcript.tsx`

Minor adjustments for better spacing:

```tsx
'use client';

import { AnimatePresence, type HTMLMotionProps, motion } from 'motion/react';
import { type ReceivedChatMessage } from '@livekit/components-react';
import { ChatEntry } from '@/components/livekit/chat-entry';

const MotionContainer = motion.create('div');
const MotionChatEntry = motion.create(ChatEntry);

const CONTAINER_MOTION_PROPS = {
  variants: {
    hidden: {
      opacity: 0,
      transition: {
        ease: 'easeOut',
        duration: 0.3,
        staggerChildren: 0.1,
        staggerDirection: -1,
      },
    },
    visible: {
      opacity: 1,
      transition: {
        delay: 0.2,
        ease: 'easeOut',
        duration: 0.3,
        stagerDelay: 0.2,
        staggerChildren: 0.1,
        staggerDirection: 1,
      },
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
};

const MESSAGE_MOTION_PROPS = {
  variants: {
    hidden: {
      opacity: 0,
      translateY: 10,
    },
    visible: {
      opacity: 1,
      translateY: 0,
    },
  },
};

interface ChatTranscriptProps {
  hidden?: boolean;
  messages?: ReceivedChatMessage[];
}

export function ChatTranscript({
  hidden = false,
  messages = [],
  ...props
}: ChatTranscriptProps & Omit<HTMLMotionProps<'div'>, 'ref'>) {
  return (
    <AnimatePresence>
      {!hidden && (
        <MotionContainer 
          {...CONTAINER_MOTION_PROPS} 
          className="flex flex-col py-4"
          {...props}
        >
          {messages.map(({ id, timestamp, from, message, editTimestamp }: ReceivedChatMessage) => {
            const locale = navigator?.language ?? 'en-US';
            const messageOrigin = from?.isLocal ? 'local' : 'remote';
            const hasBeenEdited = !!editTimestamp;

            return (
              <MotionChatEntry
                key={id}
                locale={locale}
                timestamp={timestamp}
                message={message}
                messageOrigin={messageOrigin}
                hasBeenEdited={hasBeenEdited}
                {...MESSAGE_MOTION_PROPS}
              />
            );
          })}
        </MotionContainer>
      )}
    </AnimatePresence>
  );
}
```

---

## Step 4: Optional - Update SessionView for Darker Background

**File:** `components/app/session-view.tsx`

Optional: Make the chat area darker for better contrast:

```tsx
// In SessionView component, update the ScrollArea section:

<ScrollArea 
  ref={scrollAreaRef} 
  className="px-4 pt-40 pb-[150px] md:px-6 md:pb-[180px] bg-[#0a0a0a] dark:bg-[#0a0a0a]"
>
  <ChatTranscript
    hidden={!chatOpen}
    messages={messages}
    className="mx-auto max-w-3xl transition-opacity duration-300 ease-out"
  />
</ScrollArea>
```

---

## Step 5: Icon Names Used

Phosphor Icons used (all available in `@phosphor-icons/react/dist/ssr`):
- `CopySimpleIcon` - For copy functionality
- `CaretUpIcon` - For thumbs up (simple up arrow)
- `CaretDownIcon` - For thumbs down (simple down arrow)
- `ShareNetworkIcon` - For share functionality

**Alternative icons if needed:**
- Copy: `CopyIcon`, `ClipboardIcon`
- Thumbs: `HandIcon` (with rotation), `ArrowUpIcon`/`ArrowDownIcon`
- Share: `ShareIcon`, `ExportIcon`

---

## Implementation Order

1. ✅ **Create MessageActions component** - New file
2. ✅ **Update ChatEntry component** - Modify existing
3. ✅ **Update ChatTranscript component** - Minor changes
4. ⚠️ **Test and adjust styling** - Fine-tune colors/spacing
5. ⚠️ **Optional: Update SessionView** - Darker background

---

## Key Design Decisions

1. **User messages (right)**: Dark grey bubble (`#2f2f2f`)
2. **AI messages (left)**: Lighter bubble (using `bg-muted`)
3. **Action buttons**: Only on AI messages, show on hover
4. **Timestamps**: Hidden by default, show on hover
5. **Spacing**: Increased gap between messages (`mb-4`)
6. **Max width**: 85% on mobile, 75% on desktop

---

## Testing Checklist

- [ ] User messages appear on right side
- [ ] AI messages appear on left side
- [ ] Action buttons appear on AI messages only
- [ ] Copy button works
- [ ] Thumbs up/down toggle correctly
- [ ] Share button works (or falls back to copy)
- [ ] Timestamps show on hover
- [ ] Dark mode works correctly
- [ ] Mobile responsive
- [ ] Animations work smoothly

---

## Notes

- All icons use `@phosphor-icons/react/dist/ssr` (already in project)
- Uses existing Tailwind classes and design tokens
- Maintains accessibility with proper button titles
- Follows existing component patterns
- No breaking changes to API

