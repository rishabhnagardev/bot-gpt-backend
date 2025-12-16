def test_create_conversation(client):
    response = client.post(
        "/conversations",
        json={"mode": "open"}
    )
    assert response.status_code == 200
    assert "id" in response.json()
