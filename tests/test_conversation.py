def test_create_conversation(client):
    response = client.post(
        "/conversations",
        json={"user_email": "test@example.com", "mode": "open"}
    )
    assert response.status_code == 200
    assert "id" in response.json()
