import pytest


VALID_REPAIR = {
    "ticket": "REP-032", "problem": " Chain slip ", "received_on": "2026-05-03",
    "serial_code": "BC-001",
}


def test_api_lists_and_searches(api_client, api_repair):
    response = api_client.get("/api/repairs")
    assert response.status_code == 200
    assert response.json == [{
        "ticket": "REP-031", "problem": "Brake noise", "state": "queued",
        "received_on": "2026-05-02", "services": ["brake-clean"],
    }]
    assert api_client.get("/api/repairs", query_string={"q": " brake "}).json == response.json
    assert api_client.get("/api/repairs", query_string={"q": "%"}).json == []


def test_api_creates_from_json(api_client, api_repair):
    response = api_client.post("/api/repairs", json=VALID_REPAIR)
    assert response.status_code == 201
    assert response.json["problem"] == "Chain slip"
    assert response.json in api_client.get("/api/repairs").json


@pytest.mark.parametrize(("data", "status"), [
    ([], 400),
    ({**VALID_REPAIR, "problem": ""}, 400),
    ({**VALID_REPAIR, "received_on": "2026-02-31"}, 400),
    ({**VALID_REPAIR, "received_on": "20260503"}, 400),
    ({**VALID_REPAIR, "serial_code": "MISSING"}, 404),
])
def test_api_rejects_invalid_repair(api_client, api_repair, data, status):
    response = api_client.post("/api/repairs", json=data)
    assert response.status_code == status
    assert response.json["error"]


def test_api_rejects_duplicate_ticket(api_client, api_repair):
    payload = {**VALID_REPAIR, "ticket": "REP-031"}
    assert api_client.post("/api/repairs", json=payload).status_code == 409
    assert len(api_client.get("/api/repairs").json) == 1
