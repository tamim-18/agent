# CartUp Agent Flow & Architecture Documentation

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Agent Flow & Lifecycle](#agent-flow--lifecycle)
4. [Context Handoff Mechanism](#context-handoff-mechanism)
5. [Agent Transfer Process](#agent-transfer-process)
6. [Technical Implementation](#technical-implementation)
7. [Data Flow](#data-flow)
8. [Key Design Patterns](#key-design-patterns)

---

## 🎯 System Overview

CartUp is a **multi-agent voice AI system** built on LiveKit Agents framework. It uses a **specialized agent architecture** where different agents handle different e-commerce tasks, with seamless handoffs between them.

### Core Concept
- **Single conversation session** with multiple specialized agents
- **Context preservation** across agent transfers
- **Language-aware** responses (English/Bengali)
- **Stateful session management** via `UserData`

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    LiveKit Room (WebRTC)                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              AgentSession[UserData]                   │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │  │
│  │  │   STT    │→ │   LLM    │→ │   TTS    │           │  │
│  │  │ (Google) │  │ (OpenAI) │  │ (Google) │           │  │
│  │  └──────────┘  └──────────┘  └──────────┘           │  │
│  │       ↓              ↓              ↓               │  │
│  │  ┌──────────────────────────────────────┐          │  │
│  │  │      Current Agent (e.g., OrderAgent) │          │  │
│  │  │  - Instructions                        │          │  │
│  │  │  - Tools (function_tool decorators)    │          │  │
│  │  │  - Chat Context                        │          │  │
│  │  └──────────────────────────────────────┘          │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              UserData (Session State)                 │  │
│  │  - user_id, current_order_id, language                │  │
│  │  - agents: {greeter, order, ticket, returns, recommend}│  │
│  │  - prev_agent (for context handoff)                  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    ┌──────────────────┐
                    │   Database (SQLite)│
                    │  - Users, Orders   │
                    │  - Tickets, Returns│
                    └──────────────────┘
```

---

## 🔄 Agent Flow & Lifecycle

### 1. **System Initialization** (`main.py`)

```python
async def entrypoint(ctx: JobContext):
    # Step 1: Initialize database
    init_database()
    
    # Step 2: Create session state container
    userdata = UserData()
    
    # Step 3: Instantiate ALL agents upfront
    userdata.agents = {
        "greeter": GreeterAgent(),
        "order": OrderAgent(),
        "ticket": TicketAgent(),
        "returns": ReturnAgent(),
        "recommend": RecommendAgent(),
    }
    
    # Step 4: Configure voice pipeline
    session = AgentSession[UserData](
        userdata=userdata,
        stt=google.STT(...),
        llm=openai.LLM(...),
        tts=google.TTS(...),
        vad=silero.VAD.load(),
    )
    
    # Step 5: Start with GreeterAgent
    await session.start(agent=userdata.agents["greeter"], room=ctx.room)
```

**Key Points:**
- All agents are created **once** at startup
- Agents are stored in `UserData.agents` dictionary
- Session starts with `GreeterAgent` as entry point
- `UserData` persists across the entire conversation

---

### 2. **Agent Lifecycle: `on_enter()` Method**

Every agent inherits from `BaseAgent`, which implements `on_enter()`. This is called **whenever an agent becomes active** (initial start or after transfer).

#### Flow in `BaseAgent.on_enter()`:

```python
async def on_enter(self) -> None:
    # 1. Get current session state
    userdata = self.session.userdata
    chat_ctx = self.chat_ctx.copy()
    
    # 2. Copy chat history from previous agent (if exists)
    if userdata.prev_agent:
        # Copy last 20 messages (excluding instructions)
        truncated_chat_ctx = userdata.prev_agent.chat_ctx.copy(
            exclude_instructions=True,
            exclude_function_call=False
        ).truncate(max_items=20)
        chat_ctx.items.extend(truncated_chat_ctx.items)
    
    # 3. Inject session summary + language instructions
    chat_ctx.add_message(
        role="system",
        content=(
            f"You are {agent_name}. Current session summary:\n{userdata.summarize()}\n\n"
            f"{lang_instructions}"
        ),
    )
    
    # 4. Update chat context
    await self.update_chat_ctx(chat_ctx)
    
    # 5. Generate greeting
    if userdata.prev_agent is None:
        # First agent - initial greeting
        await self.session.generate_reply(...)
    else:
        # Transferred agent - custom greeting
        await self._generate_transfer_greeting()
```

**What happens:**
1. **Context Copying**: Previous agent's chat history is copied (last 20 messages)
2. **State Injection**: Current `UserData` is summarized and injected as system message
3. **Language Awareness**: Language-specific instructions are added
4. **Greeting**: Agent-specific greeting is generated

---

### 3. **Agent Transfer Process**

#### How Transfer Works:

```python
# In any agent (e.g., GreeterAgent)
@function_tool()
async def to_order(self, context: RunContext_T):
    """Transfer to OrderAgent"""
    return await self._transfer_to_agent("order", context)

# BaseAgent._transfer_to_agent() implementation:
async def _transfer_to_agent(self, name: str, context: RunContext_T):
    userdata = context.userdata
    current_agent = context.session.current_agent
    next_agent = userdata.agents[name]  # Get agent from registry
    
    # Store current agent as previous for context handoff
    userdata.prev_agent = current_agent
    
    # Return tuple: (new_agent, transfer_message)
    return next_agent, f"Transferring to {name}."
```

**Transfer Flow:**
1. **Tool Call**: LLM calls transfer tool (e.g., `to_order()`)
2. **Agent Lookup**: Get target agent from `userdata.agents` dictionary
3. **State Update**: Set `userdata.prev_agent = current_agent`
4. **Return Tuple**: `(Agent, str)` - LiveKit uses this to switch agents
5. **Auto-trigger**: LiveKit calls `next_agent.on_enter()` automatically

---

## 🔀 Context Handoff Mechanism

### What Gets Preserved:

1. **UserData State**:
   - `user_id`, `current_order_id`, `current_ticket_id`
   - `language` preference
   - `last_intent`

2. **Chat History**:
   - Last 20 messages from previous agent
   - Excludes: system instructions (to avoid duplication)
   - Includes: function calls and results

3. **Session Summary**:
   - YAML-formatted summary injected as system message
   - Provides quick context grounding for new agent

### Example Context Handoff:

```
User: "I want to check my order status"
GreeterAgent: "Sure! What's your order ID?"
User: "o302"
GreeterAgent: [calls to_order() tool]
    ↓ TRANSFER
OrderAgent.on_enter():
    - Receives: user_id=None, current_order_id=None (from UserData)
    - Receives: Chat history with order ID "o302"
    - System message: "You are OrderAgent. user_id: unknown, current_order_id: none..."
    - LLM sees: "User mentioned order o302" → calls get_order_details("o302")
```

---

## 🎭 Agent Specialization

### Agent Hierarchy:

```
BaseAgent (Abstract)
├── GreeterAgent (Routing)
├── OrderAgent (Order Management)
├── TicketAgent (Support Tickets)
├── ReturnAgent (Returns/Refunds)
└── RecommendAgent (Product Recommendations)
```

### Each Agent Has:

1. **Instructions**: Role-specific prompts
2. **Tools**: Domain-specific function tools
3. **Transfer Tools**: Routes to other agents
4. **Custom Greeting**: `_generate_transfer_greeting()` method

---

## 🔧 Technical Implementation

### 1. **BaseAgent Pattern**

**Purpose**: Shared functionality for all agents

**Key Methods:**
- `on_enter()`: Context handoff logic
- `_transfer_to_agent()`: Agent switching mechanism
- `_generate_transfer_greeting()`: Customizable greeting

**Benefits:**
- DRY principle (Don't Repeat Yourself)
- Consistent context handoff
- Easy to add new agents

### 2. **UserData Pattern**

**Purpose**: Persistent session state

**Structure:**
```python
@dataclass
class UserData:
    user_id: Optional[str]
    current_order_id: Optional[str]
    current_ticket_id: Optional[str]
    language: Optional[str]
    agents: Dict[str, Agent]  # Agent registry
    prev_agent: Optional[Agent]  # For context copying
```

**Usage:**
- Accessed via `context.userdata` in tools
- Persists across agent transfers
- Summarized for LLM context injection

### 3. **Tool Pattern**

**Purpose**: LLM-callable functions

**Structure:**
```python
@function_tool()
async def tool_name(
    param: Annotated[str, Field(description="...")],
    context: RunContext_T,
) -> str:
    # Access session state
    context.userdata.user_id = param
    
    # Access database
    order = get_order(order_id)
    
    # Return result (or transfer tuple)
    return result
```

**Tool Types:**
- **State Tools**: Update `UserData` (e.g., `set_user`, `set_language`)
- **Database Tools**: Query/update database (e.g., `get_order_details`)
- **Transfer Tools**: Switch agents (e.g., `to_order`, `to_greeter`)

### 4. **Language-Aware System**

**Implementation:**
1. **STT**: Google Chirp-2 with Bengali support (`bn-BD`)
2. **Language Selection**: `set_language()` tool sets preference
3. **Context Injection**: Language instructions added to system message
4. **TTS**: Attempts to switch TTS (may be limited by LiveKit)

**Flow:**
```
User speaks Bengali → STT detects → LLM processes → 
set_language("bn-BD") → UserData.language = "bn-BD" → 
All agents inject Bengali instructions → Responses in Bengali
```

---

## 📊 Data Flow

### Complete Request Flow:

```
1. User Voice Input
   ↓
2. STT (Google Chirp-2) → Text
   ↓
3. Current Agent receives text via LLM
   ↓
4. LLM processes with:
   - Agent instructions
   - UserData summary (YAML)
   - Chat history (last 20 messages)
   - Available tools
   ↓
5. LLM decides:
   a) Call tool → Execute tool → Return result → LLM responds
   b) Transfer agent → _transfer_to_agent() → New agent.on_enter()
   c) Direct response → Generate reply
   ↓
6. Response generated:
   - Language-aware (based on UserData.language)
   - Context-aware (includes session summary)
   ↓
7. TTS (Google TTS) → Voice Output
   ↓
8. User hears response
```

### Agent Transfer Flow:

```
Current Agent (e.g., GreeterAgent)
   ↓
LLM calls: to_order(context)
   ↓
_transfer_to_agent("order", context):
   - userdata.prev_agent = GreeterAgent
   - next_agent = userdata.agents["order"]
   - return (OrderAgent, "Transferring to order.")
   ↓
LiveKit switches to OrderAgent
   ↓
OrderAgent.on_enter() called:
   - Copies chat history from GreeterAgent
   - Injects UserData summary
   - Adds language instructions
   - Generates greeting
   ↓
OrderAgent now active
```

---

## 🎨 Key Design Patterns

### 1. **Registry Pattern**
- All agents stored in `UserData.agents` dictionary
- Agents referenced by name: `"greeter"`, `"order"`, etc.
- Enables dynamic agent lookup

### 2. **Template Method Pattern**
- `BaseAgent.on_enter()` defines algorithm skeleton
- Subclasses override `_generate_transfer_greeting()` for customization
- Consistent flow with agent-specific behavior

### 3. **State Pattern**
- `UserData` maintains conversation state
- State persists across agent transfers
- Tools update state, agents read state

### 4. **Strategy Pattern**
- Each agent is a strategy for handling specific intents
- GreeterAgent routes to appropriate strategy
- Easy to add new strategies (agents)

### 5. **Tool Pattern**
- Functions decorated with `@function_tool()`
- LLM discovers and calls tools dynamically
- Tools can return values or trigger transfers

---

## 🔍 Detailed Agent Flow Examples

### Example 1: Order Status Query

```
1. User: "I want to check my order"
   ↓
2. GreeterAgent:
   - LLM recognizes: order-related intent
   - Calls: to_order(context)
   ↓
3. Transfer:
   - userdata.prev_agent = GreeterAgent
   - Switch to OrderAgent
   ↓
4. OrderAgent.on_enter():
   - Copies chat: "I want to check my order"
   - System: "You are OrderAgent. user_id: unknown..."
   - Greeting: "I can help with your order..."
   ↓
5. OrderAgent:
   - LLM sees order intent + no order_id
   - Asks: "What's your order ID?"
   ↓
6. User: "o302"
   ↓
7. OrderAgent:
   - LLM calls: get_order_details("o302", context)
   - Tool updates: context.userdata.current_order_id = "o302"
   - Tool returns: order details
   ↓
8. OrderAgent:
   - LLM responds: "Your order o302 is In Transit..."
```

### Example 2: Multi-Agent Workflow

```
1. User: "I have an issue with my order"
   ↓
2. GreeterAgent → OrderAgent (to check order)
   ↓
3. OrderAgent: "Order o302 is Delivered"
   ↓
4. User: "The product is damaged"
   ↓
5. OrderAgent:
   - LLM recognizes: support issue
   - Calls: to_ticket(context)
   ↓
6. Transfer to TicketAgent:
   - Context preserved: current_order_id = "o302"
   - Chat history includes order check
   ↓
7. TicketAgent:
   - Sees: order_id already in context
   - Creates ticket for order o302
   - No need to ask for order_id again!
```

---

## 🛠️ Technical Details

### Agent Session Configuration

```python
session = AgentSession[UserData](
    userdata=userdata,  # Type-safe session state
    stt=google.STT(
        model="chirp_2",
        location="asia-northeast1",
        languages=["bn-BD"],
        detect_language=True,
    ),
    llm=openai.LLM(model="gpt-4o-mini"),
    tts=google.TTS(...),
    vad=silero.VAD.load(),
    max_tool_steps=5,  # Max tool calls per turn
)
```

### Context Summarization

```python
def summarize(self) -> str:
    """Generates YAML summary for LLM context"""
    data = {
        "user_id": self.user_id or "unknown",
        "current_order_id": self.current_order_id or "none",
        "language": self.language or "en-IN",
    }
    return yaml.dump(data)
```

**Why YAML?**
- Structured and readable
- Easy for LLM to parse
- Compact representation

### Chat History Truncation

```python
truncated_chat_ctx = prev_agent.chat_ctx.copy(
    exclude_instructions=True,  # Don't copy system prompts
    exclude_function_call=False  # Keep tool calls
).truncate(max_items=20)  # Last 20 messages
```

**Why truncate?**
- Prevents context overflow
- Keeps relevant recent history
- Maintains performance

---

## 🎯 Key Design Decisions

### 1. **Why All Agents Created Upfront?**
- **Performance**: No agent instantiation delay during transfer
- **State Sharing**: Agents can share references
- **Memory Efficiency**: Agents are lightweight objects

### 2. **Why Context Copying?**
- **Continuity**: User doesn't repeat information
- **Context Awareness**: New agent understands conversation history
- **Better UX**: Seamless handoffs

### 3. **Why BaseAgent?**
- **Code Reuse**: Shared logic in one place
- **Consistency**: All agents behave similarly
- **Maintainability**: Changes in one place affect all agents

### 4. **Why UserData Pattern?**
- **Type Safety**: `RunContext[UserData]` provides type hints
- **Persistence**: State survives agent transfers
- **Accessibility**: Available in all tools via `context.userdata`

---

## 📈 Scalability Considerations

### Current Architecture Supports:

1. **Adding New Agents**:
   - Create new agent class inheriting `BaseAgent`
   - Add to `userdata.agents` dictionary
   - Add transfer tools in other agents

2. **Adding New Tools**:
   - Create function with `@function_tool()` decorator
   - Add to agent's `tools` list
   - LLM automatically discovers it

3. **Language Expansion**:
   - Add language code to `set_language()` tool
   - Update `config.py` with TTS voices
   - Add language instructions in `BaseAgent.on_enter()`

---

## 🔐 Security & Best Practices

### State Management:
- ✅ UserData is session-scoped (not global)
- ✅ Database operations are transactional
- ✅ Sensitive data not logged

### Error Handling:
- ✅ Tools return error messages instead of exceptions
- ✅ Database operations wrapped in try-except
- ✅ Graceful degradation on failures

### Language Support:
- ✅ Language preference persists across transfers
- ✅ Instructions injected dynamically
- ✅ TTS attempts to switch (may be limited)

---

## 🔬 Detailed Agent Breakdown with Code Examples

### 1. **GreeterAgent** - The Routing Hub

**Purpose**: Entry point and intelligent router that directs users to specialized agents.

**Location**: `cartup_agent/agents/greeter_agent.py`

#### What It Does:
1. **Language Selection**: First checks if user has selected a language, prompts if not
2. **Intent Recognition**: Analyzes user intent to route to appropriate agent
3. **State Initialization**: Sets initial user_id, order_id, language preferences
4. **Multi-Agent Routing**: Has transfer tools to all 4 specialized agents

#### Code Structure:

```python
class GreeterAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are CartUp's friendly voice assistant.\n"
                "FIRST, check if the user has selected a language preference...\n"
                "If they want: order tracking/modification ⇒ OrderAgent; "
                "issue/ticket ⇒ TicketAgent; returns/refunds ⇒ ReturnAgent; "
                "recommendations ⇒ RecommendAgent.\n"
            ),
            tools=[set_user, set_current_order, set_language],  # State management tools
            llm=openai.LLM(model="gpt-4o-mini"),
            tts=google.TTS(voice_name="en-IN-Chirp-HD-F", language="en-IN"),
        )
```

#### Transfer Tools (How It Connects to Other Agents):

```python
@function_tool()
async def to_order(self, context: RunContext_T):
    """Transfer to OrderAgent for order-related queries."""
    return await self._transfer_to_agent("order", context)

@function_tool()
async def to_ticket(self, context: RunContext_T):
    """Transfer to TicketAgent for support ticket creation and tracking."""
    return await self._transfer_to_agent("ticket", context)

@function_tool()
async def to_returns(self, context: RunContext_T):
    """Transfer to ReturnAgent for returns and refunds."""
    return await self._transfer_to_agent("returns", context)

@function_tool()
async def to_recommend(self, context: RunContext_T):
    """Transfer to RecommendAgent for product recommendations."""
    return await self._transfer_to_agent("recommend", context)
```

#### Connection Flow Example:

```
User: "I want to check my order status"
   ↓
GreeterAgent LLM processes:
   - Recognizes: "order status" → order-related intent
   - Checks UserData: current_order_id = None
   - Decides: Need to transfer to OrderAgent
   ↓
LLM calls: to_order(context)
   ↓
_transfer_to_agent("order", context) executes:
   1. userdata = context.userdata
   2. current_agent = context.session.current_agent  # GreeterAgent instance
   3. next_agent = userdata.agents["order"]  # OrderAgent instance from registry
   4. userdata.prev_agent = current_agent  # Store for context copying
   5. return (OrderAgent, "Transferring to order.")
   ↓
LiveKit receives tuple → Switches active agent → Calls OrderAgent.on_enter()
```

#### Custom Greeting Logic:

```python
async def _generate_transfer_greeting(self) -> None:
    """Generate a greeting when GreeterAgent becomes active after transfer."""
    userdata = self.session.userdata
    if not userdata.language:
        # Language not set - prompt for selection
        await self.session.generate_reply(
            instructions="Welcome back! Would you like to continue in English or Bengali?"
        )
    else:
        # Language is set - greet normally
        lang_name = "English" if userdata.language == "en-IN" else "Bengali (Bangladesh)"
        await self.session.generate_reply(
            instructions=f"Welcome back! How can I help you today? (Responding in {lang_name})"
        )
```

---

### 2. **OrderAgent** - Order Management Specialist

**Purpose**: Handles all order-related queries: status, details, history, address updates.

**Location**: `cartup_agent/agents/order_agent.py`

#### What It Does:
1. **Order Status Queries**: Fetches order details by order_id
2. **User Order History**: Retrieves all orders for a user_id
3. **Address Updates**: Updates delivery address for orders
4. **Context Awareness**: Checks UserData before asking for order_id/user_id

#### Code Structure:

```python
class OrderAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You handle order queries: status, items, amount, ETA, address updates.\n"
                "Before asking for user_id or order_id, FIRST check the session summary (userdata) "
                "and last tool results. If they are already present, do not re-ask and proceed.\n"
            ),
            tools=[
                set_current_order,      # Common tool: Update UserData.current_order_id
                to_greeter,              # Common tool: Return to GreeterAgent
                get_order_details,       # Order tool: Fetch order by order_id
                get_user_orders,         # Order tool: Get all orders for user_id
                update_delivery_address, # Order tool: Update order address
            ],
            llm=openai.LLM(model="gpt-4o-mini"),
            tts=google.TTS(voice_name="en-IN-Chirp-HD-D", language="en-IN"),
        )
```

#### Order Tools Implementation:

```python
# From cartup_agent/tools/order_tools.py

@function_tool()
async def get_order_details(
    order_id: Annotated[str, Field(description="Order ID to fetch (e.g., o302)")],
    context: RunContext_T,
) -> Dict[str, Any]:
    """Fetch order details from database."""
    order = get_order(order_id)  # Database query
    if not order:
        return {"error": f"Order {order_id} not found"}
    
    # CRITICAL: Update UserData state
    context.userdata.current_order_id = order_id
    
    return {
        "order_id": order_id,
        "status": order["status"],
        "items": order["items"],
        "amount": order["amount"],
        "delivery_date": order.get("delivery_date"),
        "address": order.get("address", ""),
    }
```

**Key Point**: Tools update `context.userdata` which persists across agent transfers!

#### How It Connects to Other Agents:

```python
@function_tool()
async def to_ticket(self, context: RunContext_T):
    """Transfer to TicketAgent for support ticket creation and tracking."""
    return await self._transfer_to_agent("ticket", context)

@function_tool()
async def to_returns(self, context: RunContext_T):
    """Transfer to ReturnAgent for returns and refunds."""
    return await self._transfer_to_agent("returns", context)

@function_tool()
async def to_recommend(self, context: RunContext_T):
    """Transfer to RecommendAgent for product recommendations."""
    return await self._transfer_to_agent("recommend", context)
```

#### Connection Flow Example:

```
User: "My order o302 is damaged"
   ↓
OrderAgent LLM processes:
   - Recognizes: "damaged" → support issue
   - Checks UserData: current_order_id = "o302" (already set!)
   - Decides: Transfer to TicketAgent (order already in context)
   ↓
LLM calls: to_ticket(context)
   ↓
_transfer_to_agent("ticket", context):
   1. userdata.prev_agent = OrderAgent (current)
   2. next_agent = userdata.agents["ticket"]  # TicketAgent
   3. return (TicketAgent, "Transferring to ticket.")
   ↓
TicketAgent.on_enter() called:
   - Copies chat history: "My order o302 is damaged"
   - Receives UserData: current_order_id = "o302" (preserved!)
   - System message: "You are TicketAgent. current_order_id: o302..."
   ↓
TicketAgent LLM:
   - Sees order_id already in context
   - Asks: "What's the issue?" (doesn't ask for order_id again!)
```

---

### 3. **TicketAgent** - Support Ticket Handler

**Purpose**: Creates and tracks support tickets for order issues.

**Location**: `cartup_agent/agents/ticket_agent.py`

#### What It Does:
1. **Ticket Creation**: Creates tickets linked to orders
2. **Ticket Tracking**: Fetches ticket status and details
3. **Issue Management**: Handles missing, damaged, wrong item issues
4. **Context Preservation**: Uses order_id from UserData if available

#### Code Structure:

```python
class TicketAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You create and track support tickets for orders "
                "(missing, damaged, wrong item, etc.).\n"
                "Before asking for user_id or order_id, FIRST check the session summary (userdata) "
                "and last tool results. If they are already present, do not re-ask and proceed.\n"
            ),
            tools=[
                set_current_order,  # Common tool
                to_greeter,          # Common tool
                create_ticket,        # Ticket tool: Create new ticket
                track_ticket,         # Ticket tool: Get ticket status
                get_ticket_status,    # Ticket tool: Alias for track_ticket
            ],
            llm=openai.LLM(model="gpt-4o-mini"),
            tts=google.TTS(voice_name="en-IN-Chirp-HD-F", language="en-IN"),
        )
```

#### Ticket Tools Implementation:

```python
# From cartup_agent/tools/ticket_tools.py

@function_tool()
async def create_ticket(
    order_id: Annotated[str, Field(description="Related order ID")],
    issue: Annotated[str, Field(description="Short issue description")],
    context: RunContext_T,
) -> Dict[str, Any]:
    """Create a ticket and return ticket data."""
    order = get_order(order_id)  # Validate order exists
    if not order:
        return {"error": f"Order {order_id} not found"}
    
    ticket_id = _next_id("ticket")  # Generate unique ID: "t602"
    created_at = datetime.now().strftime("%Y-%m-%d")
    
    if create_ticket_record(ticket_id, order_id, issue, "Open", created_at):
        # CRITICAL: Update UserData state
        context.userdata.current_ticket_id = ticket_id
        context.userdata.current_order_id = order_id
        
        return {
            "ticket_id": ticket_id,
            "order_id": order_id,
            "issue": issue,
            "status": "Open",
        }
```

**Key Point**: Tools update both `current_ticket_id` AND `current_order_id` for future context!

#### How It Connects to Other Agents:

```python
@function_tool()
async def to_order(self, context: RunContext_T):
    """Transfer to OrderAgent for order-related queries."""
    return await self._transfer_to_agent("order", context)

@function_tool()
async def to_returns(self, context: RunContext_T):
    """Transfer to ReturnAgent for returns and refunds."""
    return await self._transfer_to_agent("returns", context)

@function_tool()
async def to_recommend(self, context: RunContext_T):
    """Transfer to RecommendAgent for product recommendations."""
    return await self._transfer_to_agent("recommend", context)
```

#### Connection Flow Example:

```
User: "I want to return order o302"
   ↓
TicketAgent LLM processes:
   - Recognizes: "return" → return/refund intent
   - Checks UserData: current_order_id = "o302" (from previous context)
   - Decides: Transfer to ReturnAgent
   ↓
LLM calls: to_returns(context)
   ↓
_transfer_to_agent("returns", context):
   1. userdata.prev_agent = TicketAgent
   2. next_agent = userdata.agents["returns"]  # ReturnAgent
   3. return (ReturnAgent, "Transferring to returns.")
   ↓
ReturnAgent.on_enter():
   - Copies chat: "I want to return order o302"
   - Receives UserData: current_order_id = "o302" (preserved!)
   - System: "You are ReturnAgent. current_order_id: o302..."
   ↓
ReturnAgent LLM:
   - Sees order_id in context
   - Asks: "What's the reason for return?" (skips order_id question!)
```

---

### 4. **ReturnAgent** - Returns & Refunds Specialist

**Purpose**: Handles return initiation, return status tracking, and refund updates.

**Location**: `cartup_agent/agents/return_agent.py`

#### What It Does:
1. **Return Initiation**: Creates return records for orders
2. **Return Status**: Tracks return progress (Pending, In Transit, etc.)
3. **Refund Management**: Updates refund status
4. **Order Validation**: Ensures order exists before processing return

#### Code Structure:

```python
class ReturnAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You manage returns and refunds. Ask for order_id; mark a return as initiated; "
                "report return and refund status.\n"
                "Before asking for user_id or order_id, FIRST check the session summary (userdata) "
                "and last tool results. If they are already present, do not re-ask and proceed.\n"
            ),
            tools=[
                set_current_order,      # Common tool
                to_greeter,              # Common tool
                initiate_return,         # Return tool: Create return record
                get_return_status,       # Return tool: Check return status
                update_refund_status,    # Return tool: Update refund progress
            ],
            llm=openai.LLM(model="gpt-4o-mini"),
            tts=google.TTS(voice_name="en-US-Chirp-HD-D", language="en-US"),
        )
```

#### Return Tools Implementation:

```python
# From cartup_agent/tools/return_tools.py

@function_tool()
async def initiate_return(
    order_id: Annotated[str, Field(description="Order to return")],
    reason: Annotated[str, Field(description="Why returning")],
    context: RunContext_T,
) -> Dict[str, Any]:
    """Create/overwrite a return record."""
    order = get_order(order_id)  # Validate order
    if not order:
        return {"error": f"Order {order_id} not found"}
    
    created_at = datetime.now().strftime("%Y-%m-%d")
    
    if create_return_record(order_id, reason, "Pending Courier Pickup", "Not Initiated", created_at):
        # CRITICAL: Update UserData
        context.userdata.current_order_id = order_id
        
        return_record = get_return(order_id)
        return {
            "order_id": order_id,
            **return_record,  # Includes: return_status, refund_status, created_at
        }
```

#### How It Connects to Other Agents:

```python
@function_tool()
async def to_order(self, context: RunContext_T):
    """Transfer to OrderAgent for order-related queries."""
    return await self._transfer_to_agent("order", context)

@function_tool()
async def to_ticket(self, context: RunContext_T):
    """Transfer to TicketAgent for support ticket creation and tracking."""
    return await self._transfer_to_agent("ticket", context)

@function_tool()
async def to_recommend(self, context: RunContext_T):
    """Transfer to RecommendAgent for product recommendations."""
    return await self._transfer_to_agent("recommend", context)
```

---

### 5. **RecommendAgent** - Product Recommendation Engine

**Purpose**: Provides personalized product recommendations based on user profiles.

**Location**: `cartup_agent/agents/recommend_agent.py`

#### What It Does:
1. **Personalized Recommendations**: Fetches recommendations based on user_id
2. **Product Details**: Retrieves detailed product information
3. **Wishlist Management**: Adds products to user wishlist
4. **User Profile Integration**: Uses user preferences for recommendations

#### Code Structure:

```python
class RecommendAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You provide simple personalized recommendations using a dummy profile list. "
                "Ask for user_id if missing. Offer to add to wishlist (simulated).\n"
                "Before asking for user_id or order_id, FIRST check the session summary (userdata) "
                "and last tool results. If they are already present, do not re-ask and proceed.\n"
            ),
            tools=[
                set_user,               # Common tool: Set user_id
                to_greeter,             # Common tool
                get_recommendations,     # Recommend tool: Get user recommendations
                get_product_details,     # Recommend tool: Fetch product info
                add_to_wishlist,        # Recommend tool: Add to wishlist
            ],
            llm=openai.LLM(model="gpt-4o-mini"),
            tts=google.TTS(voice_name="bn-IN-Chirp3-HD-Pulcherrima", language="bn-IN"),
        )
```

#### Recommendation Tools Implementation:

```python
# From cartup_agent/tools/recommend_tools.py

@function_tool()
async def get_recommendations(
    user_id: Annotated[str, Field(description="User ID to recommend for")],
    context: RunContext_T,
) -> Dict[str, Any]:
    """Fetch recommended items for a user."""
    recommendations = get_recommendations_for_user(user_id)  # Database query
    
    # CRITICAL: Update UserData
    context.userdata.user_id = user_id
    
    return {
        "user_id": user_id,
        "recommendations": recommendations,  # List of product dicts
    }

@function_tool()
async def add_to_wishlist(
    user_id: Annotated[str, Field(description="User ID")],
    product_id: Annotated[str, Field(description="Product ID to add")],
    context: RunContext_T,
) -> str:
    """Add a product to user's wishlist."""
    product = get_product(product_id)
    if not product:
        return f"Product {product_id} not found"
    
    if db_add_to_wishlist(user_id, product_id):
        # CRITICAL: Update UserData with both IDs
        context.userdata.user_id = user_id
        context.userdata.current_product_id = product_id
        
        return f"Product {product_id} ({product['name']}) added to wishlist for user {user_id}"
```

#### How It Connects to Other Agents:

```python
@function_tool()
async def to_order(self, context: RunContext_T):
    """Transfer to OrderAgent for order-related queries."""
    return await self._transfer_to_agent("order", context)

@function_tool()
async def to_ticket(self, context: RunContext_T):
    """Transfer to TicketAgent for support ticket creation and tracking."""
    return await self._transfer_to_agent("ticket", context)

@function_tool()
async def to_returns(self, context: RunContext_T):
    """Transfer to ReturnAgent for returns and refunds."""
    return await self._transfer_to_agent("returns", context)
```

---

## 🔗 Agent Connection Matrix

### Complete Connection Graph:

```
                    ┌─────────────┐
                    │ GreeterAgent│ (Entry Point)
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ OrderAgent   │   │ TicketAgent  │   │ ReturnAgent  │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                          ▼
                  ┌──────────────┐
                  │RecommendAgent│
                  └──────────────┘

All agents can:
- Transfer to GreeterAgent (via to_greeter tool)
- Transfer to each other (via agent-specific transfer tools)
```

### Transfer Tool Availability:

| Agent | Can Transfer To |
|-------|----------------|
| **GreeterAgent** | OrderAgent, TicketAgent, ReturnAgent, RecommendAgent |
| **OrderAgent** | GreeterAgent, TicketAgent, ReturnAgent, RecommendAgent |
| **TicketAgent** | GreeterAgent, OrderAgent, ReturnAgent, RecommendAgent |
| **ReturnAgent** | GreeterAgent, OrderAgent, TicketAgent, RecommendAgent |
| **RecommendAgent** | GreeterAgent, OrderAgent, TicketAgent, ReturnAgent |

---

## 🔄 Complete Multi-Agent Workflow Example

### Scenario: User wants to return a damaged product

```
Step 1: User connects
   ↓
GreeterAgent.on_enter() called (prev_agent = None)
   - No chat history to copy
   - System: "You are GreeterAgent. user_id: unknown..."
   - Greeting: "Welcome! Would you like English or Bengali?"
   ↓
User: "English"
   ↓
GreeterAgent LLM:
   - Calls: set_language("en-IN", context)
   - context.userdata.language = "en-IN"
   ↓
User: "I want to return my order"
   ↓
GreeterAgent LLM:
   - Recognizes: "return" → ReturnAgent intent
   - Calls: to_returns(context)
   ↓
Step 2: Transfer to ReturnAgent
   ↓
_transfer_to_agent("returns", context):
   - userdata.prev_agent = GreeterAgent
   - next_agent = userdata.agents["returns"]
   - return (ReturnAgent, "Transferring to returns.")
   ↓
ReturnAgent.on_enter() called:
   - Copies chat history from GreeterAgent:
     * "I want to return my order"
   - System: "You are ReturnAgent. user_id: unknown, current_order_id: none..."
   - Greeting: "I can help with returns..."
   ↓
User: "Order o302"
   ↓
ReturnAgent LLM:
   - Calls: initiate_return("o302", "damaged", context)
   - Tool updates: context.userdata.current_order_id = "o302"
   - Tool returns: {"order_id": "o302", "return_status": "Pending..."}
   ↓
ReturnAgent LLM:
   - Responds: "I've initiated return for order o302..."
   ↓
User: "Actually, I want to create a support ticket instead"
   ↓
ReturnAgent LLM:
   - Recognizes: "support ticket" → TicketAgent intent
   - Checks UserData: current_order_id = "o302" (already set!)
   - Calls: to_ticket(context)
   ↓
Step 3: Transfer to TicketAgent
   ↓
TicketAgent.on_enter() called:
   - Copies chat history (last 20 messages):
     * "I want to return my order"
     * "Order o302"
     * "Actually, I want to create a support ticket instead"
   - Receives UserData: current_order_id = "o302" (preserved!)
   - System: "You are TicketAgent. current_order_id: o302..."
   ↓
TicketAgent LLM:
   - Sees order_id already in context (doesn't ask again!)
   - Asks: "What's the issue with order o302?"
   ↓
User: "The product is damaged"
   ↓
TicketAgent LLM:
   - Calls: create_ticket("o302", "damaged", context)
   - Tool updates:
     * context.userdata.current_ticket_id = "t602"
     * context.userdata.current_order_id = "o302"
   - Tool returns: {"ticket_id": "t602", "status": "Open"}
   ↓
TicketAgent LLM:
   - Responds: "I've created ticket t602 for order o302..."
```

**Key Observations:**
1. **Context Preservation**: `current_order_id = "o302"` persisted across 3 agents
2. **No Repetition**: User never had to repeat order_id
3. **Chat History**: All agents saw relevant conversation history
4. **State Updates**: Tools updated UserData which persisted

---

## 🛠️ BaseAgent Implementation Deep Dive

### The Core Transfer Mechanism:

```python
# From cartup_agent/agents/base_agent.py

async def _transfer_to_agent(
    self, name: str, context: RunContext_T
) -> Tuple[Agent, str]:
    """Transfer to another agent and return transfer tuple."""
    userdata = context.userdata
    current_agent = context.session.current_agent  # 'self' (current agent)
    next_agent = userdata.agents[name]  # Lookup from registry
    
    # CRITICAL: Store current agent for context copying
    userdata.prev_agent = current_agent
    
    # Return tuple: (Agent, str)
    # LiveKit uses this to switch the active agent
    return next_agent, f"Transferring to {name}."
```

**How LiveKit Uses the Tuple:**
- When a tool returns `(Agent, str)`, LiveKit recognizes it as a transfer
- LiveKit switches `session.current_agent` to the new agent
- LiveKit automatically calls `next_agent.on_enter()`

### Context Handoff Implementation:

```python
async def on_enter(self) -> None:
    """Called when agent becomes active. Handles context handoff."""
    userdata: UserData = self.session.userdata
    chat_ctx = self.chat_ctx.copy()
    
    # Copy truncated chat history from previous agent
    if isinstance(userdata.prev_agent, Agent):
        truncated_chat_ctx = userdata.prev_agent.chat_ctx.copy(
            exclude_instructions=True,  # Don't copy system prompts
            exclude_function_call=False  # Keep tool calls
        ).truncate(max_items=20)  # Last 20 messages
        
        # Avoid duplicates
        existing_ids = {item.id for item in chat_ctx.items}
        items_copy = [
            item for item in truncated_chat_ctx.items
            if item.id not in existing_ids
        ]
        chat_ctx.items.extend(items_copy)
    
    # Inject session summary + language instructions
    chat_ctx.add_message(
        role="system",
        content=(
            f"You are {agent_name}. Current session summary:\n{userdata.summarize()}\n\n"
            f"{lang_instructions}"
        ),
    )
    
    await self.update_chat_ctx(chat_ctx)
    
    # Generate greeting
    if userdata.prev_agent is None:
        # First agent (GreeterAgent)
        await self.session.generate_reply(...)
    else:
        # Transferred agent
        await self._generate_transfer_greeting()
```

**Key Technical Details:**
1. **Chat Context Copying**: Uses `chat_ctx.copy()` with filters
2. **Duplicate Prevention**: Checks `item.id` to avoid duplicate messages
3. **Truncation**: Limits to last 20 messages to prevent context overflow
4. **System Message Injection**: Adds agent-specific instructions + UserData summary
5. **Language Instructions**: Dynamically adds language-specific prompts

---

## 📝 Summary

**CartUp Agent System** is a sophisticated multi-agent architecture that:

1. **Routes intelligently** via GreeterAgent
2. **Preserves context** across agent transfers
3. **Handles specialized tasks** with dedicated agents
4. **Maintains conversation state** via UserData
5. **Supports multiple languages** dynamically
6. **Scales easily** with new agents and tools

The system demonstrates **production-ready patterns** for building complex voice AI applications with LiveKit Agents framework.

### Technical Highlights:

- **Agent Registry Pattern**: All agents stored in `UserData.agents` dictionary
- **Transfer Tuple Pattern**: Tools return `(Agent, str)` to trigger transfers
- **Context Copying**: Chat history preserved via `chat_ctx.copy()` with truncation
- **State Persistence**: `UserData` survives agent transfers
- **Tool-Based Communication**: Agents communicate via shared tools and transfer tools
- **Language-Aware System**: Dynamic language instructions injected per agent

