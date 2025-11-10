# CartUp E-Commerce Voice Agent - Architecture Plan

## 📁 Project Structure

```
cartup_agent/
├── __init__.py
├── main.py                    # Entry point
├── config.py                  # Configuration (models, voices, etc.)
│
├── database/
│   ├── __init__.py
│   ├── dummy_db.py           # In-memory dummy database
│   └── models.py              # Data models/schemas
│
├── agents/
│   ├── __init__.py
│   ├── base_agent.py         # BaseAgent class with shared logic
│   ├── greeter_agent.py      # GreeterAgent - routing agent
│   ├── order_agent.py         # OrderAgent - order management
│   ├── ticket_agent.py        # TicketAgent - support tickets
│   ├── return_agent.py        # ReturnAgent - returns/refunds
│   └── recommend_agent.py    # RecommendAgent - product recommendations
│
├── tools/
│   ├── __init__.py
│   ├── common_tools.py       # Shared tools (set_user, set_order, etc.)
│   ├── order_tools.py         # Order-specific tools
│   ├── ticket_tools.py        # Ticket-specific tools
│   ├── return_tools.py        # Return-specific tools
│   └── recommend_tools.py     # Recommendation tools
│
├── session/
│   ├── __init__.py
│   └── user_data.py           # UserData dataclass and session state
│
└── utils/
    ├── __init__.py
    └── helpers.py             # Utility functions (ID generation, etc.)
```

## 🏗️ Component Breakdown

### 1. **config.py** - Configuration Module

**Responsibilities:**

- Voice configuration (ElevenLabs voice IDs per agent)
- Model configuration (STT, LLM, TTS, VAD settings)
- Agent registry mapping
- Environment variable loading

**Key Exports:**

- `VOICES` dict: Maps agent names to ElevenLabs voice IDs
- `get_voice_pipeline()`: Returns configured voice pipeline components
- `AGENT_CONFIG`: Agent-specific configurations

---

### 2. **database/** - Database Module

#### **dummy_db.py**

**Responsibilities:**

- In-memory database structure
- CRUD operations for all entities
- ID generation helpers
- Database initialization

**Data Structures:**

```python
DUMMY_DB = {
    "users": {},           # user_id -> user_data
    "orders": {},          # order_id -> order_data
    "products": {},        # product_id -> product_data
    "tickets": {},        # ticket_id -> ticket_data
    "returns": {},        # order_id -> return_data
    "recommendations": {}, # user_id -> [product_ids]
    "carts": {},          # user_id -> cart_data
    "wishlists": {},      # user_id -> [product_ids]
    "next_ids": {}        # Auto-increment counters
}
```

**Key Functions:**

- `init_database()`: Initialize with sample data
- `get_user(user_id)`: Get user by ID
- `get_order(order_id)`: Get order by ID
- `create_ticket(...)`: Create support ticket
- `initiate_return(...)`: Create return record
- `_next_id(entity_type)`: Generate next ID

#### **models.py**

**Responsibilities:**

- Pydantic/dataclass models for type safety
- Data validation schemas
- Type definitions

**Models:**

- `User`, `Order`, `Product`, `Ticket`, `Return`, `Cart`, `Wishlist`

---

### 3. **session/user_data.py** - Session State Management

**Responsibilities:**

- UserData dataclass definition
- Session state tracking
- Context summarization for LLM

**Key Components:**

```python
@dataclass
class UserData:
    user_id: Optional[str]
    current_order_id: Optional[str]
    current_ticket_id: Optional[str]
    current_product_id: Optional[str]
    last_intent: Optional[str]
    agents: dict[str, Agent]
    prev_agent: Optional[Agent]

    def summarize(self) -> str  # YAML format
```

**Type Alias:**

- `RunContext_T = RunContext[UserData]`

---

### 4. **agents/base_agent.py** - Base Agent Class

**Responsibilities:**

- Shared agent functionality
- Agent transfer mechanism
- Context handoff logic
- Lifecycle hooks

**Key Methods:**

- `on_enter()`: Initialize agent with context
- `_transfer_to_agent(name, context)`: Transfer to another agent
- Chat history copying from previous agent
- UserData injection into system message

---

### 5. **agents/greeter_agent.py** - Greeter Agent

**Responsibilities:**

- Initial point of contact
- Intent recognition and routing
- User identification
- Route to specialized agents

**Tools:**

- `set_user()` (from common_tools)
- `set_current_order()` (from common_tools)
- `to_order()`, `to_ticket()`, `to_returns()`, `to_recommend()`

**Instructions:**

- Friendly greeting
- Understand user needs
- Route to appropriate agent
- Handle general inquiries

---

### 6. **agents/order_agent.py** - Order Management Agent

**Responsibilities:**

- Order status queries
- Order details retrieval
- Delivery address updates
- Order history

**Tools:**

- `get_order_details()` (from order_tools)
- `get_user_orders()` (from order_tools)
- `update_delivery_address()` (from order_tools)
- `set_current_order()` (from common_tools)
- `to_greeter()` (from common_tools)

**Instructions:**

- Handle order-related queries
- Provide order status updates
- Update delivery information
- Return to greeter when done

---

### 7. **agents/ticket_agent.py** - Support Ticket Agent

**Responsibilities:**

- Create support tickets
- Track ticket status
- Link tickets to orders
- Provide ticket updates

**Tools:**

- `create_ticket()` (from ticket_tools)
- `track_ticket()` (from ticket_tools)
- `get_ticket_status()` (from ticket_tools)
- `set_current_order()` (from common_tools)
- `to_greeter()` (from common_tools)

**Instructions:**

- Create tickets for issues
- Track ticket resolution
- Provide status updates
- Handle order-related issues

---

### 8. **agents/return_agent.py** - Returns & Refunds Agent

**Responsibilities:**

- Initiate returns
- Track return status
- Handle refunds
- Process return requests

**Tools:**

- `initiate_return()` (from return_tools)
- `get_return_status()` (from return_tools)
- `update_refund_status()` (from return_tools)
- `set_current_order()` (from common_tools)
- `to_greeter()` (from common_tools)

**Instructions:**

- Handle return requests
- Process refunds
- Track return progress
- Provide return status

---

### 9. **agents/recommend_agent.py** - Product Recommendations Agent

**Responsibilities:**

- Provide product recommendations
- Suggest related items
- Handle wishlist operations
- Product discovery

**Tools:**

- `get_recommendations()` (from recommend_tools)
- `get_product_details()` (from recommend_tools)
- `add_to_wishlist()` (from recommend_tools)
- `set_user()` (from common_tools)
- `to_greeter()` (from common_tools)

**Instructions:**

- Provide personalized recommendations
- Suggest products based on user history
- Handle wishlist requests
- Product information queries

---

### 10. **tools/common_tools.py** - Shared Tools

**Tools:**

- `set_user(user_id, context)`: Set/authenticate user
- `set_current_order(order_id, context)`: Set focal order
- `to_greeter(context)`: Return to greeter agent

**Usage:**

- Available to all agents
- Imported in agent `__init__` tools list

---

### 11. **tools/order_tools.py** - Order Tools

**Tools:**

- `get_order_details(order_id, context)`: Fetch order info
- `get_user_orders(user_id, context)`: Get all user orders
- `update_delivery_address(order_id, new_address, context)`: Update address

**Database Operations:**

- Query `DUMMY_DB["orders"]`
- Update `context.userdata.current_order_id`

---

### 12. **tools/ticket_tools.py** - Ticket Tools

**Tools:**

- `create_ticket(order_id, issue, context)`: Create new ticket
- `track_ticket(ticket_id, context)`: Get ticket status
- `get_ticket_status(ticket_id, context)`: Check ticket details

**Database Operations:**

- Create in `DUMMY_DB["tickets"]`
- Use `_next_id("ticket")` for ID generation
- Update `context.userdata.current_ticket_id`

---

### 13. **tools/return_tools.py** - Return Tools

**Tools:**

- `initiate_return(order_id, reason, context)`: Start return process
- `get_return_status(order_id, context)`: Check return status
- `update_refund_status(order_id, refund_status, context)`: Update refund

**Database Operations:**

- Store in `DUMMY_DB["returns"]`
- Link to orders
- Track refund status

---

### 14. **tools/recommend_tools.py** - Recommendation Tools

**Tools:**

- `get_recommendations(user_id, context)`: Get personalized recommendations
- `get_product_details(product_id, context)`: Get product info
- `add_to_wishlist(user_id, product_id, context)`: Add to wishlist

**Database Operations:**

- Query `DUMMY_DB["recommendations"]`
- Query `DUMMY_DB["products"]`
- Update `DUMMY_DB["wishlists"]`

---

### 15. **utils/helpers.py** - Utility Functions

**Functions:**

- `_next_id(entity_type: str) -> str`: Generate next ID
- `format_order_summary(order) -> str`: Format order for display
- `format_ticket_summary(ticket) -> str`: Format ticket for display
- `validate_order_id(order_id) -> bool`: Validate order ID format

---

### 16. **main.py** - Entry Point

**Responsibilities:**

- Initialize database
- Create UserData instance
- Instantiate all agents
- Configure AgentSession
- Start voice session

**Flow:**

```python
async def entrypoint(ctx: JobContext):
    # 1. Initialize database
    init_database()

    # 2. Create session state
    userdata = UserData()

    # 3. Create agents
    userdata.agents = {
        "greeter": GreeterAgent(),
        "order": OrderAgent(),
        "ticket": TicketAgent(),
        "returns": ReturnAgent(),
        "recommend": RecommendAgent(),
    }

    # 4. Configure session
    session = AgentSession[UserData](
        userdata=userdata,
        stt=deepgram.STT(model="nova-2"),
        llm=groq.LLM(model="openai/gpt-oss-20b", temperature=0.2),
        tts=elevenlabs.TTS(model="eleven_multilingual_v2"),
        vad=silero.VAD.load(),
        max_tool_steps=5,
    )

    # 5. Start with greeter
    await session.start(
        agent=userdata.agents["greeter"],
        room=ctx.room,
    )
```

---

## 🔄 Data Flow

```
User Input
    ↓
AgentSession (STT → LLM → TTS)
    ↓
Current Agent (processes with tools)
    ↓
Tool Execution (accesses DUMMY_DB, updates UserData)
    ↓
Tool Returns (string or Agent transfer)
    ↓
Agent Transfer (if needed) → New Agent.on_enter()
    ↓
Context Injection (UserData summary + chat history)
    ↓
Response Generation
```

---

## 📦 Dependencies

**Core:**

- `livekit-agents`
- `livekit-plugins-deepgram`
- `livekit-plugins-groq`
- `livekit-plugins-elevenlabs`
- `livekit-plugins-silero`

**Utilities:**

- `python-dotenv`
- `pydantic` (for Field annotations)
- `pyyaml` (for UserData summarization)

---

## 🎯 Implementation Order

### Phase 1: Foundation

1. ✅ Create folder structure
2. ✅ Setup `config.py` with voice/model config
3. ✅ Create `database/models.py` with data models
4. ✅ Implement `database/dummy_db.py` with sample data
5. ✅ Create `session/user_data.py` with UserData class

### Phase 2: Core Infrastructure

6. ✅ Implement `agents/base_agent.py`
7. ✅ Create `tools/common_tools.py`
8. ✅ Setup `utils/helpers.py`

### Phase 3: Specialized Agents

9. ✅ Implement `agents/greeter_agent.py`
10. ✅ Implement `agents/order_agent.py` + `tools/order_tools.py`
11. ✅ Implement `agents/ticket_agent.py` + `tools/ticket_tools.py`
12. ✅ Implement `agents/return_agent.py` + `tools/return_tools.py`
13. ✅ Implement `agents/recommend_agent.py` + `tools/recommend_tools.py`

### Phase 4: Integration

14. ✅ Create `main.py` entry point
15. ✅ Test agent transfers
16. ✅ Verify database operations
17. ✅ Test voice pipeline

---

## 🧪 Testing Strategy

**Unit Tests:**

- Database operations
- Tool functions
- UserData summarization
- ID generation

**Integration Tests:**

- Agent transfers
- Context handoff
- Tool execution flow
- Voice pipeline

**Manual Testing:**

- Full conversation flows
- Multi-agent interactions
- Error handling
- Voice quality

---

## 🔧 Configuration Notes

**Voice Configuration:**

- Each agent should have unique ElevenLabs voice
- Store voice IDs in `config.py`
- Can be overridden per agent in `__init__`

**Model Configuration:**

- Session-level: groq.LLM, deepgram.STT, elevenlabs.TTS, silero.VAD
- Agent-level: Can override LLM/TTS if needed
- Temperature: 0.2 (from basic agent)

**Database:**

- Start with comprehensive dummy data
- Include multiple users, orders, products
- Realistic relationships (users → orders → tickets)

---

## 📝 Key Design Principles

1. **Modularity**: Each component in separate file
2. **Separation of Concerns**: Agents, tools, database, config separate
3. **Reusability**: Common tools shared, base agent pattern
4. **Extensibility**: Easy to add new agents/tools
5. **Type Safety**: Use type hints and RunContext_T
6. **Context Preservation**: UserData + chat history handoff
7. **Error Handling**: Graceful failures in tools
8. **Documentation**: Clear docstrings for all tools

---

## 🚀 Next Steps

After plan approval:

1. Create folder structure
2. Implement Phase 1 (Foundation)
3. Implement Phase 2 (Core Infrastructure)
4. Implement Phase 3 (Specialized Agents)
5. Implement Phase 4 (Integration)
6. Test and refine
