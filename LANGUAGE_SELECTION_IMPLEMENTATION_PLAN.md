# Language Selection Implementation Plan

## 🎯 Objective
Implement frontend language selection before call starts, and configure STT based on selected language to prevent transcription errors (English being transcribed as Bengali/Hindi).

---

## 📋 Current Problem

1. **STT is hardcoded to Bengali** (`bn-BD`) in `cartup_agent/main.py`
2. When users speak English, STT transcribes it as Bengali/Hindi
3. LLM fixes the issue, but transcriptions look wrong to users
4. LiveKit Google STT doesn't support multiple languages like `["en-IN", "bn-BD"]` in single config

---

## 🏗️ Architecture Overview

```
User selects language (Frontend)
    ↓
Language passed in API request
    ↓
Backend includes language in room name
    ↓
Agent extracts language from room name
    ↓
STT configured based on language
    ↓
UserData.language set upfront
```

---

## 📝 Implementation Steps

### **Step 1: Frontend - Add Language Selector UI**

**File:** `agent-starter-react/components/app/welcome-view.tsx`

**Changes:**
- Add language selection UI (radio buttons or dropdown)
- Store selected language in component state
- Pass language to `onStartCall` callback

**Code Example:**
```tsx
interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: (language: 'en-IN' | 'bn-BD') => void; // Updated signature
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  const [selectedLanguage, setSelectedLanguage] = useState<'en-IN' | 'bn-BD'>('en-IN');

  return (
    <div ref={ref}>
      <section className="bg-background flex flex-col items-center justify-center text-center">
        <WelcomeImage />

        <p className="text-foreground max-w-prose pt-1 leading-6 font-medium">
          Chat live with CartUp voice assistant
        </p>

        {/* Language Selection */}
        <div className="mt-4 flex flex-col gap-3">
          <p className="text-sm text-muted-foreground">Select your language:</p>
          <div className="flex gap-4 justify-center">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="language"
                value="en-IN"
                checked={selectedLanguage === 'en-IN'}
                onChange={(e) => setSelectedLanguage(e.target.value as 'en-IN' | 'bn-BD')}
                className="w-4 h-4"
              />
              <span className="text-sm">English</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="language"
                value="bn-BD"
                checked={selectedLanguage === 'bn-BD'}
                onChange={(e) => setSelectedLanguage(e.target.value as 'en-IN' | 'bn-BD')}
                className="w-4 h-4"
              />
              <span className="text-sm">বাংলা (Bengali)</span>
            </label>
          </div>
        </div>

        <Button 
          variant="primary" 
          size="lg" 
          onClick={() => onStartCall(selectedLanguage)} 
          className="mt-6 w-64 font-mono"
        >
          {startButtonText}
        </Button>
      </section>

      {/* Footer remains same */}
    </div>
  );
};
```

---

### **Step 2: Frontend - Update useRoom Hook**

**File:** `agent-starter-react/hooks/useRoom.ts`

**Changes:**
- Update `startSession` to accept language parameter
- Include language in TokenSource fetch body

**Code Example:**
```typescript
export function useRoom(appConfig: AppConfig) {
  // ... existing code ...

  const tokenSource = useMemo(
    () =>
      TokenSource.custom(async (options?: { agentName?: string; language?: string }) => {
        const url = new URL(
          process.env.NEXT_PUBLIC_CONN_DETAILS_ENDPOINT ?? '/api/connection-details',
          window.location.origin
        );

        try {
          const res = await fetch(url.toString(), {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-Sandbox-Id': appConfig.sandboxId ?? '',
            },
            body: JSON.stringify({
              language: options?.language || 'en-IN', // Add language to request
              room_config: options?.agentName
                ? {
                    agents: [{ agent_name: options.agentName }],
                  }
                : undefined,
            }),
          });
          return await res.json();
        } catch (error) {
          console.error('Error fetching connection details:', error);
          throw new Error('Error fetching connection details!');
        }
      }),
    [appConfig]
  );

  const startSession = useCallback((language: 'en-IN' | 'bn-BD' = 'en-IN') => {
    setIsSessionActive(true);

    if (room.state === 'disconnected') {
      const { isPreConnectBufferEnabled } = appConfig;
      Promise.all([
        room.localParticipant.setMicrophoneEnabled(true, undefined, {
          preConnectBuffer: isPreConnectBufferEnabled,
        }),
        tokenSource
          .fetch({ agentName: appConfig.agentName, language }) // Pass language
          .then((connectionDetails) =>
            room.connect(connectionDetails.serverUrl, connectionDetails.participantToken)
          ),
      ]).catch((error) => {
        // ... existing error handling ...
      });
    }
  }, [room, appConfig, tokenSource]);

  // ... rest of the code ...
}
```

---

### **Step 3: Frontend - Update ViewController**

**File:** `agent-starter-react/components/app/view-controller.tsx`

**Changes:**
- Update `onStartCall` to accept language parameter
- Pass language to `startSession`

**Code Example:**
```tsx
export function ViewController() {
  const room = useRoomContext();
  const isSessionActiveRef = useRef(false);
  const { appConfig, isSessionActive, startSession } = useSession();

  // ... existing code ...

  return (
    <AnimatePresence mode="wait">
      {!isSessionActive && (
        <MotionWelcomeView
          key="welcome"
          {...VIEW_MOTION_PROPS}
          startButtonText={appConfig.startButtonText}
          onStartCall={(language) => startSession(language)} // Pass language
        />
      )}
      {/* ... rest of the code ... */}
    </AnimatePresence>
  );
}
```

---

### **Step 4: Backend API - Accept and Process Language**

**File:** `agent-starter-react/app/api/connection-details/route.ts`

**Changes:**
- Extract `language` from request body
- Include language in room name pattern

**Code Example:**
```typescript
export async function POST(req: Request) {
  try {
    // ... existing validation ...

    // Parse agent configuration and language from request body
    const body = await req.json();
    const agentName: string = body?.room_config?.agents?.[0]?.agent_name;
    const language: string = body?.language || 'en-IN'; // Extract language, default to en-IN

    // Validate language
    const validLanguages = ['en-IN', 'bn-BD'];
    const selectedLanguage = validLanguages.includes(language) ? language : 'en-IN';

    // Generate participant token
    const participantName = 'user';
    const participantIdentity = `voice_assistant_user_${Math.floor(Math.random() * 10_000)}`;
    
    // Include language in room name: pattern "voice_assistant_room_{language}_{random}"
    const roomName = `voice_assistant_room_${selectedLanguage}_${Math.floor(Math.random() * 10_000)}`;

    const participantToken = await createParticipantToken(
      { identity: participantIdentity, name: participantName },
      roomName,
      agentName
    );

    // Return connection details
    const data: ConnectionDetails = {
      serverUrl: LIVEKIT_URL,
      roomName,
      participantToken: participantToken,
      participantName,
    };
    
    // ... rest of the code ...
  } catch (error) {
    // ... error handling ...
  }
}
```

---

### **Step 5: Agent - Extract Language from Room Name**

**File:** `cartup_agent/main.py`

**Changes:**
- Extract language from room name
- Configure STT based on language
- Set UserData.language upfront

**Code Example:**
```python
async def entrypoint(ctx: JobContext):
    """Entry point for the CartUp voice agent."""
    logger.info(f"CartUp agent started in room: {ctx.room.name}")
    
    # Extract language from room name
    # Room name pattern: "voice_assistant_room_{language}_{random}"
    room_name_parts = ctx.room.name.split('_')
    language = "en-IN"  # Default fallback
    
    # Try to extract language from room name
    if len(room_name_parts) >= 4 and room_name_parts[-2] in ["en-IN", "bn-BD"]:
        language = room_name_parts[-2]
    elif len(room_name_parts) >= 3:
        # Fallback: check if any part matches language codes
        for part in room_name_parts:
            if part in ["en-IN", "bn-BD"]:
                language = part
                break
    
    logger.info(f"Detected language from room name: {language}")
    
    # Initialize database with sample data
    init_database()
    logger.info("Database initialized")
    
    # Create session state
    userdata = UserData()
    userdata.language = language  # Set language upfront
    
    # Instantiate all agents
    userdata.agents.update({
        "greeter": GreeterAgent(),
        "order": OrderAgent(),
        "ticket": TicketAgent(),
        "returns": ReturnAgent(),
        "recommend": RecommendAgent(),
    })
    logger.info("All agents instantiated")
    
    # Configure STT based on language
    if language == "bn-BD":
        # Bengali STT configuration
        stt_config = google.STT(
            model="chirp_2",  # Bengali model
            location="asia-northeast1",  # Required location for chirp_2 with Bengali
            languages=["bn-BD"],  # Bangladesh Bengali
            detect_language=False,  # Disable auto-detection since we know the language
        )
        logger.info("Configured STT for Bengali (bn-BD)")
    else:
        # English STT configuration
        stt_config = google.STT(
            model="chirp_2",  # English model (verify available models)
            location="asia-northeast1",  # May need different location for English
            languages=["en-IN"],  # English (India)
            detect_language=False,  # Disable auto-detection
        )
        logger.info("Configured STT for English (en-IN)")
    
    # Configure voice pipeline
    session = AgentSession[UserData](
        userdata=userdata,
        stt=stt_config,
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=google.TTS(voice_name="en-IN-Chirp-HD-F", language="en-IN"),  # Default, will be overridden per agent
        vad=silero.VAD.load(),
        max_tool_steps=5,
    )
    
    # Start session with greeter agent
    await session.start(
        agent=userdata.agents["greeter"],
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    
    logger.info(f"Session started with greeter agent (Language: {language})")
```

---

### **Step 6: Update Greeter Agent (Optional)**

**File:** `cartup_agent/agents/greeter_agent.py`

**Changes:**
- Skip language selection if language is already set
- Greet directly in the selected language

**Code Example:**
```python
class GreeterAgent(BaseAgent):
    """Greeter agent that routes users to specialized agents."""
    
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are CartUp's friendly voice assistant.\n"
                "FIRST, check if the user has selected a language preference (check userdata.language). "
                "If language is already set (en-IN or bn-BD), greet the user warmly in that language and figure out what they need, then route them.\n"
                "If no language is set (should not happen in normal flow), offer language selection: 'Would you like to continue in English or Bengali? Please say English or Bengali.' "
                "When the user responds with their choice, call the set_language tool with 'en-IN' for English or 'bn-BD' for Bangladesh Bengali.\n"
                "After language is selected, greet the caller warmly in the selected language and figure out what they need, then route them.\n"
                "If they want: order tracking/modification ⇒ OrderAgent; issue/ticket ⇒ TicketAgent; "
                "returns/refunds ⇒ ReturnAgent; recommendations ⇒ RecommendAgent.\n"
                "Ask for user_id or order_id when needed and call the appropriate tools.\n"
                "Always respond in the user's selected language. "
                "If language is 'bn-BD', respond in Bangladesh Bengali with authentic Bangladesh accent, pronunciation, and cultural context. "
                "If 'en-IN', respond in English."
            ),
            tools=[set_user, set_current_order, set_language],
            llm=openai.LLM(model="gpt-4o-mini"),
            tts=google.TTS(voice_name="en-IN-Chirp-HD-F", language="en-IN"),
        )
```

---

## 📁 Files to Modify

### Frontend Files:
1. ✅ `agent-starter-react/components/app/welcome-view.tsx` - Add language selector UI
2. ✅ `agent-starter-react/hooks/useRoom.ts` - Accept and pass language
3. ✅ `agent-starter-react/components/app/view-controller.tsx` - Update callback
4. ✅ `agent-starter-react/app/api/connection-details/route.ts` - Process language

### Backend Files:
5. ✅ `cartup_agent/main.py` - Extract language and configure STT

### Optional Files:
6. ⚠️ `cartup_agent/agents/greeter_agent.py` - Update instructions (optional)

---

## 🔍 Testing Checklist

### Frontend Testing:
- [ ] Language selector appears on welcome screen
- [ ] Default language is English (en-IN)
- [ ] User can select Bengali (bn-BD)
- [ ] Language selection persists until call starts
- [ ] Language is passed correctly to API

### Backend Testing:
- [ ] API accepts language in request body
- [ ] Room name includes language pattern
- [ ] Default language (en-IN) works if language not provided
- [ ] Invalid language falls back to en-IN

### Agent Testing:
- [ ] Agent extracts language from room name correctly
- [ ] STT configured for Bengali when bn-BD selected
- [ ] STT configured for English when en-IN selected
- [ ] UserData.language is set correctly
- [ ] English speech transcribed correctly (no Bengali/Hindi)
- [ ] Bengali speech transcribed correctly
- [ ] Greeter agent greets in correct language

---

## ⚠️ Important Notes

### STT Model Configuration:
1. **Bengali (bn-BD):**
   - Model: `chirp_2` (verify availability)
   - Location: `asia-northeast1`
   - Languages: `["bn-BD"]`

2. **English (en-IN):**
   - Model: `chirp_2` or alternative (verify availability)
   - Location: `asia-northeast1` or alternative (verify)
   - Languages: `["en-IN"]`

### Room Name Pattern:
- Pattern: `voice_assistant_room_{language}_{random}`
- Example: `voice_assistant_room_en-IN_1234`
- Example: `voice_assistant_room_bn-BD_5678`

### Fallback Behavior:
- If language extraction fails → Default to `en-IN`
- If invalid language provided → Default to `en-IN`
- If STT model unavailable → Log error and use default

---

## 🚀 Implementation Order

1. **Phase 1: Frontend UI** (Steps 1-3)
   - Add language selector
   - Update hooks and callbacks
   - Test UI interaction

2. **Phase 2: Backend API** (Step 4)
   - Update API to accept language
   - Include in room name
   - Test API endpoint

3. **Phase 3: Agent Configuration** (Step 5)
   - Extract language from room name
   - Configure STT conditionally
   - Test with both languages

4. **Phase 4: Optional Updates** (Step 6)
   - Update greeter agent instructions
   - Test end-to-end flow

---

## 📊 Expected Outcomes

### Before Implementation:
- ❌ STT always configured for Bengali
- ❌ English speech transcribed as Bengali/Hindi
- ❌ Users see incorrect transcriptions
- ❌ LLM has to correct transcription errors

### After Implementation:
- ✅ STT configured based on user selection
- ✅ English speech transcribed correctly as English
- ✅ Bengali speech transcribed correctly as Bengali
- ✅ Users see accurate transcriptions
- ✅ No LLM correction needed for transcription

---

## 🔧 Configuration Variables Needed

Before implementation, verify:
- [ ] Bengali STT model name (currently `chirp_2`)
- [ ] Bengali STT location (currently `asia-northeast1`)
- [ ] English STT model name (may be `chirp_2` or different)
- [ ] English STT location (may be `asia-northeast1` or different)

---

## 📝 Code Review Checklist

- [ ] All TypeScript types are correct
- [ ] Error handling is in place
- [ ] Default fallbacks are implemented
- [ ] Logging is added for debugging
- [ ] Room name pattern is consistent
- [ ] Language validation is performed
- [ ] STT configuration matches selected language

---

## 🎯 Success Criteria

1. ✅ User can select language before starting call
2. ✅ Selected language is passed to backend
3. ✅ Agent receives language from room name
4. ✅ STT is configured for selected language
5. ✅ English speech is transcribed as English (not Bengali)
6. ✅ Bengali speech is transcribed as Bengali
7. ✅ Transcriptions are accurate and match spoken language

---

**Ready for Implementation:** ✅ Yes

**Estimated Time:** 2-4 hours

**Risk Level:** Low-Medium (depends on STT model availability)


