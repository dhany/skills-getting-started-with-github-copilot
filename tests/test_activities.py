from fastapi.testclient import TestClient
import copy
import pytest

from src.app import app, activities as activities_store

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities dict to a pristine state for each test."""
    original = {
        name: {**details, "participants": list(details["participants"])}
        for name, details in activities_store.items()
    }
    backup = copy.deepcopy(original)
    try:
        yield
    finally:
        activities_store.clear()
        activities_store.update(backup)


def test_get_activities_returns_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_adds_participant():
    email = "pytest.user@example.com"
    # ensure not present
    if email in activities_store["Chess Club"]["participants"]:
        activities_store["Chess Club"]["participants"].remove(email)

    r = client.post(f"/activities/Chess Club/signup?email={email}")
    assert r.status_code == 200
    assert "Signed up" in r.json().get("message", "")

    # verify in store
    assert email in activities_store["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    email = activities_store["Chess Club"]["participants"][0]
    r = client.post(f"/activities/Chess Club/signup?email={email}")
    assert r.status_code == 400


def test_unregister_removes_participant():
    email = "to.remove@example.com"
    activities_store["Chess Club"]["participants"].append(email)

    r = client.delete(f"/activities/Chess Club/signup?email={email}")
    assert r.status_code == 200
    assert "Unregistered" in r.json().get("message", "")
    assert email not in activities_store["Chess Club"]["participants"]


def test_unregister_nonexistent_returns_400():
    email = "nonexistent@example.com"
    # ensure not present
    if email in activities_store["Chess Club"]["participants"]:
        activities_store["Chess Club"]["participants"].remove(email)

    r = client.delete(f"/activities/Chess Club/signup?email={email}")
    assert r.status_code == 400
