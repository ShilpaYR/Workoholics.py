def test_validation_agent(applicant_client):
    response = applicant_client.post("/apply", json={
        "job_id": "",
        "resume": ""
    })
    assert response.status_code == 400


def test_enrichment_agent(applicant_client):
    response = applicant_client.post("/apply", json={
        "job_id": 1,
        "resume": "resume.pdf"
    })
    assert "skills" in response.json()


def test_deduplication_agent(applicant_client):
    response = applicant_client.post("/apply", json={
        "job_id": 1,
        "resume": "duplicate_resume.pdf"
    })
    assert "duplicate" in response.json()["status"].lower()


def test_routing_agent(applicant_client):
    response = applicant_client.post("/apply", json={
        "job_id": 1,
        "resume": "backend_resume.pdf"
    })
    assert response.json()["status"] == "routed"
