# Sales Bike Agent API - Complete Testing Guide

## Prerequisites

1. ✅ Server is running on `http://localhost:8000`
2. ✅ Postman is installed on your computer
3. ✅ Mem0 API key is configured in `.env`
4. ✅ OpenAI API key is configured in `.env`

---

## Part 1: Import the Postman Collection

### Step 1: Open Postman
- Launch the Postman application on your computer

### Step 2: Import the Collection
1. Click the **Import** button in the top-left corner
2. Click **Upload Files** or drag and drop
3. Navigate to: `/Users/vee/Desktop/Archon/sales_bike/`
4. Select: `Sales_Bike_Agent_API.postman_collection.json`
5. Click **Import**

### Step 3: Verify Import
- You should see a new collection called **"Sales Bike Agent API"**
- It should contain 13 requests organized in folders
- Click on the collection to expand it

---

## Part 2: Set Up Environment (Optional but Recommended)

### Step 1: Create a New Environment
1. Click **Environments** in the left sidebar
2. Click **+ Create New Environment**
3. Name it: `Sales Bike Local`

### Step 2: Add Variables
Add these two variables:

| Variable | Type | Initial Value | Current Value |
|----------|------|---------------|---------------|
| `base_url` | default | `http://localhost:8000` | `http://localhost:8000` |
| ` session_id` | default | (leave empty) | (leave empty) |

3. Click **Save**
4. Select this environment from the dropdown in top-right

**Note:** If you skip this step, the collection will auto-generate a session_id for you.

---

## Part 3: Test Complete Customer Journey (Recommended Path)

Follow these requests **IN ORDER** for the best test experience:

### Test 1: Health Check ✅

**Purpose:** Verify the server is running

1. Expand the collection
2. Click on **"Health Check"**
3. Click the blue **Send** button
4. **Expected Response:**
```json
{
    "status": "ok"
}
```
5. Status: **200 OK**

---

### Test 2: Pydantic AI Health Check 🔍

**Purpose:** Verify Mem0 and all components are working

1. Click on **"Pydantic AI Health Check"**
2. Click **Send**
3. **Expected Response:**
```json
{
    "status": "ok",
    "agent": "pydantic_ai",
    "components": {
        "mcp_client": false,
        "memory_client": true,  // ← Should be TRUE
        "http_client": true,
        "orchestrator": true
    }
}
```
4. Status: **200 OK**
5. ✅ **Check:** `memory_client` should be `true` (Mem0 is working!)

---

### Test 3: Mountain Bike Inquiry 🚵

**Purpose:** Test product search tool

1. Click on **"V2 - Send Message (Mountain Bike Inquiry)"**
2. Review the request body:
```json
{
    "message": "I'm looking for a mountain bike for trail riding under €2000. What do you recommend?"
}
```
3. Click **Send**
4. **Expected Response:**
```json
{
    "session_id": "abc-123-def-456...",
    "response": "I'd be happy to help you find a mountain bike! Based on your budget...",
    "products": null,
    "lead_created": false
}
```
5. Status: **200 OK**
6. ✅ **Check:** The response should mention specific bike models

**What happens behind the scenes:**
- Pydantic AI agent receives your message
- Agent calls `search_products` tool
- Tool searches product catalog via Archon RAG
- Agent generates personalized response

---

### Test 4: FAQ Question ❓

**Purpose:** Test FAQ search tool

1. Click on **"V2 - Send Message (FAQ Question)"**
2. Request body:
```json
{
    "message": "What's your warranty policy on mountain bikes?"
}
```
3. Click **Send**
4. **Expected Response:** Agent should provide warranty information from FAQ
5. Status: **200 OK**

**What happens behind the scenes:**
- Agent calls `search_faq` tool
- Tool searches FAQ knowledge base
- Agent provides answer based on FAQ content

---

### Test 5: Express Purchase Intent 🛒

**Purpose:** Trigger lead capture flow

1. Click on **"V2 - Send Message (Purchase Intent)"**
2. Request body:
```json
{
    "message": "The Trailblazer 500 looks perfect! I want to buy it. How do I proceed?"
}
```
3. Click **Send**
4. **Expected Response:** Agent should:
   - Express enthusiasm
   - Ask for your name
   - Example: "Great choice! May I have your name?"
5. Status: **200 OK**

**What happens behind the scenes:**
- Agent detects purchase intent keywords
- System prompt guides agent to start lead capture flow
- Agent asks for customer information

---

### Test 6: Provide Name 👤

**Purpose:** First step of lead capture

1. Click on **"V2 - Send Message (Provide Name)"**
2. Request body:
```json
{
    "message": "My name is John Doe"
}
```
3. Click **Send**
4. **Expected Response:** Agent should:
   - Acknowledge the name
   - Ask for email address
   - Example: "Thank you, John! What's the best email to reach you at?"
5. Status: **200 OK**

---

### Test 7: Provide Email 📧 (Lead Created!)

**Purpose:** Trigger `capture_lead` tool

1. Click on **"V2 - Send Message (Provide Email)"**
2. Request body:
```json
{
    "message": "john.doe@example.com"
}
```
3. Click **Send**
4. **Expected Response:** Agent should:
   - Confirm lead creation
   - Mention sales team will contact
   - Example: "Thank you John! I've recorded your information. Our sales team will contact you soon at john.doe@example.com."
5. Status: **200 OK**

**What happens behind the scenes:**
- Agent calls `capture_lead` tool with name="John Doe", email="john.doe@example.com"
- Email validation occurs (regex check)
- CRM client creates lead (will fail with placeholder URL, but that's expected)
- Agent confirms to customer

---

### Test 8: Provide Phone (Optional) 📱

**Purpose:** Add optional phone number to lead

1. Click on **"V2 - Send Message (Provide Phone - Optional)"**
2. Request body:
```json
{
    "message": "My phone is +1-555-123-4567"
}
```
3. Click **Send**
4. **Expected Response:** Agent acknowledges phone number
5. Status: **200 OK**

---

### Test 9: Returning Customer - Mem0 Memory Test 🧠

**Purpose:** Test Mem0 conversation memory recall

1. Click on **"V2 - Send Message (Returning Customer - Test Mem0)"**
2. Request body:
```json
{
    "message": "Hi! I'm back. I was looking at mountain bikes last time."
}
```
3. Click **Send**
4. **Expected Behavior:**
   - If using **same session_id**: Agent has full context from session
   - If Mem0 is working: Agent may recall preferences from memory
   - Agent should reference previous conversation

**What happens behind the scenes:**
- Agent may call `recall_customer_preferences` tool
- Mem0 searches for memories associated with user_id
- Agent personalizes response based on memory

---

### Test 10: Price Filtering 💰

**Purpose:** Test advanced product search with filters

1. Click on **"V2 - Send Message (Price Filtering)"**
2. Request body:
```json
{
    "message": "Show me electric bikes under €3000"
}
```
3. Click **Send**
4. **Expected Response:** Agent should list electric bikes under €3000
5. Status: **200 OK**

**What happens behind the scenes:**
- Agent calls `search_products` with max_price=3000
- Tool filters products by price
- Agent presents filtered results

---

## Part 4: Advanced Testing

### Testing with Different Session IDs

**To test Mem0 memory across different sessions:**

1. After completing Test 1-8, **note down your session_id** from any response
2. In Postman, go to **Environments** (top-right dropdown)
3. Click **Edit** on your environment
4. Change the `session_id` to a **new UUID** (or delete it to auto-generate)
5. Run Test 9 again - this simulates a new session
6. If Mem0 memory is working, agent should still recall previous conversation

### Manual Session ID Creation

To use a specific session ID:

1. Go to Environments → Edit
2. Set `session_id` to any UUID format, e.g.: `test-session-123`
3. All requests will now use this session ID
4. This is useful for debugging specific sessions

---

## Part 5: Monitor Server Logs

### Watch What's Happening Behind the Scenes

Open your terminal where the server is running and watch the logs:

**What to look for:**

1. **Request received:**
```
INFO: 127.0.0.1:12345 - "POST /api/v2/conversations/{session_id}/messages HTTP/1.1" 200 OK
```

2. **Tool calls:**
```
INFO: [Pydantic AI] Processing message in session abc-123...
```

3. **Mem0 operations:**
```
INFO: Saving conversation memory for user: abc-123
INFO: HTTP Request: POST https://api.mem0.ai/v1/memories/ "HTTP/1.1 200 OK"
```

4. **Lead capture:**
```
INFO: Capturing lead: name=John Doe, email=john.doe@example.com
```

---

## Part 6: Troubleshooting

### Issue 1: "Session not found"
**Solution:**
- Make sure you're using the same `session_id` variable
- Create a new session by changing the session_id in environment variables

### Issue 2: No response from agent
**Solution:**
- Check server logs for errors
- Verify OpenAI API key is valid
- Check if server is still running

### Issue 3: Mem0 memory_client is false
**Solution:**
- Verify `MEM0_API_KEY` is set correctly in `.env` file
- Restart the server
- Run health check again

### Issue 4: Agent doesn't capture lead
**Solution:**
- Use clear purchase intent language
- Try: "I want to buy this bike"
- Make sure to provide valid email format

---

## Part 7: Understanding the Response Structure

### Standard Response Format

```json
{
    "session_id": "uuid-format-string",
    "response": "Agent's text response",
    "products": null,  // Will be populated in future updates
    "lead_created": false  // Will be true when lead is captured
}
```

### What Each Field Means:

- **session_id**: Unique identifier for this conversation
- **response**: The agent's reply to your message
- **products**: List of recommended products (currently null in v2)
- **lead_created**: Boolean indicating if a CRM lead was created

---

## Part 8: Expected Timeline

**Complete test should take about 10-15 minutes:**

- ✅ Part 1 (Import): 2 minutes
- ✅ Part 2 (Environment): 2 minutes
- ✅ Part 3 (Tests 1-10): 8-10 minutes
- ✅ Part 4 (Advanced): 3 minutes (optional)

---

## Quick Reference: Test Order

1. ✅ Health Check
2. 🔍 Pydantic AI Health Check (verify Mem0 = true)
3. 🚵 Mountain Bike Inquiry
4. ❓ FAQ Question
5. 🛒 Purchase Intent
6. 👤 Provide Name
7. 📧 Provide Email (lead created!)
8. 📱 Provide Phone (optional)
9. 🧠 Returning Customer (Mem0 test)
10. 💰 Price Filtering

---

## Success Criteria

You've successfully tested everything if:

- ✅ Health checks return 200 OK
- ✅ Mem0 memory_client shows `true`
- ✅ Agent responds to product inquiries
- ✅ Agent answers FAQ questions
- ✅ Agent detects purchase intent
- ✅ Agent collects name and email
- ✅ Lead capture flow completes
- ✅ Agent uses natural conversation
- ✅ Price filtering works correctly

---

## What's Next?

After testing, you can:

1. **Customize the messages** - Edit any request body to try different conversations
2. **Test edge cases** - Invalid emails, different price ranges, etc.
3. **Monitor Mem0 dashboard** - Check if memories are being stored (if you have Mem0 dashboard access)
4. **Integrate with real CRM** - Update the CRM API URL in `.env` to test actual lead creation

---

## Support

If you encounter any issues:

1. Check the server logs for detailed error messages
2. Verify all environment variables are set correctly
3. Ensure Mem0 API key is valid
4. Restart the server if needed

Happy Testing! 🎉
