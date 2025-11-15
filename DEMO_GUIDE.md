# 🎤 CartUp Voice Agent - Demo Guide & Test Cases

## 📋 Pre-Demo Checklist

### ✅ Technical Setup (15 minutes before demo)

1. **Backend Agent**
   ```bash
   # Terminal 1: Start the agent
   cd /home/tn-99633/Downloads/livekit-agent
   uv run python -m cartup_agent.main dev
   ```
   - ✅ Verify agent starts without errors
   - ✅ Check logs show "Agent ready" or similar
   - ✅ Ensure microphone permissions are granted

2. **Frontend Application**
   ```bash
   # Terminal 2: Start the frontend
   cd agent-starter-react
   npm run dev
   ```
   - ✅ Open browser to `http://localhost:3000`
   - ✅ Verify UI loads correctly
   - ✅ Check microphone permissions popup appears

3. **Environment Variables**
   - ✅ `OPENAI_API_KEY` is set
   - ✅ `GOOGLE_APPLICATION_CREDENTIALS` or Google Cloud credentials are configured
   - ✅ `DEEPGRAM_API_KEY` is set (if using Deepgram STT)
   - ✅ LiveKit server is running (local or cloud)

4. **Browser Setup**
   - ✅ Use Chrome/Edge (best WebRTC support)
   - ✅ Grant microphone permissions
   - ✅ Test audio output (speakers/headphones)
   - ✅ Close unnecessary tabs to reduce CPU usage

5. **Network**
   - ✅ Stable internet connection
   - ✅ Low latency (< 100ms ideal)
   - ✅ Test WebRTC connection quality

### 🎯 Demo Environment Setup

**Recommended Setup:**
- **Backend**: Running in terminal (visible to audience)
- **Frontend**: Full-screen browser window
- **Audio**: External speakers or headphones for clear audio
- **Backup Plan**: Have screenshots/video ready if live demo fails

---

## 🎬 Demo Flow (15-20 minutes)

### Phase 1: Introduction & Setup (2 minutes)

**What to Show:**
1. Open the application in browser
2. Point out the clean, modern UI
3. Show the control bar (microphone, chat, end call buttons)
4. Explain: "This is a real-time voice AI agent for e-commerce support"

**Key Points to Mention:**
- Built with LiveKit for real-time communication
- Multi-agent architecture (specialized agents for different tasks)
- Supports Bengali and English languages
- Natural conversation flow with interruption handling

---

### Phase 2: Basic Voice Interaction (3 minutes)

**Test Case 1: Initial Greeting & Language Selection**

**Steps:**
1. Click microphone button to start
2. Wait for agent greeting
3. Say: **"Hello"** or **"Hi"**
4. Agent should offer language selection
5. Say: **"Bengali"** or **"English"**

**Expected Result:**
- ✅ Agent greets warmly
- ✅ Offers language selection
- ✅ Responds in selected language
- ✅ Chat transcript shows messages on correct sides (user right, agent left)

**What to Highlight:**
- Real-time transcription appears instantly
- Natural conversation flow
- Language detection and switching
- UI shows messages on opposite sides

**Demo Script:**
> "Notice how the agent greets us and offers language selection. The transcript appears in real-time, with user messages on the right and AI responses on the left, just like modern chat interfaces."

---

### Phase 3: Ticket Creation Workflow (5 minutes)

**Test Case 2: Create Support Ticket**

**Steps:**
1. After language selection, say: **"I need help with my order"** or **"আমার অর্ডারে সমস্যা আছে"** (Bengali)
2. Agent should ask for order details
3. Say: **"Order number o302"** or **"অর্ডার নম্বর o302"**
4. Describe issue: **"My product is damaged"** or **"আমার পণ্যটি ক্ষতিগ্রস্ত"**
5. Agent should create ticket

**Expected Result:**
- ✅ Agent transfers to TicketAgent seamlessly
- ✅ Asks for order ID and issue description
- ✅ Creates ticket successfully
- ✅ Provides ticket ID conversationally (not just reading codes)
- ✅ Shows ticket status in chat transcript

**What to Highlight:**
- Agent transfer happens seamlessly (no interruption)
- Context is preserved across agents
- Conversational responses (not robotic)
- Ticket creation happens in real-time

**Demo Script:**
> "The agent automatically transferred to the ticket specialist. Notice how it remembers our order number and creates the ticket conversationally. The context is preserved across agent transfers."

---

### Phase 4: Advanced Features (5 minutes)

**Test Case 3: Check Ticket Status**

**Steps:**
1. Say: **"Can you check my ticket status?"** or **"আমার টিকেটের অবস্থা দেখুন"**
2. Agent should retrieve ticket status
3. Show conversational response

**Expected Result:**
- ✅ Agent retrieves ticket status
- ✅ Responds conversationally (e.g., "Your ticket is being reviewed")
- ✅ Not just reading database codes

**Test Case 4: Agent Transfer**

**Steps:**
1. Say: **"I want to check my order status"** or **"আমার অর্ডারের অবস্থা দেখতে চাই"**
2. Agent should transfer to OrderAgent
3. Continue conversation seamlessly

**Expected Result:**
- ✅ Smooth agent transfer
- ✅ Context preserved (order ID remembered)
- ✅ No conversation restart

**What to Highlight:**
- Multi-agent architecture working seamlessly
- Context preservation across transfers
- Specialized agents for different tasks

**Demo Script:**
> "Now I'm asking about order status. The system automatically transfers to the Order Agent, but notice how it remembers our previous conversation - the order number is already known."

---

### Phase 5: UI Features (3 minutes)

**Test Case 5: Chat Interface Features**

**Steps:**
1. Show chat transcript scrolling
2. Hover over AI messages to show action buttons
3. Demonstrate copy, thumbs up/down, share buttons
4. Show message alignment (user right, AI left)

**Expected Result:**
- ✅ Messages properly aligned
- ✅ Action buttons appear on hover
- ✅ Smooth scrolling
- ✅ Clean, modern UI

**What to Highlight:**
- GPT Realtime-like UI design
- Interactive message actions
- Responsive design
- Real-time updates

**Demo Script:**
> "The UI is designed to match modern chat interfaces. Notice the action buttons on AI messages - users can copy, rate, or share responses. The layout is clean and responsive."

---

### Phase 6: Edge Cases & Robustness (2 minutes)

**Test Case 6: Interruption Handling**

**Steps:**
1. Start speaking while agent is responding
2. Show how agent stops and listens
3. Continue conversation naturally

**Expected Result:**
- ✅ Agent stops speaking when interrupted
- ✅ Listens to user input
- ✅ Responds appropriately

**Test Case 7: Error Handling**

**Steps:**
1. Say something unclear: **"Umm... I think... maybe..."**
2. Agent should ask for clarification
3. Provide clear information

**Expected Result:**
- ✅ Agent asks clarifying questions
- ✅ Handles ambiguity gracefully
- ✅ Maintains conversation flow

**What to Highlight:**
- Natural conversation handling
- Robust error recovery
- User-friendly experience

---

## 📝 Detailed Test Cases

### Test Case Suite 1: Language Support

#### TC-1.1: English Conversation
**Input:** "Hello, I need help"
**Expected:** Agent responds in English, offers language selection if not set

#### TC-1.2: Bengali Conversation
**Input:** "হ্যালো, আমার সাহায্য দরকার"
**Expected:** Agent responds in Bengali (bn-BD), uses culturally appropriate greetings

#### TC-1.3: Language Switching
**Input:** Start in English, then say "Bengali"
**Expected:** Agent switches to Bengali for rest of conversation

---

### Test Case Suite 2: Ticket Management

#### TC-2.1: Create Ticket - English
**Input:** 
- "I need help with my order"
- "Order o302"
- "Product is damaged"
**Expected:** Ticket created, ID provided conversationally

#### TC-2.2: Create Ticket - Bengali
**Input:**
- "আমার অর্ডারে সমস্যা আছে"
- "অর্ডার o302"
- "পণ্যটি ক্ষতিগ্রস্ত"
**Expected:** Ticket created in Bengali, natural response

#### TC-2.3: Check Ticket Status
**Input:** "What's the status of my ticket?"
**Expected:** Status retrieved and explained conversationally

#### TC-2.4: Multiple Tickets
**Input:** Create multiple tickets, check each
**Expected:** Agent tracks multiple tickets correctly

---

### Test Case Suite 3: Agent Transfers

#### TC-3.1: Greeter → Ticket Agent
**Input:** "I want to create a ticket"
**Expected:** Smooth transfer, context preserved

#### TC-3.2: Ticket → Order Agent
**Input:** "Actually, I want to check my order status"
**Expected:** Transfer to OrderAgent, order ID remembered

#### TC-3.3: Order → Returns Agent
**Input:** "I want to return this order"
**Expected:** Transfer to ReturnsAgent, context maintained

---

### Test Case Suite 4: UI/UX

#### TC-4.1: Message Alignment
**Action:** Send messages and check transcript
**Expected:** User messages right-aligned, AI messages left-aligned

#### TC-4.2: Action Buttons
**Action:** Hover over AI messages
**Expected:** Copy, thumbs up/down, share buttons appear

#### TC-4.3: Real-time Updates
**Action:** Speak and watch transcript
**Expected:** Messages appear in real-time as conversation progresses

#### TC-4.4: Scrolling
**Action:** Long conversation
**Expected:** Auto-scrolls to latest message, smooth scrolling

---

### Test Case Suite 5: Error Handling

#### TC-5.1: Unclear Input
**Input:** "Umm... I think maybe..."
**Expected:** Agent asks for clarification

#### TC-5.2: Missing Information
**Input:** "Create a ticket" (without order ID)
**Expected:** Agent asks for required information

#### TC-5.3: Invalid Order ID
**Input:** "Order number xyz123" (invalid)
**Expected:** Agent handles gracefully, asks to verify

#### TC-5.4: Network Interruption
**Action:** Simulate network issue
**Expected:** Graceful error message, reconnection option

---

## 🎯 Key Points to Emphasize

### Technical Highlights
1. **Real-time Communication**: LiveKit WebRTC for low-latency voice
2. **Multi-Agent Architecture**: Specialized agents for different tasks
3. **Context Preservation**: Seamless handoffs between agents
4. **Language Support**: Bengali and English with cultural context
5. **Modern UI**: GPT Realtime-inspired design

### Business Value
1. **24/7 Support**: Automated customer service
2. **Multilingual**: Serves Bengali and English speakers
3. **Scalable**: Handles multiple conversations simultaneously
4. **User-Friendly**: Natural conversation, no training needed
5. **Cost-Effective**: Reduces support team workload

### Differentiators
1. **Voice-First**: Designed for voice, not just chat
2. **Agent Specialization**: Each agent is expert in its domain
3. **Cultural Awareness**: Bengali responses use appropriate cultural context
4. **Conversational**: Not robotic, natural responses
5. **Real-time**: Instant responses, no delays

---

## 🚨 Troubleshooting Guide

### Issue: Agent Not Responding
**Symptoms:** No audio output, no transcript
**Solutions:**
1. Check backend logs for errors
2. Verify API keys are set
3. Check microphone permissions
4. Restart agent: `Ctrl+C` then restart

### Issue: Poor Audio Quality
**Symptoms:** Choppy audio, delays
**Solutions:**
1. Check network connection
2. Close other applications
3. Use wired connection if possible
4. Check browser console for errors

### Issue: UI Not Loading
**Symptoms:** Blank screen, errors
**Solutions:**
1. Check frontend logs: `npm run dev`
2. Clear browser cache
3. Check browser console for errors
4. Verify port 3000 is available

### Issue: Messages Not Aligning
**Symptoms:** All messages on one side
**Solutions:**
1. Check browser console for errors
2. Verify `useChatMessages` hook is working
3. Check LiveKit participant properties
4. Refresh page

### Issue: Agent Transfer Failing
**Symptoms:** Agent doesn't transfer, repeats questions
**Solutions:**
1. Check backend logs for transfer errors
2. Verify agent names match configuration
3. Check UserData is being passed correctly
4. Review agent transfer logic

---

## 📊 Demo Metrics to Mention

- **Latency**: < 500ms response time
- **Accuracy**: High transcription accuracy (Deepgram/Google STT)
- **Languages**: 2 languages supported (English, Bengali)
- **Agents**: 5 specialized agents (Greeter, Ticket, Order, Returns, Recommend)
- **Uptime**: Designed for 99.9% availability
- **Scalability**: Handles multiple concurrent conversations

---

## 🎤 Presentation Tips

1. **Start Strong**: Begin with a working demo, not setup
2. **Show, Don't Tell**: Let the demo speak for itself
3. **Have Backup**: Screenshots/video ready if live demo fails
4. **Practice**: Run through demo 2-3 times before presentation
5. **Engage Audience**: Ask questions, show real use cases
6. **Time Management**: Keep demo to 15-20 minutes, leave time for Q&A
7. **Highlight Pain Points**: Show how this solves real problems
8. **Be Confident**: You built this, show it with pride!

---

## ✅ Post-Demo Checklist

- [ ] Answer questions from audience
- [ ] Provide contact information for follow-up
- [ ] Share demo recording (if recorded)
- [ ] Collect feedback
- [ ] Note any issues for future improvements

---

## 📞 Quick Reference Commands

```bash
# Start Backend
cd /home/tn-99633/Downloads/livekit-agent
uv run python -m cartup_agent.main dev

# Start Frontend
cd agent-starter-react
npm run dev

# Check Logs
# Backend: Terminal 1
# Frontend: Browser console (F12)
```

---

**Good luck with your presentation! 🚀**

