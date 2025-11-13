import { useMemo } from 'react';
import { Room } from 'livekit-client';
import {
  type ReceivedChatMessage,
  type TextStreamData,
  useChat,
  useRoomContext,
  useTranscriptions,
} from '@livekit/components-react';

function transcriptionToChatMessage(textStream: TextStreamData, room: Room): ReceivedChatMessage {
  // Get the track ID from the transcription (note: key uses dots, not underscores)
  const transcribedTrackId = (textStream.streamInfo.attributes as any)?.['lk.transcribed_track_id'];
  
  // Get local participant's microphone track ID
  const localMicTrack = Array.from(room.localParticipant.audioTrackPublications.values())
    .find(pub => pub.source === 'microphone');
  const localMicTrackId = localMicTrack?.trackSid;
  
  // Determine if this is from the local user's microphone
  const isUserMessage = transcribedTrackId === localMicTrackId;
  
  // Set the "from" participant correctly
  const fromParticipant = isUserMessage
    ? room.localParticipant
    : Array.from(room.remoteParticipants.values()).find(
        (p) => p.identity === textStream.participantInfo.identity
      );

  return {
    id: textStream.streamInfo.id,
    timestamp: textStream.streamInfo.timestamp,
    message: textStream.text,
    from: fromParticipant,
  };
}

export function useChatMessages() {
  const chat = useChat();
  const room = useRoomContext();
  const transcriptions: TextStreamData[] = useTranscriptions();

  const mergedTranscriptions = useMemo(() => {
    const merged: Array<ReceivedChatMessage> = [
      ...transcriptions.map((transcription) => transcriptionToChatMessage(transcription, room)),
      ...chat.chatMessages,
    ];
    return merged.sort((a, b) => a.timestamp - b.timestamp);
  }, [transcriptions, chat.chatMessages, room]);

  return mergedTranscriptions;
}
