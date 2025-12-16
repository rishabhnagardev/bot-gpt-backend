from app.services import llm_service, message_service


def test_send_message_open_mode(client, monkeypatch):
    async def mock_llm(*args, **kwargs):
        return "Hello from mock LLM"

    monkeypatch.setattr(
        llm_service,
        "call_llm",
        mock_llm
    )
    # message_service may have imported call_llm directly; patch that reference too
    monkeypatch.setattr(
        message_service,
        "call_llm",
        mock_llm
    )

    # create conversation (include user_email)
    conv = client.post(
        "/conversations",
        json={"user_email": "test@example.com", "mode": "open"}
    ).json()

    # send message (include X-User-Email header for auth/ownership)
    response = client.post(
        f"/conversations/{conv['id']}/messages",
        data={"content": "Hi"},
        headers={"X-User-Email": "test@example.com"}
    )

    assert response.status_code == 200
    assert response.json()["content"] == "Hello from mock LLM"
