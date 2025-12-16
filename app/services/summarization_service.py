from types import SimpleNamespace
from app.services.llm_service import call_llm

SUMMARY_PROMPT = """
Summarize the following conversation briefly.
Focus on key facts, decisions and context.
"""


async def summarize_messages(messages):
    """Generate a short summary for a list of messages using the async LLM.

    Returns the assistant text as a string.
    """
    text = "\n".join(f"{m.role}: {m.content}" for m in messages)

    # Build a minimal conversation object expected by call_llm
    convo = SimpleNamespace(summary=None, id=None)
    # Combine prompt and text into a single user message
    user_message = f"{SUMMARY_PROMPT}\n\n{text}"

    reply = await call_llm(convo, recent_messages=[], user_message=user_message)
    return reply
