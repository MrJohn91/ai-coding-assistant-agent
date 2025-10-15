# Sales Bike Agent - API Design

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication required (add Bearer token in production).

## Endpoints

### 1. Health Check
Check API health status.

**Endpoint:** `GET /health`

**Response:** `200 OK`
```json
{
  "status": "ok"
}
```

---

### 2. Create Conversation
Start a new conversation session.

**Endpoint:** `POST /api/v1/conversations`

**Response:** `201 Created`
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Hello! I'm your bike shop assistant. What type of bike are you looking for today?"
}
```

---

### 3. Send Message
Send a message in an existing conversation.

**Endpoint:** `POST /api/v1/conversations/{session_id}/messages`

**Request Body:**
```json
{
  "message": "I'm looking for a mountain bike"
}
```

**Response:** `200 OK`
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "Great choice! I have several mountain bikes...",
  "products": [
    {
      "id": 1,
      "name": "Trailblazer 500",
      "type": "Mountain Bike",
      "brand": "RockRider",
      "price_eur": 1499,
      "key_features": "Aluminum frame, 12 gears, Hydraulic Disc",
      "intended_use": ["Trail", "Off-road"]
    }
  ],
  "lead_created": false
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Conversation {session_id} not found or expired"
}
```

---

### 4. Get Conversation History
Retrieve full conversation history.

**Endpoint:** `GET /api/v1/conversations/{session_id}`

**Response:** `200 OK`
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "messages": [
    {
      "role": "user",
      "content": "I'm looking for a bike",
      "timestamp": "2025-10-13T16:00:00Z"
    },
    {
      "role": "assistant",
      "content": "Great! What type of bike...",
      "timestamp": "2025-10-13T16:00:02Z"
    }
  ],
  "state": "DISCOVERY",
  "created_at": "2025-10-13T16:00:00Z"
}
```

---

### 5. Delete Conversation
End and delete a conversation session.

**Endpoint:** `DELETE /api/v1/conversations/{session_id}`

**Response:** `204 No Content`

**Error Response:** `404 Not Found`

---

## Data Models

### MessageRequest
```json
{
  "message": "string (required, min 1 char)"
}
```

### MessageResponse
```json
{
  "session_id": "string (UUID)",
  "response": "string",
  "products": "array of ProductRecommendation | null",
  "lead_created": "boolean"
}
```

### ProductRecommendation
```json
{
  "id": "integer",
  "name": "string",
  "type": "string",
  "brand": "string",
  "price_eur": "integer",
  "key_features": "string",
  "intended_use": "array of string"
}
```

### ConversationHistoryResponse
```json
{
  "session_id": "string (UUID)",
  "messages": "array of Message",
  "state": "string (GREETING|DISCOVERY|...)",
  "created_at": "string (ISO 8601)"
}
```

---

## Conversation States

| State | Description |
|-------|-------------|
| `GREETING` | Initial contact |
| `DISCOVERY` | Understanding customer needs |
| `RECOMMENDATION` | Showing products |
| `INTEREST_CONFIRMED` | Customer shows buying intent |
| `NAME_COLLECTED` | Name captured |
| `EMAIL_COLLECTED` | Email captured |
| `PHONE_COLLECTED` | Phone captured |
| `LEAD_CREATED` | Lead successfully created in CRM |
| `FAQ_MODE` | Answering general questions |

---

## Error Codes

| Code | Description |
|------|-------------|
| `200` | Success |
| `201` | Created |
| `204` | No Content (successful deletion) |
| `400` | Bad Request (invalid input) |
| `404` | Not Found (session not found or expired) |
| `422` | Validation Error (Pydantic) |
| `500` | Internal Server Error |

---

## Rate Limiting

Currently no rate limiting. Recommended for production:
- 60 requests/minute per IP
- 10 sessions/minute per IP

---

## Example Workflows

### Simple Product Inquiry
```
POST /api/v1/conversations
→ {"session_id": "abc123", "message": "Hello..."}

POST /api/v1/conversations/abc123/messages
Body: {"message": "I need a city bike"}
→ {"response": "...", "products": [...]}
```

### Full Lead Capture Flow
```
1. POST /api/v1/conversations
2. POST /conversations/{id}/messages {"message": "mountain bike"}
3. POST /conversations/{id}/messages {"message": "I like the Trailblazer"}
4. POST /conversations/{id}/messages {"message": "John Doe"}
5. POST /conversations/{id}/messages {"message": "john@example.com"}
6. POST /conversations/{id}/messages {"message": "+491234567890"}
   → {"lead_created": true}
```

---

## WebSocket Support (Future)

Planned for real-time chat:
```
WS /ws/{session_id}
```

Message format:
```json
{
  "type": "message",
  "content": "Hello",
  "timestamp": "2025-10-13T16:00:00Z"
}
```
