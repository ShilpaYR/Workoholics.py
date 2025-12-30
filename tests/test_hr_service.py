def test_create_job(hr_client):
    response = hr_client.post("/jobs", json={
        "title": "Software Engineer",
        "description": "Backend role",
        "location": "Remote"
    })
    assert response.status_code == 201


def test_update_job(hr_client):
    response = hr_client.put("/jobs/1", json={
        "description": "Updated description"
    })
    assert response.status_code == 200


def test_delete_job(hr_client):
    response = hr_client.delete("/jobs/1")
    assert response.status_code == 200


def test_view_applicants(hr_client):
    response = hr_client.get("/jobs/1/applications")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
