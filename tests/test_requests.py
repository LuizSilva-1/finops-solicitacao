import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app import models
from app.services import auth_service
from datetime import date, timedelta

SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture()
def seeded_db():
    db = TestingSessionLocal()
    admin = models.user.User(
        username="admin",
        password_hash=auth_service.hash_password("admin123"),
        role="admin",
        display_name="Administrador",
    )
    user = models.user.User(
        username="user",
        password_hash=auth_service.hash_password("user123"),
        role="user",
        display_name="User",
    )
    db.add_all([admin, user])
    db.commit()
    db.close()
    yield
    # cleanup
    db = TestingSessionLocal()
    db.query(models.request.Request).delete()
    db.query(models.user.User).delete()
    db.commit()
    db.close()


def login(username: str, password: str):
    res = client.post("/api/auth/login", json={"username": username, "password": password})
    assert res.status_code == 200
    return res.json()["access_token"]


def test_admin_cannot_create_request(seeded_db):
    token = login("admin", "admin123")
    payload = {
        "requester": "admin",
        "service_type": "ebs_snapshot",
        "aws_account": "123",
        "region": "sa-east-1",
        "expires_at": "2030-01-01",
    }
    res = client.post("/api/requests", json=payload, headers={"X-Auth-Token": token})
    assert res.status_code == 403


def test_create_and_list_request(seeded_db):
    token = login("user", "user123")
    future_date = (date.today() + timedelta(days=30)).strftime("%Y-%m-%d")
    payload = {
        "service_type": "ebs_snapshot",
        "aws_account": "123",
        "region": "sa-east-1",
        "expires_at": future_date,
        "params": "test",
        "tags": "Owner=user",
    }
    res = client.post("/api/requests", json=payload, headers={"X-Auth-Token": token})
    assert res.status_code == 200
    data = res.json()
    assert data["service_type"] == "ebs_snapshot"
    # list
    res_list = client.get("/api/requests", headers={"X-Auth-Token": token})
    assert res_list.status_code == 200
    body = res_list.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == data["id"]


def test_validation_expires_in_future(seeded_db):
    token = login("user", "user123")
    payload = {
        "service_type": "ebs_snapshot",
        "aws_account": "123",
        "region": "sa-east-1",
        "expires_at": "2000-01-01",
    }
    res = client.post("/api/requests", json=payload, headers={"X-Auth-Token": token})
    assert res.status_code == 400
