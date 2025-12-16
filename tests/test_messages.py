from app.services import llm_service


def test_send_message_open_mode(client, monkeypatch):
    def mock_llm(*args, **kwargs):
        return "Hello from mock LLM"

    monkeypatch.setattr(
        llm_service,
        "call_llm",
        mock_llm
    )

    # create conversation
    conv = client.post(
        "/conversations",
        json={"mode": "open"}
    ).json()

    # send message
    response = client.post(
        f"/conversations/{conv['id']}/messages",
        data={"content": "Hi"}
    )

    assert response.status_code == 200
    assert response.json()["content"] == "Hello from mock LLM"
