import copy

from fastapi.testclient import TestClient
import pytest

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    backup = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(backup)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success():
    email = "testuser@example.com"
    resp = client.post(f"/activities/Chess Club/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate():
    existing = activities["Chess Club"]["participants"][0]
    resp = client.post(f"/activities/Chess Club/signup", params={"email": existing})
    assert resp.status_code == 400


def test_signup_missing_activity():
    resp = client.post(f"/activities/NoSuchActivity/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404


def test_unregister_success():
    email = "toremove@example.com"
    activities["Chess Club"]["participants"].append(email)
    resp = client.post(f"/activities/Chess Club/unregister", params={"email": email})
    assert resp.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_nonparticipant():
    resp = client.post(f"/activities/Chess Club/unregister", params={"email": "not@there.com"})
    assert resp.status_code == 400
