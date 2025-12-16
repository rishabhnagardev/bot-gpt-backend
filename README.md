# BOT GPT – Conversational Backend (FastAPI)

Short backend for a conversational AI system (Open Chat + RAG).

## Quick Links
- **Code:** [app/main.py](app/main.py)
- **APIs:** [app/api/conversations.py](app/api/conversations.py), [app/api/messages.py](app/api/messages.py)
- **Services:** [app/services/conversation_service.py](app/services/conversation_service.py), [app/services/message_service.py](app/services/message_service.py)

## Overview
This project provides a FastAPI backend that:
- Persists conversations and messages
- Supports Open Chat (LLM-only) and RAG (PDF-backed) modes
- Summarizes old messages to control token usage
- Retrieves relevant document chunks for RAG

## Architecture (high level)
Client -> FastAPI routers -> Services (conversation/message/rag) -> LLM / PDF service

## Data model (brief)
- `User` owns `Conversation`
- `Conversation` has `Message` objects and optional `summary` and `mode` (`open` | `rag`)
- `Document` linked via `ConversationDocument`

## API Endpoints (summary)

- **Create conversation**: `POST /conversations`
  - Body: `{ "user_email": "...", "mode": "open"|"rag", "title": "optional" }`
  - See: [app/api/conversations.py](app/api/conversations.py)

- **List conversations**: `GET /conversations?user_email=...&limit=20&offset=0`

  - Authentication: Requires header `X-User-Email` matching `user_email`.
  - Example cURL:

```
curl -H "X-User-Email: alice@example.com" \
  "http://localhost:8000/conversations?user_email=alice@example.com"
```

- **Get conversation**: `GET /conversations/{conversation_id}`

  - Authentication: Requires header `X-User-Email` and the conversation must belong to that user.
  - Example cURL:

```
curl -H "X-User-Email: alice@example.com" \
  http://localhost:8000/conversations/1
```

- **Delete conversation**: `DELETE /conversations/{conversation_id}`

  - Authentication: Requires header `X-User-Email` and ownership check.

  - Example cURL:

```
curl -X DELETE -H "X-User-Email: alice@example.com" \
  http://localhost:8000/conversations/1
```

- **Send message**: `POST /conversations/{conversation_id}/messages`
  - Form fields: `content` (string), optional `file` (PDF — only allowed when conversation.mode == `rag`)
  - See: [app/api/messages.py](app/api/messages.py)

  - Authentication: Requires `X-User-Email` header and ownership check.
  - Note: LLM calls are performed asynchronously; the endpoint awaits the response but the implementation uses a mocked async LLM client.
# BOT GPT – Conversational Backend (FastAPI)

Lightweight backend for a conversational AI system supporting Open Chat and RAG (PDF ingestion).

This README is a compact design + API reference for engineers. Diagrams are Mermaid-friendly (paste into mermaid.live or mermaid.com).

**Contents**
- Architecture diagram (Mermaid)
- Sequence diagram (Mermaid)
- API summary
- Data schema
- LLM context & cost management
- RAG flow
- Scalability & error handling notes

---

**Architecture (compact)**

```mermaid
flowchart LR
  A[Client] --> C[FastAPI App]
  C --> D[(Postgres)]
  C --> E[(Redis / In-Memory TTL Cache)]
  C --> DOC[(Documents table in Postgres)]
  C --> G[(LLM API)]
```

---

**Sequence diagram (message send)**

Paste to mermaid.live; script below:

```mermaid
sequenceDiagram
  participant User
  participant Client
  participant API
  participant Auth
  participant DB
  participant MsgSvc
  participant DOC
  participant LLM

  User->>Client: submit message
  Client->>API: POST /conversations/{id}/messages
  API->>Auth: validate X-User-Email
  Auth-->>API: user
  API->>DB: fetch conversation
  API->>MsgSvc: store user message
  MsgSvc->>DB: insert message
  alt mode == rag
    MsgSvc->>DOC: retrieve linked documents / chunks (simple retriever)
    DOC-->>MsgSvc: relevant text
  end
  MsgSvc->>LLM: call_llm(context)
  LLM-->>MsgSvc: reply
  MsgSvc->>DB: store assistant message
  MsgSvc-->>API: assistant content
  API-->>Client: 200 {content}

```

---

**API summary (quick)**

- POST /conversations
  - Body: { user_email, title?, mode: open|rag }
  - Response: { id, user_id, mode, created_at }

Small diagrams for these endpoints (paste to mermaid.live):

POST /conversations

```mermaid
sequenceDiagram
  participant Client
  participant API
  participant DB

  Client->>API: POST /conversations {user_email, mode}
  API->>DB: create user (if needed) and conversation
  DB-->>API: conversation id
  API-->>Client: 201 {id, mode}
```

POST /conversations/{id}/messages

```mermaid
sequenceDiagram
  participant Client
  participant API
  participant DB
  participant MsgSvc
  participant LLM

  Client->>API: POST /conversations/{id}/messages (content, optional PDF)
  API->>DB: fetch conversation
  API->>MsgSvc: persist user message
  MsgSvc->>DB: store message (and document row if PDF)
  MsgSvc->>LLM: call_llm(context)
  LLM-->>MsgSvc: assistant reply
  MsgSvc->>DB: store assistant message
  API-->>Client: 200 {content}
```

- GET /conversations?user_email=...
  - Response: list of conversation summaries

- GET /conversations/{id}
  - Response: conversation with messages (paginated)

- DELETE /conversations/{id}
  - Auth required (X-User-Email)

- POST /conversations/{id}/messages
  - Form: content (string), file (optional PDF, only allowed in `rag` mode)
  - Headers: X-User-Email for ownership check
  - Response: persisted assistant message

Notes: endpoints enforce `conversation.user_id == current_user.id`. LLM calls are awaited by the message processing service which runs asynchronously.

---

**Data model (concise)**

Tables:

users(id PK, email UNIQUE, created_at)

conversations(id PK, user_id FK, title, mode, created_at)

messages(id PK, conversation_id FK, seq INT, role TEXT, content TEXT, created_at TIMESTAMP)

documents(id PK, filename, content TEXT, created_at)

conversation_documents(id PK, conversation_id FK, document_id FK)

---

**LLM Context & Cost Management**

How context is constructed:
1. System prompt / instructions
2. RAG context (top_k chunks retrieved from `documents` linked to the conversation) — only when mode == `rag`
3. Recent raw messages (sliding window)
4. Summaries for older history
5. Latest user message

When history exceeds model limits:
- Apply windowing: keep last M raw messages
- Replace older messages with a periodic summary message
- Optionally compress older history (summarize then store)

Cost-reduction strategies:
- Use cheaper/smaller models for summarization and reranking
- Summarize older history in background, not on every request
- Cache LLM responses for repeated prompts
- Limit `max_tokens` and tune stop sequences
- Batch or queue heavy LLM tasks and use async workers

---

**RAG flow (brief, current implementation)**

1. Ingest PDF -> extract text -> chunk (configurable size) -> store chunks as `documents` rows linked to the conversation
2. At query: retrieve relevant chunks from `documents` using simple substring/ranking heuristics (our `rag_service`) — no vector DB in this implementation
3. Provide top_k chunks as context to the LLM

Implementation note: this repo uses a DB-backed document store and a simple retriever. If you need vector similarity at scale, consider adding a vector DB later.

---

**Scaling & bottlenecks**

Primary bottlenecks at large scale (1M users):
- LLM throughput and token cost
- DB write/read throughput for messages and documents
- Document retrieval latency (if many large documents per conversation)

Scaling strategies:
- App: horizontal stateless FastAPI instances behind a load balancer
- DB: read replicas, partitioning (by user or time), sharding for writes
- LLM: queue calls, worker autoscaling, use cheaper models as fallback
- Use caching (Redis) for hot conversations and recent messages

Pattern: Prefer CQRS for separation of read/write workloads and background workers for heavy tasks (summaries, embeddings, PDF processing).

---

**Operational & error handling**

- Timeouts and circuit breakers for external LLM providers
- Retries with exponential backoff for transient failures
- Idempotency support for message ingestion
- Monitor token usage, latency, and error rates; add quotas & rate-limiting per user


## Additional implementation notes

- **Auth:** Protected endpoints expect `X-User-Email` header and enforce ownership for conversation reads/updates/deletes and message posting. See [app/api/deps.py](app/api/deps.py).
- **Caching:** A simple in-memory cache is used for `get_conversation` to reduce DB hits. See [app/db/cache.py](app/db/cache.py). Cache is invalidated when conversations or messages change.
- **Logging:** Basic application logging is configured in [app/main.py](app/main.py). Handlers and services log key events.
- **Async LLM calls:** `app/services/llm_service.py` exposes an `async call_llm(...)` entrypoint; `message_service.process_user_message` awaits it so handlers are non-blocking.

## Running locally
1. Create venv: `python -m venv venv`
2. Activate: `source venv/bin/activate`
3. Install: `pip install -r requirements.txt`
4. Run: `uvicorn app.main:app --reload`
5. Open API docs: `http://localhost:8000/docs`

## Tests
- Run: `pytest`

## Docker
- Build: `docker build -t bot-gpt .`
- Run: `docker run -p 8000:8000 bot-gpt`

## Notes & future improvements
- Async LLM calls, streaming, vector DB, auth, background PDF processing.