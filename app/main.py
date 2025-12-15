from fastapi import FastAPI

app = FastAPI(
    title="BOT GPT Backend",
    description="Conversational AI backend for BOT Consulting",
    version="0.1.0"
)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "bot-gpt-backend"
    }
