import os
os.environ["DATABASE_URL"] = "sqlite:///./test_incidents.db"
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

def test_incident_lifecycle():
    r = client.post("/alerts", json={"alert_name":"CPUHigh","severity":"warning","summary":"CPU utilization above 90 percent"})
    assert r.status_code == 201
    iid = r.json()["id"]
    a = client.post(f"/incidents/{iid}/analyze", json={"include_ai":False})
    assert a.status_code == 200
    assert "recommended_actions" in a.json()
    d = client.post(f"/incidents/{iid}/approval", json={"decision":"approved","note":"Reviewed by operator"}, headers={"x-actor":"tester"})
    assert d.status_code == 200
    assert "No remediation was executed" in d.json()["message"]
    assert client.get(f"/incidents/{iid}/audit").json()[0]["actor"] == "tester"
