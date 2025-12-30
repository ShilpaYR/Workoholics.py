def test_unauthorized_hr_access(hr_client):
    response = hr_client.get("/jobs")
    assert response.status_code == 401


def test_expired_token(auth_client):
    response = auth_client.get("/protected", headers={
        "Authorization": "Bearer expired_token"
    })
    assert response.status_code == 401


def test_rag_response_time(rag_client):
    import time
    start = time.time()
    rag_client.post("/query", json={"query": "Leave policy"})
    assert time.time() - start < 3
