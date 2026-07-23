from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_home_page() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Career Mentor Agent" in response.text


def test_post_career_form_valid() -> None:
    response = client.post(
        "/career",
        data={
            "skills": "Python, HTML, CSS",
            "interests": "Machine Learning",
            "goal": "Become an ML Engineer"
        }
    )
    assert response.status_code == 200
    assert "Your Career Guidance Roadmap" in response.text


def test_post_career_form_invalid() -> None:
    response = client.post(
        "/career",
        data={
            "skills": "",
            "interests": "",
            "goal": ""
        }
    )
    assert response.status_code == 422
    assert "Invalid Input Details" in response.text


def test_post_career_json_api_discriminated_union() -> None:
    response = client.post(
        "/api/v1/career",
        json={
            "skills": "Python, HTML, CSS",
            "interests": "AI Solutions",
            "goal": "Targeting AI Solution Architect"
        }
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["type"] == "success"
    assert "data" in json_data
    assert "career_paths" in json_data["data"]
