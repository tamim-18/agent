# 🎤 Demo Quick Reference Card

## ⚡ Quick Start Commands

```bash
# Terminal 1: Backend
cd /home/tn-99633/Downloads/livekit-agent
uv run python -m cartup_agent.main dev

# Terminal 2: Frontend  
cd agent-starter-react
npm run dev

# Browser: http://localhost:3000
```

---

## 🎯 5-Minute Demo Script

### 1. Introduction (30 sec)
- "This is CartUp Voice Agent - real-time AI support"
- Show UI: clean, modern, GPT-like design
- Point out: microphone, chat, end call buttons

### 2. Basic Interaction (1 min)
- Click microphone → Say "Hello"
- Say "English" or "Bengali"
- **Highlight:** Real-time transcription, message alignment

### 3. Ticket Creation (2 min)
- Say: "I need help with my order"
- Say: "Order number o302"
- Say: "The product is damaged"
- **Highlight:** Agent transfer, conversational response, ticket created

### 4. UI Features (1 min)
- Show chat transcript
- Hover over AI messages → show action buttons
- **Highlight:** Copy, rate, share functionality

### 5. Agent Transfer (30 sec)
- Say: "Check my order status"
- **Highlight:** Smooth transfer, context preserved

---

## 📝 Key Phrases to Use

### English
- "Hello"
- "I need help with my order"
- "Order number o302"
- "The product is damaged"
- "Can you check my ticket status?"

### Bengali
- "হ্যালো"
- "আমার অর্ডারে সমস্যা আছে"
- "অর্ডার নম্বর o302"
- "পণ্যটি ক্ষতিগ্রস্ত"
- "আমার টিকেটের অবস্থা দেখুন"

---

## ✅ Pre-Demo Checklist

- [ ] Backend running (Terminal 1)
- [ ] Frontend running (Terminal 2)
- [ ] Browser open: http://localhost:3000
- [ ] Microphone permissions granted
- [ ] Audio output working
- [ ] API keys configured
- [ ] Network stable

---

## 🚨 Quick Troubleshooting

| Issue | Quick Fix |
|-------|-----------|
| No response | Check backend logs, restart agent |
| Poor audio | Check network, close other apps |
| UI not loading | Check frontend logs, clear cache |
| Messages misaligned | Refresh page, check console |

---

## 🎯 Key Points to Emphasize

1. **Real-time**: < 500ms latency
2. **Multi-agent**: Specialized agents for different tasks
3. **Multilingual**: English & Bengali support
4. **Context-aware**: Remembers conversation across transfers
5. **Modern UI**: GPT Realtime-inspired design

---

## 📊 Demo Flow Diagram

```
Start → Language Selection → Greeter Agent
                              ↓
                    User Intent Detected
                              ↓
        ┌───────────┬───────────┬───────────┐
        ↓           ↓           ↓           ↓
    Ticket      Order      Returns    Recommend
    Agent       Agent      Agent      Agent
        ↓           ↓           ↓           ↓
    Create      Check      Process    Provide
    Ticket      Status     Return    Suggestions
```

---

## 💡 Presentation Tips

1. **Start with working demo** - Don't show setup
2. **Show, don't tell** - Let demo speak
3. **Have backup** - Screenshots/video ready
4. **Practice** - Run through 2-3 times
5. **Engage** - Ask audience questions
6. **Time box** - 15-20 min demo, 10 min Q&A

---

## 📞 Emergency Contacts

- **Backend Issues**: Check Terminal 1 logs
- **Frontend Issues**: Check browser console (F12)
- **API Issues**: Verify `.env` file has all keys

---

**Good luck! 🚀**

