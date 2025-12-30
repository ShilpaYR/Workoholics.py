import pytest

class MockResponse:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json_data = json_data or {}

    def json(self):
        return self._json_data

class MockClient:
    # def get(self, url, headers=None):
    #     headers = headers or {}
    #     # OAuth callback
    #     if url.startswith("/oauth/callback"):
    #         return MockResponse(200, {"token": "dummy_token"})
    #     # Unauthorized or expired token
    #     if "expired_token" in (headers or {}).get("Authorization", ""):
    #         return MockResponse(401)
    #     if url == "/jobs" and headers.get("Authorization") is None:
    #         return MockResponse(401)
    #     # Applicant requests: list of jobs
    #     if url == "/jobs" and isinstance(self, MockClient):
    #         return MockResponse(200, {"jobs": ["Software Engineer", "Data Scientist"]})

    #     # HR: list of applicants
    #     if url.endswith("/applications"):
    #         return MockResponse(200, [{"name": "Alice"}, {"name": "Bob"}])        
    #     # Applicant: list of jobs
    #     if url == "/jobs":
    #         return MockResponse(200, {"jobs": ["Software Engineer", "Data Scientist"]})
    #     # HR: list of applicants
    #     if url.endswith("/applications"):
    #         return MockResponse(200, [{"name": "Alice"}, {"name": "Bob"}])
    #     return MockResponse(200)
    
    def get(self, url, headers=None):
        headers = headers or {}

        # OAuth callback
        if url.startswith("/oauth/callback"):
            return MockResponse(200, {"token": "dummy_token"})
        
        # Unauthorized HR access
        if url == "/jobs" and headers.get("Authorization") is None:
            return MockResponse(401)

        # Applicant requests: list of jobs
        if url == "/jobs" and isinstance(self, MockClient):
            return MockResponse(200, {"jobs": ["Software Engineer", "Data Scientist"]})

        # HR: list of applicants
        if url.endswith("/applications"):
            return MockResponse(200, [{"name": "Alice"}, {"name": "Bob"}])

        # Expired token
        if "expired_token" in headers.get("Authorization", ""):
            return MockResponse(401)

        return MockResponse(200)


    def post(self, url, json=None, headers=None):
        json = json or {}
        if url == "/apply":
            if not json.get("job_id") or not json.get("resume"):
                return MockResponse(400)
            if json.get("resume", "").endswith(".exe"):
                return MockResponse(400)
            if "duplicate" in json.get("resume", ""):
                return MockResponse(200, {"status": "duplicate"})
            if "backend" in json.get("resume", ""):
                return MockResponse(200, {"status": "routed"})
            return MockResponse(201, {"status": "submitted", "skills": ["Python"]})
        if url == "/login":
            if json.get("password") != "correct_password":
                return MockResponse(401)
            return MockResponse(200, {"totp_required": True})
        if url == "/verify-totp":
            if json.get("code") != "123456":
                return MockResponse(401)
            return MockResponse(200, {"token": "jwt_token"})
        if url == "/query":
            query = json.get("query", "").lower()
            if "cafeteria" in query or "ceo phone" in query:
                return MockResponse(200, {"answer": "Not available"})
            return MockResponse(200, {"answer": "Policy response", "sources": ["doc.pdf"]})
        if url == "/jobs":
            return MockResponse(201, {"job_id": 1, "status": "created"})
        return MockResponse(200)

    def put(self, url, json=None, headers=None):
        return MockResponse(200, {"message": "Updated"})

    def delete(self, url, headers=None):
        return MockResponse(200, {"message": "Deleted"})

@pytest.fixture
def applicant_client():
    return MockClient()

@pytest.fixture
def auth_client():
    return MockClient()

@pytest.fixture
def hr_client():
    return MockClient()

@pytest.fixture
def rag_client():
    return MockClient()
