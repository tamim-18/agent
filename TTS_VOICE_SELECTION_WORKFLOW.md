# TTS Voice Selection Workflow - Agent to Agent Transfer

## Overview

This document describes how Text-to-Speech (TTS) voice selection works when agents transfer from one to another, covering both Bengali (`bn-BD`) and English (`en-IN`) languages.

---

## Current Architecture

### 1. Session-Level TTS Configuration

**Location:** `cartup_agent/main.py` (line 92)

```python
session = AgentSession[UserData](
    userdata=userdata,
    stt=stt_config,
    llm=openai.LLM(model="gpt-4o-mini"),
    tts=google.TTS(voice_name="en-IN-Chirp-HD-F", language="en-IN"),  # Default English TTS
    vad=silero.VAD.load(),
    max_tool_steps=5,
)
```

**Current Behavior:**
- Session-level TTS is hardcoded to English: `en-IN-Chirp-HD-F`
- This is set once during session initialization
- Acts as a default/fallback TTS configuration

---

### 2. Agent-Level TTS Configuration

Each agent has its own TTS configured during initialization in their `__init__` method:

#### GreeterAgent
**Location:** `cartup_agent/agents/greeter_agent.py` (line 33)
```python
tts=google.TTS(voice_name="en-IN-Chirp-HD-F", language="en-IN")
```
- **Voice:** English (India), Female
- **Language:** English

#### OrderAgent
**Location:** `cartup_agent/agents/order_agent.py` (line 43)
```python
tts=google.TTS(voice_name="en-IN-Chirp-HD-D", language="en-IN")
```
- **Voice:** English (India), Male
- **Language:** English

#### TicketAgent
**Location:** `cartup_agent/agents/ticket_agent.py` (line 43)
```python
tts=google.TTS(voice_name="en-IN-Chirp-HD-F", language="en-IN")
```
- **Voice:** English (India), Female
- **Language:** English

#### ReturnAgent
**Location:** `cartup_agent/agents/return_agent.py` (line 44)
```python
tts=google.TTS(voice_name="en-US-Chirp-HD-D", language="en-US")
```
- **Voice:** English (US), Male
- **Language:** English (US variant)

#### RecommendAgent
**Location:** `cartup_agent/agents/recommend_agent.py` (line 47)
```python
tts=google.TTS(voice_name="bn-IN-Chirp3-HD-Pulcherrima", language="bn-IN")
```
- **Voice:** Bengali (India), Female
- **Language:** Bengali

---

### 3. Language Preference Storage

**Location:** `cartup_agent/main.py` (line 54)

```python
userdata = UserData()
userdata.language = language  # Set from room name: "en-IN" or "bn-BD"
```

**Current Behavior:**
- Language preference is extracted from room name at session start
- Stored in `userdata.language`
- Available to all agents via `self.session.userdata.language`

---

### 4. Language-Aware Instructions

**Location:** `cartup_agent/agents/base_agent.py` (lines 50-63)

When an agent becomes active (`on_enter()`), language-specific instructions are injected:

```python
language = userdata.language or "en-IN"

if language == "bn-BD":
    lang_instructions = (
        "IMPORTANT: Respond in Bengali with Bangladesh accent..."
    )
else:
    lang_instructions = (
        "IMPORTANT: Respond in English..."
    )
```

**Current Behavior:**
- LLM receives language instructions in system prompt
- LLM generates responses in the correct language
- But TTS voice doesn't change based on language preference

---

## Current Workflow: Agent Transfer

### Step-by-Step Flow

```
1. User selects language (en-IN or bn-BD) → Frontend
   ↓
2. Language stored in userdata.language → main.py
   ↓
3. Session starts with default English TTS → main.py (line 92)
   ↓
4. First agent (GreeterAgent) becomes active
   ↓
5. BaseAgent.on_enter() called:
   - Reads userdata.language
   - Adds language instructions to LLM prompt
   - LLM generates response in correct language
   - Uses agent's hardcoded TTS voice (English for most agents)
   ↓
6. User requests transfer (e.g., "I want to track my order")
   ↓
7. Current agent calls _transfer_to_agent("order", context)
   ↓
8. OrderAgent becomes active
   ↓
9. OrderAgent.on_enter() called:
   - Reads userdata.language (still "bn-BD" or "en-IN")
   - Adds language instructions to LLM prompt
   - LLM generates response in correct language
   - Uses OrderAgent's hardcoded TTS: en-IN-Chirp-HD-D (English Male)
   ↓
10. TTS speaks response using agent's configured voice
```

---

## Current Limitations

### Issue 1: TTS Voice Doesn't Match Language Preference

**Problem:**
- If user selects Bengali (`bn-BD`), but agent has English TTS configured
- LLM generates Bengali text (correct)
- But TTS speaks it using English voice (incorrect pronunciation)

**Example:**
```
User selects: bn-BD (Bengali)
LLM generates: "আপনার অর্ডার o302 বর্তমানে পেন্ডিং আছে"
TTS voice: en-IN-Chirp-HD-F (English voice)
Result: English voice trying to pronounce Bengali text (poor quality)
```

### Issue 2: Agent TTS is Read-Only

**Location:** `cartup_agent/agents/base_agent.py` (lines 30-33)

```python
# Note: Agent's TTS is read-only and set during initialization.
# The session-level TTS will be used, and we configure language-aware TTS
# by ensuring the agent's instructions include language context.
# For future enhancement, we could update session.tts if supported.
```

**Current Behavior:**
- Agent TTS is set during `__init__` and cannot be changed
- Session TTS is also read-only after initialization
- No dynamic TTS switching based on language preference

### Issue 3: Inconsistent TTS Configuration

**Current State:**
- Most agents use English TTS voices
- Only RecommendAgent uses Bengali TTS (`bn-IN-Chirp3-HD-Pulcherrima`)
- No consistent pattern for language-based voice selection

---

## Available TTS Configuration Helper

**Location:** `cartup_agent/config.py` (lines 50-67)

There's a helper function `get_tts_for_language()` that can return appropriate TTS:

```python
def get_tts_for_language(language: str, voice_name: str = None):
    """
    Returns appropriate TTS instance based on language preference.
    """
    if language == "bn-BD":
        voice = voice_name or BENGALI_TTS_VOICE  # "bn-BD-Chirp3-HD-Achernar"
        return google.TTS(voice_name=voice, language="bn-BD")
    else:
        voice = voice_name or ENGLISH_TTS_VOICE  # "en-IN-Chirp-HD-F"
        return google.TTS(voice_name=voice, language="en-IN")
```

**Current Status:** This function exists but is **NOT being used** for agent TTS configuration.

---

## Bengali TTS Voice Options

**Location:** `cartup_agent/config.py` (lines 72-107)

### Female Voices (bn-BD):
- `bn-BD-Chirp3-HD-Achernar` (Currently configured as default)
- `bn-BD-Chirp3-HD-Aoede`
- `bn-BD-Chirp3-HD-Pulcherrima` (Used by RecommendAgent)
- And 11 more options...

### Male Voices (bn-BD):
- `bn-BD-Chirp3-HD-Achird`
- `bn-BD-Chirp3-HD-Algenib`
- And 14 more options...

---

## English TTS Voice Options

### Currently Used:
- `en-IN-Chirp-HD-F` (Female, India) - GreeterAgent, TicketAgent, Session default
- `en-IN-Chirp-HD-D` (Male, India) - OrderAgent
- `en-US-Chirp-HD-D` (Male, US) - ReturnAgent

---

## How It Currently Works (Summary)

### For English (`en-IN`):
1. User selects English → `userdata.language = "en-IN"`
2. Each agent has English TTS configured
3. LLM generates English text
4. TTS speaks using English voice
5. **Result:** Works correctly ✅

### For Bengali (`bn-BD`):
1. User selects Bengali → `userdata.language = "bn-BD"`
2. Most agents have English TTS configured (problem!)
3. LLM generates Bengali text (correct)
4. TTS tries to speak Bengali using English voice
5. **Result:** Poor pronunciation quality ❌

**Exception:** RecommendAgent has Bengali TTS, so it works correctly for Bengali.

---

## Recommended Solution (Not Yet Implemented)

To fix the Bengali TTS issue, agents should use `get_tts_for_language()` during initialization:

```python
# In each agent's __init__:
from ..config import get_tts_for_language

class OrderAgent(BaseAgent):
    def __init__(self) -> None:
        # Get language-aware TTS (but language not known at init time)
        # This is the challenge - language is set AFTER agents are instantiated
        super().__init__(
            # ... other config ...
            tts=get_tts_for_language("en-IN"),  # Default, but should be dynamic
        )
```

**Challenge:** Language is set in `main.py` AFTER agents are instantiated, so agents can't use language preference during `__init__`.

**Alternative Approach:** Use session-level TTS and update it based on language, but LiveKit may not support dynamic TTS updates.

---

## Current State Summary

| Component | English (`en-IN`) | Bengali (`bn-BD`) |
|-----------|-------------------|-------------------|
| **LLM Response** | ✅ Correct | ✅ Correct |
| **TTS Voice** | ✅ Correct | ❌ Wrong (English voice) |
| **Pronunciation** | ✅ Good | ❌ Poor (English voice pronouncing Bengali) |
| **User Experience** | ✅ Good | ⚠️ Acceptable but not optimal |

---

## Testing Recommendations

### Test Case 1: English Flow
1. Select English language
2. Transfer through multiple agents (Greeter → Order → Ticket)
3. Verify: All agents speak in English with correct pronunciation

### Test Case 2: Bengali Flow
1. Select Bengali language
2. Transfer through multiple agents (Greeter → Order → Ticket)
3. Verify: 
   - LLM generates Bengali text ✅
   - TTS uses English voice (current limitation) ⚠️
   - Pronunciation quality may be poor

### Test Case 3: RecommendAgent (Bengali)
1. Select Bengali language
2. Transfer to RecommendAgent
3. Verify: TTS uses Bengali voice (`bn-IN-Chirp3-HD-Pulcherrima`) ✅

---

## Conclusion

**Current Implementation:**
- Language preference is correctly stored and passed to agents
- LLM generates responses in the correct language
- TTS voice selection is **NOT** language-aware (except RecommendAgent)
- Most agents use hardcoded English TTS voices

**Impact:**
- English users: Full functionality ✅
- Bengali users: LLM works correctly, but TTS pronunciation may be suboptimal ⚠️

**Future Enhancement Needed:**
- Implement dynamic TTS selection based on `userdata.language`
- Update agent TTS configuration to use `get_tts_for_language()`
- Or implement session-level TTS updates if LiveKit supports it





