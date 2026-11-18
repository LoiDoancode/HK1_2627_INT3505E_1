import pytest
from app import create_app


@pytest.fixture()
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_v1_returns_full_name_schema(client):
    res = client.get("/api/v1/users/1")
    assert res.status_code == 200
    assert res.get_json() == {
        "id": 1,
        "full_name": "Doãn Lợi",
        "email": "Doan.Loi@example.com",
    }


def test_v2_returns_split_name_schema(client):
    res = client.get("/api/v2/users/1")
    assert res.status_code == 200
    assert res.get_json() == {
        "id": 1,
        "first_name": "Doãn",
        "last_name": "Lợi",
        "email": "Doan.Loi@example.com",
    }


def test_not_found_both_versions(client):
    for path in ("/api/v1/users/999", "/api/v2/users/999"):
        res = client.get(path)
        assert res.status_code == 404
        assert res.get_json() == {"error": "nf"}
