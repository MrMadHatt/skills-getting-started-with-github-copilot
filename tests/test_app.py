import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


@pytest.fixture()
def client():
    return TestClient(app)


def test_get_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow(client):
    email = "alex@mergington.edu"
    activity = "Basketball Team"

    signup_response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email},
    )

    assert signup_response.status_code == 200
    assert email in activities[activity]["participants"]

    unregister_response = client.delete(
        f"/activities/{activity}/participants",
        params={"email": email},
    )

    assert unregister_response.status_code == 200
    assert email not in activities[activity]["participants"]


def test_duplicate_signup_rejected(client):
    email = "emma@mergington.edu"
    activity = "Programming Class"

    first_response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email},
    )

    assert first_response.status_code == 400
    assert first_response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_missing_participant_returns_404(client):
    email = "missing@mergington.edu"
    activity = "Tennis Club"

    response = client.delete(
        f"/activities/{activity}/participants",
        params={"email": email},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not registered for this activity"
