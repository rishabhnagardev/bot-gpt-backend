from app.services.llm_service import client

SUMMARY_PROMPT = """
Summarize the following conversation briefly.
Focus on key facts, decisions and context.
"""


def summarize_messages(messages):
    text = "\n".join(
        f"{m.role}: {m.content}" for m in messages
    )

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": SUMMARY_PROMPT},
            {"role": "user", "content": text}
        ],
        temperature=0.3,
        max_tokens=200
    )

    return response.choices[0].message.content
