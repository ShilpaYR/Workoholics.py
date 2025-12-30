def test_google_sso_login(applicant_client):
    response = applicant_client.get("/oauth/callback?code=dummy")
    assert response.status_code in (200, 302)

def test_submit_application(applicant_client):
    response = applicant_client.post("/apply", json={
        "job_id": 1,
        "resume": "resume.pdf"
    })
    assert response.status_code == 201


def test_invalid_resume_format(applicant_client):
    response = applicant_client.post("/apply", json={
        "job_id": 1,
        "resume": "resume.exe"
    })
    assert response.status_code == 400
