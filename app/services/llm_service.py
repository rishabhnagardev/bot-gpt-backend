import asyncio
import logging
import os
from groq import Groq
import dotenv

dotenv.load_dotenv()

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are BOT GPT, a helpful, concise and professional AI assistant."
)

MAX_HISTORY_MESSAGES = 10  # sliding window

# Initialize Groq client (blocking SDK) if API key is present
_GROQ_API_KEY = os.getenv("GROQ_API_KEY")
_groq_client = None
if _GROQ_API_KEY:
    try:
        _groq_client = Groq(api_key=_GROQ_API_KEY)
    except Exception:
        logger.exception("Failed to initialize Groq client")


def build_llm_messages(conversation, recent_messages, user_message, context_chunks=None):
    """Compose messages to send to the LLM.

    This is a small helper that builds the chat-style message list from the
    conversation summary, recent messages and optional retrieval context.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if conversation.summary:
        messages.append({
            "role": "system",
            "content": f"Conversation summary: {conversation.summary}"
        })

    if context_chunks:
        context_text = "\n".join(context_chunks)
        messages.append({
            "role": "system",
            "content": f"Use the following context to answer:\n{context_text}"
        })

    for msg in recent_messages[-MAX_HISTORY_MESSAGES:]:
        messages.append({"role": msg.role, "content": msg.content})

    messages.append({"role": "user", "content": user_message})
    return messages


async def call_llm(conversation, recent_messages, user_message: str, context_chunks=None) -> str:
    """Asynchronously call the Groq LLM and return assistant text.

    Uses the blocking Groq SDK inside `asyncio.to_thread` so callers can
    await this function without blocking the event loop. If the Groq API
    key is not configured, the function falls back to a mocked reply.
    """
    messages = build_llm_messages(conversation, recent_messages, user_message, context_chunks)
    logger.info("Calling LLM for conversation %s (messages=%d)", getattr(conversation, 'id', None), len(messages))

    if not _groq_client:
        logger.warning("GROQ_API_KEY not set; returning mocked reply")
        await asyncio.sleep(0.05)
        return f"(mock) Echo: {user_message[:200]}"

    # Run the blocking SDK call in a thread to keep this function async
    try:
        response = await asyncio.to_thread(
            _groq_client.chat.completions.create,
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=512,
        )

        # Extract assistant content (SDK returns choices with message)
        return response.choices[0].message.content
    except Exception:
        logger.exception("Groq LLM call failed")
        # Fallback to a safe mocked reply instead of raising
        return f"(error) LLM call failed; using fallback response for: {user_message[:120]}"
