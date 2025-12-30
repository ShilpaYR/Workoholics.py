def test_rag_valid_policy_query(rag_client):
    response = rag_client.post("/query", json={
        "query": "What is the work from home policy?"
    })
    assert response.status_code == 200
    assert "answer" in response.json()


def test_rag_out_of_scope_query(rag_client):
    response = rag_client.post("/query", json={
        "query": "What is the cafeteria menu?"
    })
    assert response.status_code == 200
    assert "not available" in response.json()["answer"].lower()


def test_rag_retrieval_chunks(rag_client):
    response = rag_client.post("/query", json={
        "query": "Leave policy details"
    })
    assert response.status_code == 200
    assert "sources" in response.json()


def test_rag_no_hallucination(rag_client):
    response = rag_client.post("/query", json={
        "query": "Tell me the CEO phone number"
    })
    assert "not available" in response.json()["answer"].lower()
