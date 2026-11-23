import os

os.environ["DATABASE_URL"] = "sqlite:///./test_data_gather.db"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.mark.parametrize(
    ("path", "value", "unit", "bad_value"),
    [
        ("/api/temperatures", 25.5, "℃", -300),
        ("/api/humidities", 60.0, "%RH", 120),
        ("/api/pressures", 101.3, "kPa", -1),
    ],
)
def test_save_and_query(client, path, value, unit, bad_value):
    r = client.post(path, json={"device_id": "dev-1", "value": value,
                                "collected_at": "2026-11-24T10:00:00"})
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["value"] == value and body["unit"] == unit
    client.post(path, json={"device_id": "dev-2", "value": value,
                            "collected_at": "2026-11-24T12:00:00"})

    assert client.get(f"{path}/{body['id']}").json()["id"] == body["id"]
    assert client.get(f"{path}/9999").status_code == 404

    assert client.get(path).json()["total"] == 2
    assert client.get(path, params={"device_id": "dev-1"}).json()["total"] == 1
    assert client.get(path, params={"start": "2026-11-24T11:00:00"}).json()["total"] == 1

    assert client.post(path, json={"device_id": "d", "value": bad_value}).status_code == 422
