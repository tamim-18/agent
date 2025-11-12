# CartUp Agent System - Comprehensive Test Cases

## 📋 Test Case Categories

1. [Agent Routing & Transfers](#agent-routing--transfers)
2. [Order Management](#order-management)
3. [Support Tickets](#support-tickets)
4. [Returns & Refunds](#returns--refunds)
5. [Product Recommendations](#product-recommendations)
6. [Context Preservation](#context-preservation)
7. [ID Formatting](#id-formatting)
8. [Language Switching](#language-switching)
9. [Multi-Agent Workflows](#multi-agent-workflows)
10. [Edge Cases & Error Handling](#edge-cases--error-handling)

---

## 🔀 Agent Routing & Transfers

### TC-001: Initial Greeting and Language Selection
**Objective**: Verify GreeterAgent handles initial connection and language selection

**Steps**:
1. Connect to agent
2. Agent should greet and ask for language preference
3. User: "English" or "Bengali"
4. Agent should confirm language selection

**Expected Result**:
- GreeterAgent greets user
- Language selection prompt appears
- Language is set correctly in UserData
- Subsequent responses use selected language

**Test Data**: None required

---

### TC-002: Route to OrderAgent
**Objective**: Verify GreeterAgent routes to OrderAgent correctly

**Steps**:
1. User: "I want to check my order status"
2. GreeterAgent should recognize order intent
3. Transfer to OrderAgent
4. OrderAgent should greet and ask for order ID

**Expected Result**:
- Transfer happens smoothly
- OrderAgent receives context
- No duplicate greetings
- User doesn't need to repeat intent

**Test Data**: User u101, Order o302

---

### TC-003: Route to TicketAgent
**Objective**: Verify GreeterAgent routes to TicketAgent correctly

**Steps**:
1. User: "I have an issue with my order"
2. GreeterAgent should recognize support intent
3. Transfer to TicketAgent
4. TicketAgent should greet and ask for order ID

**Expected Result**:
- Transfer happens smoothly
- TicketAgent receives context
- Appropriate greeting

**Test Data**: User u102, Order o303

---

### TC-004: Route to ReturnAgent
**Objective**: Verify GreeterAgent routes to ReturnAgent correctly

**Steps**:
1. User: "I want to return my order"
2. GreeterAgent should recognize return intent
3. Transfer to ReturnAgent
4. ReturnAgent should greet and ask for order ID

**Expected Result**:
- Transfer happens smoothly
- ReturnAgent receives context

**Test Data**: User u103, Order o304

---

### TC-005: Route to RecommendAgent
**Objective**: Verify GreeterAgent routes to RecommendAgent correctly

**Steps**:
1. User: "Show me product recommendations"
2. GreeterAgent should recognize recommendation intent
3. Transfer to RecommendAgent
4. RecommendAgent should greet and ask for user ID

**Expected Result**:
- Transfer happens smoothly
- RecommendAgent receives context

**Test Data**: User u104

---

### TC-006: Return to GreeterAgent
**Objective**: Verify agents can return to GreeterAgent

**Steps**:
1. User is in OrderAgent
2. User: "Go back to main menu"
3. OrderAgent should transfer to GreeterAgent
4. GreeterAgent should greet appropriately

**Expected Result**:
- Transfer back works
- Context preserved
- GreeterAgent greets correctly

**Test Data**: User u105

---

## 📦 Order Management

### TC-007: Get Order Details by Order ID
**Objective**: Verify OrderAgent can fetch order details

**Steps**:
1. Transfer to OrderAgent
2. User: "Check order o302"
3. Agent should call get_order_details("o302")
4. Agent should display order information

**Expected Result**:
- Order details retrieved successfully
- Status, items, amount displayed
- UserData.current_order_id updated

**Test Data**: Order o302 (In Transit, Wireless Earbuds, 79.99)

---

### TC-008: Get Order Details with Capitalized ID
**Objective**: Verify ID normalization works

**Steps**:
1. Transfer to OrderAgent
2. User: "Check order O302" (capital O)
3. Agent should normalize to lowercase
4. Order should be found

**Expected Result**:
- ID normalized to "o302"
- Order found successfully
- No "order not found" error

**Test Data**: Order o302

---

### TC-009: Get All Orders for User
**Objective**: Verify OrderAgent can fetch user's order history

**Steps**:
1. Transfer to OrderAgent
2. User: "Show all my orders"
3. Agent should ask for user ID
4. User: "u101"
5. Agent should call get_user_orders("u101")
6. Display all orders

**Expected Result**:
- All orders for user retrieved
- Order list displayed
- UserData.user_id updated

**Test Data**: User u101 (has orders o301, o302)

---

### TC-010: Update Delivery Address
**Objective**: Verify OrderAgent can update order address

**Steps**:
1. Transfer to OrderAgent
2. User: "Update address for order o302"
3. Agent should ask for new address
4. User: "123 New Street, Dhaka"
5. Agent should call update_delivery_address()
6. Confirm update

**Expected Result**:
- Address updated successfully
- Confirmation message displayed
- UserData.current_order_id updated

**Test Data**: Order o302

---

### TC-011: Order Not Found
**Objective**: Verify error handling for non-existent orders

**Steps**:
1. Transfer to OrderAgent
2. User: "Check order o999"
3. Agent should call get_order_details("o999")
4. Handle error gracefully

**Expected Result**:
- Error message displayed
- Agent asks for correct order ID
- No system crash

**Test Data**: Order o999 (does not exist)

---

### TC-012: Order Status Query
**Objective**: Verify OrderAgent handles status queries

**Steps**:
1. Transfer to OrderAgent
2. User: "What's the status of order o302?"
3. Agent should retrieve and display status

**Expected Result**:
- Status retrieved correctly
- Clear status message displayed

**Test Data**: Order o302 (In Transit)

---

## 🎫 Support Tickets

### TC-013: Create Support Ticket
**Objective**: Verify TicketAgent can create tickets

**Steps**:
1. Transfer to TicketAgent
2. User: "Create a ticket for order o301"
3. Agent should ask for issue description
4. User: "Product is damaged"
5. Agent should call create_ticket()
6. Display ticket ID

**Expected Result**:
- Ticket created successfully
- Ticket ID displayed (e.g., t526)
- UserData.current_ticket_id updated
- UserData.current_order_id updated

**Test Data**: Order o301

---

### TC-014: Create Ticket with Order ID in Context
**Objective**: Verify context preservation works

**Steps**:
1. Transfer to OrderAgent
2. User: "Check order o302"
3. Agent retrieves order (sets current_order_id)
4. User: "I want to create a ticket"
5. Transfer to TicketAgent
6. TicketAgent should use order ID from context
7. User: "Product is damaged"
8. Ticket created without asking for order ID

**Expected Result**:
- Order ID preserved across transfer
- TicketAgent doesn't ask for order ID again
- Ticket created successfully

**Test Data**: Order o302

---

### TC-015: Track Ticket Status
**Objective**: Verify TicketAgent can track tickets

**Steps**:
1. Transfer to TicketAgent
2. User: "Check ticket t501"
3. Agent should call track_ticket("t501")
4. Display ticket status

**Expected Result**:
- Ticket status retrieved
- Status, issue, order_id displayed
- UserData.current_ticket_id updated

**Test Data**: Ticket t501 (Resolved, Damaged product, o301)

---

### TC-016: Track Ticket with Capitalized ID
**Objective**: Verify ticket ID normalization

**Steps**:
1. Transfer to TicketAgent
2. User: "Check ticket T501" (capital T)
3. Agent should normalize to lowercase
4. Ticket should be found

**Expected Result**:
- ID normalized to "t501"
- Ticket found successfully

**Test Data**: Ticket t501

---

### TC-017: Ticket Not Found
**Objective**: Verify error handling for non-existent tickets

**Steps**:
1. Transfer to TicketAgent
2. User: "Check ticket t999"
3. Agent should handle error gracefully

**Expected Result**:
- Error message displayed
- Agent asks for correct ticket ID

**Test Data**: Ticket t999 (does not exist)

---

## 🔄 Returns & Refunds

### TC-018: Initiate Return
**Objective**: Verify ReturnAgent can initiate returns

**Steps**:
1. Transfer to ReturnAgent
2. User: "I want to return order o301"
3. Agent should ask for reason
4. User: "Product damaged"
5. Agent should call initiate_return()
6. Display return status

**Expected Result**:
- Return initiated successfully
- Return status displayed
- UserData.current_order_id updated

**Test Data**: Order o301

---

### TC-019: Check Return Status
**Objective**: Verify ReturnAgent can check return status

**Steps**:
1. Transfer to ReturnAgent
2. User: "Check return status for order o301"
3. Agent should call get_return_status("o301")
4. Display return and refund status

**Expected Result**:
- Return status retrieved
- Status and refund_status displayed

**Test Data**: Order o301 (has return record)

---

### TC-020: Update Refund Status
**Objective**: Verify ReturnAgent can update refund status

**Steps**:
1. Transfer to ReturnAgent
2. User: "Update refund for order o301"
3. Agent should ask for new status
4. User: "Approved"
5. Agent should call update_refund_status()
6. Confirm update

**Expected Result**:
- Refund status updated
- Confirmation displayed

**Test Data**: Order o301 (has return record)

---

### TC-021: Return with Order ID in Context
**Objective**: Verify context preservation for returns

**Steps**:
1. Transfer to OrderAgent
2. User: "Check order o302"
3. Agent retrieves order
4. User: "I want to return this"
5. Transfer to ReturnAgent
6. ReturnAgent should use order ID from context
7. User: "Changed my mind"
8. Return initiated without asking for order ID

**Expected Result**:
- Order ID preserved
- ReturnAgent doesn't ask for order ID
- Return initiated successfully

**Test Data**: Order o302

---

## 🎁 Product Recommendations

### TC-022: Get Recommendations for User
**Objective**: Verify RecommendAgent can fetch recommendations

**Steps**:
1. Transfer to RecommendAgent
2. User: "Show me recommendations"
3. Agent should ask for user ID
4. User: "u101"
5. Agent should call get_recommendations("u101")
6. Display recommended products

**Expected Result**:
- Recommendations retrieved
- Product list displayed
- UserData.user_id updated

**Test Data**: User u101 (has recommendations)

---

### TC-023: Get Product Details
**Objective**: Verify RecommendAgent can fetch product details

**Steps**:
1. Transfer to RecommendAgent
2. User: "Show details for product p001"
3. Agent should call get_product_details("p001")
4. Display product information

**Expected Result**:
- Product details retrieved
- Name, description, price displayed
- UserData.current_product_id updated

**Test Data**: Product p001 (Smartphone)

---

### TC-024: Add to Wishlist
**Objective**: Verify RecommendAgent can add products to wishlist

**Steps**:
1. Transfer to RecommendAgent
2. User: "Add product p001 to my wishlist"
3. Agent should ask for user ID if not set
4. User: "u101"
5. Agent should call add_to_wishlist("u101", "p001")
6. Confirm addition

**Expected Result**:
- Product added to wishlist
- Confirmation displayed
- UserData updated

**Test Data**: User u101, Product p001

---

### TC-025: Recommendations with User ID in Context
**Objective**: Verify context preservation for recommendations

**Steps**:
1. Transfer to OrderAgent
2. User: "Show orders for user u101"
3. Agent sets user_id in context
4. User: "Show me recommendations"
5. Transfer to RecommendAgent
6. RecommendAgent should use user_id from context
7. Recommendations displayed without asking for user ID

**Expected Result**:
- User ID preserved
- Recommendations displayed without asking for user ID

**Test Data**: User u101

---

## 🔄 Context Preservation

### TC-026: Multi-Agent Context Preservation
**Objective**: Verify context preserved across multiple transfers

**Steps**:
1. Transfer to OrderAgent
2. User: "Check order o302"
3. Agent retrieves order (sets current_order_id = "o302")
4. User: "Create a ticket for this order"
5. Transfer to TicketAgent
6. TicketAgent should see order_id in context
7. User: "Product is damaged"
8. Ticket created without asking for order ID
9. User: "Actually, I want to return it instead"
10. Transfer to ReturnAgent
11. ReturnAgent should see order_id in context
12. User: "Changed my mind"
13. Return initiated without asking for order ID

**Expected Result**:
- Order ID preserved across 3 agents
- No repeated questions
- Smooth workflow

**Test Data**: Order o302

---

### TC-027: Chat History Preservation
**Objective**: Verify chat history is copied between agents

**Steps**:
1. Transfer to OrderAgent
2. User: "Check order o302"
3. Agent: "Order o302 is In Transit..."
4. User: "What items are in it?"
5. Agent: "Wireless Earbuds"
6. User: "Create a ticket"
7. Transfer to TicketAgent
8. TicketAgent should know about order o302 and items
9. User: "The earbuds are damaged"
10. Ticket created with context

**Expected Result**:
- Chat history preserved
- TicketAgent knows about order and items
- No need to repeat information

**Test Data**: Order o302

---

### TC-028: Language Preference Preservation
**Objective**: Verify language preference persists across transfers

**Steps**:
1. User selects Bengali language
2. Transfer to OrderAgent
3. OrderAgent should respond in Bengali
4. Transfer to TicketAgent
5. TicketAgent should respond in Bengali
6. Transfer to ReturnAgent
7. ReturnAgent should respond in Bengali

**Expected Result**:
- Language preference preserved
- All agents respond in Bengali
- No language reset

**Test Data**: Language "bn-BD"

---

## 🔤 ID Formatting

### TC-029: Order ID Normalization (Capital O)
**Objective**: Verify order ID normalization handles capitals

**Steps**:
1. Transfer to OrderAgent
2. User: "Check order O302" (capital O)
3. Agent should normalize to "o302"
4. Order should be found

**Expected Result**:
- ID normalized correctly
- Order found
- No error

**Test Data**: Order o302

---

### TC-030: User ID Normalization (Capital U)
**Objective**: Verify user ID normalization handles capitals

**Steps**:
1. Transfer to OrderAgent
2. User: "Show orders for user U101" (capital U)
3. Agent should normalize to "u101"
4. Orders should be found

**Expected Result**:
- ID normalized correctly
- Orders found

**Test Data**: User u101

---

### TC-031: Ticket ID Normalization (Capital T)
**Objective**: Verify ticket ID normalization handles capitals

**Steps**:
1. Transfer to TicketAgent
2. User: "Check ticket T501" (capital T)
3. Agent should normalize to "t501"
4. Ticket should be found

**Expected Result**:
- ID normalized correctly
- Ticket found

**Test Data**: Ticket t501

---

### TC-032: Product ID Normalization (Capital P)
**Objective**: Verify product ID normalization handles capitals

**Steps**:
1. Transfer to RecommendAgent
2. User: "Show product P001" (capital P)
3. Agent should normalize to "p001"
4. Product should be found

**Expected Result**:
- ID normalized correctly
- Product found

**Test Data**: Product p001

---

### TC-033: ID with Spaces
**Objective**: Verify ID normalization handles spaces

**Steps**:
1. Transfer to OrderAgent
2. User: "Check order o 302" (with space)
3. Agent should normalize to "o302"
4. Order should be found

**Expected Result**:
- Spaces stripped
- ID normalized
- Order found

**Test Data**: Order o302

---

## 🌐 Language Switching

### TC-034: Switch to English
**Objective**: Verify language switching to English works

**Steps**:
1. User: "Switch to English"
2. Agent should call set_language("en-IN")
3. All subsequent responses in English

**Expected Result**:
- Language switched to English
- Responses in English
- Preference saved

**Test Data**: None

---

### TC-035: Switch to Bengali
**Objective**: Verify language switching to Bengali works

**Steps**:
1. User: "Switch to Bengali"
2. Agent should call set_language("bn-BD")
3. All subsequent responses in Bengali

**Expected Result**:
- Language switched to Bengali
- Responses in Bengali
- Preference saved

**Test Data**: None

---

### TC-036: Language Persistence Across Transfers
**Objective**: Verify language persists when transferring agents

**Steps**:
1. Set language to Bengali
2. Transfer to OrderAgent
3. OrderAgent responds in Bengali
4. Transfer to TicketAgent
5. TicketAgent responds in Bengali

**Expected Result**:
- Language persists
- All agents use Bengali

**Test Data**: Language "bn-BD"

---

## 🔄 Multi-Agent Workflows

### TC-037: Order → Ticket Workflow
**Objective**: Verify complete order to ticket workflow

**Steps**:
1. User: "Check my order o302"
2. Transfer to OrderAgent
3. Agent displays order details
4. User: "I have an issue with this order"
5. Transfer to TicketAgent
6. Agent uses order_id from context
7. User: "Product is damaged"
8. Ticket created successfully

**Expected Result**:
- Smooth workflow
- Context preserved
- Ticket created

**Test Data**: Order o302

---

### TC-038: Order → Return → Ticket Workflow
**Objective**: Verify complex multi-agent workflow

**Steps**:
1. User: "Check order o301"
2. Transfer to OrderAgent
3. Agent displays order
4. User: "I want to return it"
5. Transfer to ReturnAgent
6. Return initiated
7. User: "Actually, create a ticket instead"
8. Transfer to TicketAgent
9. Ticket created with order context

**Expected Result**:
- All transfers work
- Context preserved throughout
- Final ticket created successfully

**Test Data**: Order o301

---

### TC-039: Recommendation → Order Workflow
**Objective**: Verify recommendation to order workflow

**Steps**:
1. User: "Show me recommendations"
2. Transfer to RecommendAgent
3. Recommendations displayed
4. User: "Check my orders"
5. Transfer to OrderAgent
6. Orders displayed

**Expected Result**:
- Transfers work
- Context preserved

**Test Data**: User u101

---

### TC-040: Complete Customer Journey
**Objective**: Verify end-to-end customer journey

**Steps**:
1. User connects
2. Selects language (Bengali)
3. User: "Check order o302"
4. Transfer to OrderAgent
5. Order displayed
6. User: "Create ticket"
7. Transfer to TicketAgent
8. Ticket created
9. User: "Show recommendations"
10. Transfer to RecommendAgent
11. Recommendations displayed
12. User: "Add p001 to wishlist"
13. Product added

**Expected Result**:
- Complete journey works
- All agents function correctly
- Context preserved throughout

**Test Data**: Order o302, User u101, Product p001

---

## ⚠️ Edge Cases & Error Handling

### TC-041: Invalid Order ID
**Objective**: Verify handling of invalid order IDs

**Steps**:
1. Transfer to OrderAgent
2. User: "Check order invalid123"
3. Agent should handle error gracefully

**Expected Result**:
- Error message displayed
- Agent asks for correct order ID
- No system crash

**Test Data**: Order "invalid123" (does not exist)

---

### TC-042: Invalid User ID
**Objective**: Verify handling of invalid user IDs

**Steps**:
1. Transfer to OrderAgent
2. User: "Show orders for user invalid999"
3. Agent should handle error gracefully

**Expected Result**:
- Error message displayed
- Agent asks for correct user ID

**Test Data**: User "invalid999" (does not exist)

---

### TC-043: Empty Input
**Objective**: Verify handling of empty input

**Steps**:
1. User sends empty message
2. Agent should handle gracefully

**Expected Result**:
- Agent asks for clarification
- No error

**Test Data**: None

---

### TC-044: Rapid Agent Transfers
**Objective**: Verify system handles rapid transfers

**Steps**:
1. Transfer to OrderAgent
2. Immediately transfer to TicketAgent
3. Immediately transfer to ReturnAgent
4. Immediately transfer to RecommendAgent

**Expected Result**:
- All transfers work
- No context loss
- System stable

**Test Data**: None

---

### TC-045: Create Ticket for Non-Existent Order
**Objective**: Verify error handling for ticket creation

**Steps**:
1. Transfer to TicketAgent
2. User: "Create ticket for order o999"
3. Agent should validate order exists
4. Handle error gracefully

**Expected Result**:
- Error message displayed
- Agent asks for valid order ID

**Test Data**: Order o999 (does not exist)

---

### TC-046: Return for Non-Existent Order
**Objective**: Verify error handling for return initiation

**Steps**:
1. Transfer to ReturnAgent
2. User: "Return order o999"
3. Agent should validate order exists
4. Handle error gracefully

**Expected Result**:
- Error message displayed
- Agent asks for valid order ID

**Test Data**: Order o999 (does not exist)

---

### TC-047: Multiple Orders Same User
**Objective**: Verify handling of users with multiple orders

**Steps**:
1. Transfer to OrderAgent
2. User: "Show all orders for u101"
3. Agent should display all orders
4. User: "Check order o301"
5. Agent should display specific order

**Expected Result**:
- All orders displayed
- Specific order retrieved correctly

**Test Data**: User u101 (has orders o301, o302)

---

### TC-048: Order with Multiple Items
**Objective**: Verify handling of orders with multiple items

**Steps**:
1. Transfer to OrderAgent
2. User: "Check order o301"
3. Agent should display all items

**Expected Result**:
- All items displayed
- Correct quantities shown

**Test Data**: Order o301 (has multiple items)

---

### TC-049: Ticket Status Variations
**Objective**: Verify handling of different ticket statuses

**Steps**:
1. Transfer to TicketAgent
2. Check tickets with different statuses:
   - t501 (Resolved)
   - t502 (Open)
   - t503 (In Progress)

**Expected Result**:
- All statuses displayed correctly
- Appropriate responses

**Test Data**: Tickets t501, t502, t503

---

### TC-050: Return Status Variations
**Objective**: Verify handling of different return statuses

**Steps**:
1. Transfer to ReturnAgent
2. Check returns with different statuses:
   - o301 (Pending Courier Pickup)
   - o304 (In Transit)
   - o305 (Received)

**Expected Result**:
- All statuses displayed correctly
- Appropriate responses

**Test Data**: Returns for o301, o304, o305

---

## 📊 Test Execution Checklist

### Pre-Test Setup
- [ ] Database initialized with seed data
- [ ] All agents registered correctly
- [ ] Frontend connected to backend
- [ ] LiveKit credentials configured

### Test Execution
- [ ] Run all routing tests (TC-001 to TC-006)
- [ ] Run all order management tests (TC-007 to TC-012)
- [ ] Run all ticket tests (TC-013 to TC-017)
- [ ] Run all return tests (TC-018 to TC-021)
- [ ] Run all recommendation tests (TC-022 to TC-025)
- [ ] Run all context preservation tests (TC-026 to TC-028)
- [ ] Run all ID formatting tests (TC-029 to TC-033)
- [ ] Run all language switching tests (TC-034 to TC-036)
- [ ] Run all multi-agent workflow tests (TC-037 to TC-040)
- [ ] Run all edge case tests (TC-041 to TC-050)

### Post-Test Verification
- [ ] All tests passed
- [ ] No system crashes
- [ ] Database integrity maintained
- [ ] Logs reviewed for errors

---

## 🎯 Priority Test Cases (Must Pass)

### Critical Path Tests:
1. **TC-001**: Initial Greeting and Language Selection
2. **TC-002**: Route to OrderAgent
3. **TC-007**: Get Order Details by Order ID
4. **TC-008**: Get Order Details with Capitalized ID (ID normalization)
5. **TC-013**: Create Support Ticket
6. **TC-014**: Create Ticket with Order ID in Context (Context preservation)
7. **TC-026**: Multi-Agent Context Preservation
8. **TC-037**: Order → Ticket Workflow

### High Priority Tests:
- TC-003 to TC-006: All routing tests
- TC-018 to TC-021: All return tests
- TC-029 to TC-033: All ID formatting tests
- TC-034 to TC-036: Language switching tests

---

## 📝 Test Data Reference

### Users:
- u101: Alex (has orders o301, o302)
- u102: Mehedi (has order o303)
- u103: Sarah (has order o304)
- u104: Rahman (has order o305)
- u105: Emily (has order o306)

### Orders:
- o301: Delivered, User u101, Amount 320.00
- o302: In Transit, User u101, Amount 79.99
- o303: Processing, User u102, Amount 19.99
- o304: Delivered, User u103, Amount 899.99
- o305: Delivered, User u104, Amount 249.99

### Tickets:
- t501: Resolved, Order o301, Issue "Damaged product"
- t502: Open, Order o304, Issue "Wrong item received"
- t503: In Progress, Order o305, Issue "Missing item"

### Products:
- p001: Smartphone, 299.99
- p002: Wireless Earbuds, 79.99
- p003: Phone Case, 19.99
- p004: USB-C Charger, 15.99
- p005: Laptop, 899.99

---

## 🔍 Test Execution Notes

1. **Test Environment**: Ensure database is fresh or reset before testing
2. **Voice Input**: Use clear pronunciation for IDs (e.g., "o three zero two")
3. **Context Testing**: Test context preservation by transferring between agents
4. **Error Handling**: Verify graceful error handling for invalid inputs
5. **Language Testing**: Test both English and Bengali responses
6. **ID Formatting**: Test various ID formats (capital, lowercase, with spaces)

---

## ✅ Success Criteria

- All critical path tests pass
- ID normalization works for all ID types
- Context preservation works across all agent transfers
- Language switching works correctly
- Error handling is graceful
- No system crashes or data corruption
- Database operations complete successfully

