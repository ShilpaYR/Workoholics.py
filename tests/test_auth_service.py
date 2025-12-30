def test_employee_login_valid(auth_client):
    response = auth_client.post("/login", json={
        "email": "employee@test.com",
        "password": "correct_password"
    })
    assert response.status_code == 200
    assert "totp_required" in response.json()


def test_employee_login_invalid_password(auth_client):
    response = auth_client.post("/login", json={
        "email": "employee@test.com",
        "password": "wrong_password"
    })
    assert response.status_code == 401


def test_totp_verification_valid(auth_client):
    response = auth_client.post("/verify-totp", json={
        "email": "employee@test.com",
        "code": "123456"
    })
    assert response.status_code == 200
    assert "token" in response.json()


def test_totp_verification_invalid(auth_client):
    response = auth_client.post("/verify-totp", json={
        "email": "employee@test.com",
        "code": "000000"
    })
    assert response.status_code == 401
