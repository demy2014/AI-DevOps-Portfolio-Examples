import os
os.environ["DATABASE_URL"]="sqlite:///./test_leads.db"
from fastapi.testclient import TestClient
from backend.main import app
client=TestClient(app)

def test_lead_scoring_review_and_report():
    r=client.post('/leads',json={'company':'Example Systems','email':'sales@example.org','industry':'IT services','website':'https://example.org','employee_count':100,'contact_name':'Alex','notes':'Provides managed cloud and infrastructure services.'})
    assert r.status_code==201
    item=r.json();assert item['priority']=='high' and item['score']==100
    review=client.post(f"/leads/{item['id']}/review",json={'status':'qualified','reviewer_note':'Demo review'})
    assert review.status_code==200 and 'No email' in review.json()['message']
    assert client.get('/reports/summary').json()['qualified']>=1

def test_invalid_email_rejected():
    r=client.post('/leads',json={'company':'Invalid Co','email':'not-an-email'})
    assert r.status_code==422
