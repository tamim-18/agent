# 🧪 CartUp Voice Agent - Test Cases

## Quick Test Scenarios (5 minutes)

### Scenario 1: Happy Path - Ticket Creation (English)
```
1. Open application
2. Click microphone
3. Say: "Hello"
4. Say: "English"
5. Say: "I need help with my order"
6. Say: "Order number o302"
7. Say: "The product is damaged"
8. Verify: Ticket created, ID shown conversationally
```

### Scenario 2: Happy Path - Ticket Creation (Bengali)
```
1. Open application
2. Click microphone
3. Say: "হ্যালো"
4. Say: "Bengali"
5. Say: "আমার অর্ডারে সমস্যা আছে"
6. Say: "অর্ডার নম্বর o302"
7. Say: "পণ্যটি ক্ষতিগ্রস্ত"
8. Verify: Ticket created in Bengali, natural response
```

### Scenario 3: Agent Transfer
```
1. Start conversation
2. Say: "I want to check my order status"
3. Verify: Transfers to OrderAgent smoothly
4. Say: "Order o302"
5. Verify: Order status retrieved, context preserved
```

### Scenario 4: UI Features
```
1. Have conversation with multiple messages
2. Verify: User messages on right, AI on left
3. Hover over AI messages
4. Verify: Action buttons appear (copy, thumbs, share)
5. Click copy button
6. Verify: Message copied to clipboard
```

---

## Comprehensive Test Cases

### Category 1: Language Support

#### TC-LANG-001: English Language Selection
**Priority:** High  
**Preconditions:** Application loaded, microphone enabled  
**Steps:**
1. Click microphone button
2. Wait for agent greeting
3. Say: "Hello"
4. Agent offers language selection
5. Say: "English"
**Expected:** Agent responds in English for rest of conversation  
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

#### TC-LANG-002: Bengali Language Selection
**Priority:** High  
**Preconditions:** Application loaded, microphone enabled  
**Steps:**
1. Click microphone button
2. Wait for agent greeting
3. Say: "হ্যালো"
4. Agent offers language selection
5. Say: "Bengali"
**Expected:** Agent responds in Bengali (bn-BD) with cultural greetings  
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

#### TC-LANG-003: Language Persistence
**Priority:** Medium  
**Preconditions:** Language selected (English or Bengali)  
**Steps:**
1. Continue conversation after language selection
2. Ask multiple questions
3. Transfer between agents
**Expected:** Language preference maintained across entire session  
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

---

### Category 2: Ticket Management

#### TC-TICKET-001: Create Ticket - English
**Priority:** High  
**Preconditions:** Language set to English  
**Steps:**
1. Say: "I need help with my order"
2. Agent asks for order ID
3. Say: "Order number o302"
4. Agent asks for issue description
5. Say: "The product arrived damaged"
**Expected:** 
- Ticket created successfully
- Ticket ID provided conversationally (e.g., "I've created ticket t602 for your order o302")
- Not reading raw ticket_id, order_id, status codes
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

#### TC-TICKET-002: Create Ticket - Bengali
**Priority:** High  
**Preconditions:** Language set to Bengali  
**Steps:**
1. Say: "আমার অর্ডারে সমস্যা আছে"
2. Agent asks for order ID
3. Say: "অর্ডার নম্বর o302"
4. Agent asks for issue description
5. Say: "পণ্যটি ক্ষতিগ্রস্ত"
**Expected:** 
- Ticket created successfully
- Response in Bengali: "আমি আপনার o302 নম্বর অর্ডারের জন্য t602 নম্বর টিকেট তৈরি করেছি"
- Natural Bengali expressions used
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

#### TC-TICKET-003: Check Ticket Status
**Priority:** High  
**Preconditions:** Ticket created in previous conversation  
**Steps:**
1. Say: "Can you check my ticket status?"
2. Agent retrieves ticket information
**Expected:** 
- Status retrieved successfully
- Response is conversational (e.g., "Your ticket is currently being reviewed")
- Not reading raw status codes
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

#### TC-TICKET-004: Multiple Tickets
**Priority:** Medium  
**Preconditions:** None  
**Steps:**
1. Create ticket for order o302
2. Create ticket for order o303
3. Ask: "What's the status of my tickets?"
**Expected:** Agent tracks and reports on multiple tickets correctly  
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

#### TC-TICKET-005: Context Preservation
**Priority:** High  
**Preconditions:** Order ID mentioned earlier in conversation  
**Steps:**
1. Mention order ID: "Order o302"
2. Later say: "Create a ticket for this order"
**Expected:** Agent uses previously mentioned order ID, doesn't re-ask  
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

---

### Category 3: Agent Transfers

#### TC-TRANSFER-001: Greeter → Ticket Agent
**Priority:** High  
**Preconditions:** Language selected  
**Steps:**
1. Say: "I want to create a support ticket"
2. Agent transfers to TicketAgent
**Expected:** 
- Smooth transfer, no interruption
- Context preserved (language, user info)
- TicketAgent greets briefly and continues
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

#### TC-TRANSFER-002: Ticket → Order Agent
**Priority:** High  
**Preconditions:** In TicketAgent conversation  
**Steps:**
1. Say: "Actually, I want to check my order status first"
2. Agent transfers to OrderAgent
**Expected:** 
- Smooth transfer
- Order ID remembered if mentioned earlier
- OrderAgent continues conversation naturally
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

#### TC-TRANSFER-003: Order → Returns Agent
**Priority:** Medium  
**Preconditions:** In OrderAgent conversation  
**Steps:**
1. Say: "I want to return this order"
2. Agent transfers to ReturnsAgent
**Expected:** 
- Smooth transfer
- Order context preserved
- ReturnsAgent handles return request
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

#### TC-TRANSFER-004: Multiple Transfers
**Priority:** Medium  
**Preconditions:** None  
**Steps:**
1. Start with GreeterAgent
2. Transfer to TicketAgent
3. Transfer to OrderAgent
4. Transfer back to TicketAgent
**Expected:** All transfers smooth, context maintained throughout  
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

---

### Category 4: UI/UX

#### TC-UI-001: Message Alignment
**Priority:** High  
**Preconditions:** Application loaded  
**Steps:**
1. Send user message
2. Receive AI response
3. Check transcript display
**Expected:** 
- User messages aligned right (dark grey background)
- AI messages aligned left (white/light background)
- Clear visual distinction
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

#### TC-UI-002: Action Buttons Visibility
**Priority:** Medium  
**Preconditions:** AI message in transcript  
**Steps:**
1. Hover over AI message
2. Check for action buttons
**Expected:** 
- Copy, thumbs up, thumbs down, share buttons appear
- Buttons only visible on hover
- Smooth transition
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

#### TC-UI-003: Copy Functionality
**Priority:** Medium  
**Preconditions:** AI message with action buttons visible  
**Steps:**
1. Click copy button
2. Paste in text editor
**Expected:** Message text copied to clipboard correctly  
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

#### TC-UI-004: Thumbs Up/Down
**Priority:** Low  
**Preconditions:** AI message with action buttons visible  
**Steps:**
1. Click thumbs up button
2. Verify visual feedback
3. Click thumbs down button
4. Verify visual feedback
**Expected:** 
- Button state changes on click
- Visual feedback (color change, fill state)
- Can toggle between states
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

#### TC-UI-005: Real-time Updates
**Priority:** High  
**Preconditions:** Active conversation  
**Steps:**
1. Speak to agent
2. Watch transcript area
**Expected:** 
- Messages appear in real-time as conversation progresses
- No delay between speech and transcript
- Smooth scrolling to latest message
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

#### TC-UI-006: Scrolling Behavior
**Priority:** Medium  
**Preconditions:** Long conversation (>10 messages)  
**Steps:**
1. Have long conversation
2. Check scroll behavior
**Expected:** 
- Auto-scrolls to latest message
- Smooth scrolling animation
- Can manually scroll up to see history
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

#### TC-UI-007: Control Bar Visibility
**Priority:** High  
**Preconditions:** Application loaded  
**Steps:**
1. Check bottom control bar
2. Verify buttons present
**Expected:** 
- Microphone button visible
- Chat toggle button visible
- End Call button visible
- Camera and Screen Share buttons NOT visible (commented out)
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

---

### Category 5: Error Handling

#### TC-ERROR-001: Unclear Input
**Priority:** Medium  
**Preconditions:** Active conversation  
**Steps:**
1. Say: "Umm... I think maybe..."
2. Pause
**Expected:** Agent asks for clarification or waits for more input  
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

#### TC-ERROR-002: Missing Required Information
**Priority:** High  
**Preconditions:** In TicketAgent  
**Steps:**
1. Say: "Create a ticket"
2. Don't provide order ID
**Expected:** Agent asks for order ID politely  
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

#### TC-ERROR-003: Invalid Order ID
**Priority:** Medium  
**Preconditions:** In TicketAgent or OrderAgent  
**Steps:**
1. Say: "Order number invalid123"
2. Agent tries to process
**Expected:** Agent handles gracefully, asks to verify order ID  
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

#### TC-ERROR-004: Interruption Handling
**Priority:** High  
**Preconditions:** Agent is speaking  
**Steps:**
1. Start speaking while agent is responding
2. Agent should stop
**Expected:** 
- Agent stops speaking immediately
- Listens to user input
- Responds appropriately to interruption
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

#### TC-ERROR-005: Network Interruption
**Priority:** Medium  
**Preconditions:** Active conversation  
**Steps:**
1. Simulate network disconnection (disable WiFi briefly)
2. Reconnect
**Expected:** 
- Graceful error message shown
- Option to reconnect
- Session can resume
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

---

### Category 6: Performance

#### TC-PERF-001: Response Latency
**Priority:** High  
**Preconditions:** Active conversation  
**Steps:**
1. Speak to agent
2. Measure time until response starts
**Expected:** Response starts within 1-2 seconds  
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

#### TC-PERF-002: Transcription Speed
**Priority:** High  
**Preconditions:** Active conversation  
**Steps:**
1. Speak to agent
2. Watch transcript appear
**Expected:** Transcript appears in real-time, minimal delay  
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

#### TC-PERF-003: Concurrent Conversations
**Priority:** Low  
**Preconditions:** Multiple browser tabs/windows  
**Steps:**
1. Open multiple instances
2. Have conversations simultaneously
**Expected:** All conversations work independently without interference  
**Actual:** [ ] Pass [ ] Fail  
**Notes:** 

---

## Test Execution Checklist

### Before Demo
- [ ] All test cases reviewed
- [ ] Test environment set up
- [ ] Backend running
- [ ] Frontend running
- [ ] API keys configured
- [ ] Microphone permissions granted
- [ ] Browser ready (Chrome/Edge)

### During Demo
- [ ] Run Quick Test Scenarios first
- [ ] Execute high-priority test cases
- [ ] Document any failures
- [ ] Note performance metrics
- [ ] Capture screenshots/video if needed

### After Demo
- [ ] Review test results
- [ ] Document issues found
- [ ] Prioritize fixes
- [ ] Update test cases based on findings

---

## Test Data

### Sample Order IDs
- `o302` - Valid order
- `o303` - Valid order
- `invalid123` - Invalid order (for error testing)

### Sample Ticket IDs
- `t602` - Sample ticket ID
- `t603` - Sample ticket ID

### Sample User IDs
- `u101` - Sample user ID
- `u102` - Sample user ID

### Sample Phrases (English)
- "Hello"
- "I need help with my order"
- "Order number o302"
- "The product is damaged"
- "Can you check my ticket status?"
- "I want to check my order status"

### Sample Phrases (Bengali)
- "হ্যালো"
- "আমার অর্ডারে সমস্যা আছে"
- "অর্ডার নম্বর o302"
- "পণ্যটি ক্ষতিগ্রস্ত"
- "আমার টিকেটের অবস্থা দেখুন"
- "আমার অর্ডারের অবস্থা দেখতে চাই"

---

## Notes

- **Priority Levels:**
  - High: Critical for demo, must work
  - Medium: Important but not critical
  - Low: Nice to have, can skip if time constrained

- **Test Execution:**
  - Focus on High priority tests for demo
  - Run Medium priority if time permits
  - Low priority can be skipped or done post-demo

- **Documentation:**
  - Mark Pass/Fail for each test
  - Add notes for any issues found
  - Screenshot errors if possible

---

**Last Updated:** [Current Date]  
**Version:** 1.0

