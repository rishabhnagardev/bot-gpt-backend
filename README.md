cURL
cURL
cURL
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

  - Example cURL (open chat):

```
curl -X POST -H "X-User-Email: alice@example.com" \
  -F "content=Explain microservices" \
  http://localhost:8000/conversations/1/messages
```

  - Example cURL (RAG + PDF upload):

```
curl -X POST -H "X-User-Email: alice@example.com" \
  -F "content=Summarize this document" \
  -F "file=@policy.pdf" \
  http://localhost:8000/conversations/2/messages
```

## Diagram placeholders (where to add visuals)
- DIAGRAM: Add sequence diagram for **Open Chat Flow** here (mermaid). This should show: client -> API -> DB save user message -> services -> LLM -> save assistant -> return response.
- DIAGRAM: Add sequence diagram for **RAG Flow (PDF)** here (mermaid). This should show: client -> API (upload PDF) -> PDF extractor -> DB store document & link -> retriever -> LLM -> save assistant -> return response.
- DIAGRAM: Add component diagram for high-level architecture here (clients, API, services, DB, LLM, PDF service).

## How to render the mermaid diagrams
Use https://mermaid.live — paste the mermaid script and export PNG/SVG.

## Context & cost management (concise)
- Keep a sliding window of most recent messages (controlled by `MAX_RAW_MESSAGES` in `message_service`).
- When the window is exceeded, older messages are summarized (see `summarization_service`).
- In RAG mode, documents linked to a conversation are chunked and retrieval injects top-k chunks only.

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

---
Add your diagrams where the DIAGRAM placeholders are noted above.