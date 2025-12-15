import os
from groq import Groq
import dotenv
dotenv.load_dotenv()    

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


SYSTEM_PROMPT = (
    "You are BOT GPT, a helpful, concise and professional AI assistant."
)

MAX_HISTORY_MESSAGES = 10  # sliding window


def build_llm_messages(history, user_message: str):
    """
    Builds messages in OpenAI-compatible format
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in history[-MAX_HISTORY_MESSAGES:]:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })

    messages.append({"role": "user", "content": user_message})
    return messages


def call_llm(history, user_message: str) -> str:
    messages = build_llm_messages(history, user_message)
    response = "dummy response for now to avoid llm calls"
    # response = client.chat.completions.create(
    #     model="llama-3.3-70b-versatile",
    #     messages=messages,
    #     temperature=0.7,
    #     max_tokens=512,
    # )

    return response.choices[0].message.content
