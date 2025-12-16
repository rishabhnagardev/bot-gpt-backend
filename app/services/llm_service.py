import os
from groq import Groq
import dotenv
dotenv.load_dotenv()    

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


SYSTEM_PROMPT = (
    "You are BOT GPT, a helpful, concise and professional AI assistant."
)

MAX_HISTORY_MESSAGES = 10  # sliding window

def build_llm_messages(conversation, recent_messages, user_message):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if conversation.summary:
        messages.append({
            "role": "system",
            "content": f"Conversation summary: {conversation.summary}"
        })

    for msg in recent_messages:
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
