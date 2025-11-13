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
            : // AI message (left side) - lighter bubble with white background
              'bg-white dark:bg-[#2a2a2a] text-foreground border border-border/50 shadow-sm mr-auto'
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
