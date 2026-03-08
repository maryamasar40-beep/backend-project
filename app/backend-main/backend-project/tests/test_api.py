import os
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db import Base, get_db
from app.main import app

TEST_DB_PATH = Path("test_phishing.db")
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    if TEST_DB_PATH.exists():
        os.remove(TEST_DB_PATH)

    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    test_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with test_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    if TEST_DB_PATH.exists():
        os.remove(TEST_DB_PATH)


@pytest.fixture
async def auth_headers(client: AsyncClient):
    register_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "qa@example.com", "password": "StrongPass123"},
    )
    assert register_resp.status_code in {201, 409}

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "qa@example.com", "password": "StrongPass123"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.anyio
async def test_scan_and_hash_check(client: AsyncClient, auth_headers: dict[str, str]):
    payload = {
        "url": "https://example.com/login",
        "domain": "example.com",
        "screenshot_hash": "0f0f",
    }
    create_resp = await client.post("/api/v1/scan", json=payload, headers=auth_headers)
    assert create_resp.status_code == 200
    scan_id = create_resp.json()["id"]

    get_resp = await client.get(f"/api/v1/scan/{scan_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["domain"] == "example.com"

    hash_resp = await client.post(
        "/api/v1/hash-check",
        json={"screenshot_hash": "0f0f", "max_distance": 4},
    )
    assert hash_resp.status_code == 200
    assert hash_resp.json()["exact_match"] is True


@pytest.mark.anyio
async def test_whitelist_flow(client: AsyncClient):
    check_resp = await client.get("/api/v1/whitelist/check", params={"domain": "trusted.com"})
    assert check_resp.status_code == 200
    assert check_resp.json()["whitelisted"] is False

    login_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "wl@example.com", "password": "StrongPass123"},
    )
    assert login_resp.status_code == 201
    token_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "wl@example.com", "password": "StrongPass123"},
    )
    headers = {"Authorization": f"Bearer {token_resp.json()['access_token']}"}

    create_resp = await client.post(
        "/api/v1/whitelist",
        json={"domain": "trusted.com", "logo_hash": "abcd"},
        headers=headers,
    )
    assert create_resp.status_code == 200

    check_resp_2 = await client.get("/api/v1/whitelist/check", params={"domain": "trusted.com"})
    assert check_resp_2.status_code == 200
    assert check_resp_2.json()["whitelisted"] is True


@pytest.mark.anyio
async def test_result_requires_existing_scan(client: AsyncClient, auth_headers: dict[str, str]):
    resp = await client.post(
        "/api/v1/result",
        json={"scan_id": 9999, "risk_score": 0.8, "classification": "phishing"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_health_endpoint(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] in {"ok", "degraded"}


@pytest.mark.anyio
async def test_result_and_feedback_flow(client: AsyncClient, auth_headers: dict[str, str]):
    scan_payload = {
        "url": "https://example.org",
        "domain": "example.org",
        "screenshot_hash": "aaaa",
    }
    scan_resp = await client.post("/api/v1/scan", json=scan_payload, headers=auth_headers)
    assert scan_resp.status_code == 200
    scan_id = scan_resp.json()["id"]

    result_resp = await client.post(
        "/api/v1/result",
        json={"scan_id": scan_id, "risk_score": 0.3, "classification": "safe"},
        headers=auth_headers,
    )
    assert result_resp.status_code == 200
    result_id = result_resp.json()["id"]

    fetch_result = await client.get(f"/api/v1/result/{result_id}")
    assert fetch_result.status_code == 200
    assert fetch_result.json()["scan_id"] == scan_id

    feedback_resp = await client.post(
        "/api/v1/feedback",
        json={"result_id": result_id, "user_verdict": "correct", "comment": "looks good"},
        headers=auth_headers,
    )
    assert feedback_resp.status_code == 200

    feedback_list_resp = await client.get(f"/api/v1/feedback/result/{result_id}")
    assert feedback_list_resp.status_code == 200
    assert len(feedback_list_resp.json()["feedbacks"]) == 1


@pytest.mark.anyio
async def test_auth_me_endpoint(client: AsyncClient, auth_headers: dict[str, str]):
    me_resp = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "qa@example.com"
    assert me_resp.json()["role"] == "admin"


@pytest.mark.anyio
async def test_brands_crud(client: AsyncClient, auth_headers: dict[str, str]):
    create_resp = await client.post(
        "/api/v1/brand",
        json={"name": "Example Brand", "domains": ["example.com"]},
        headers=auth_headers,
    )
    assert create_resp.status_code == 201
    brand_id = create_resp.json()["id"]

    list_resp = await client.get("/api/v1/brands")
    assert list_resp.status_code == 200
    assert len(list_resp.json()["brands"]) == 1

    update_resp = await client.put(
        f"/api/v1/brand/{brand_id}",
        json={"domains": ["example.com", "example.org"]},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200
    assert "example.org" in update_resp.json()["domains"]

    analyst_register = await client.post(
        "/api/v1/auth/register",
        json={"email": "analyst@example.com", "password": "StrongPass123"},
    )
    assert analyst_register.status_code == 201
    assert analyst_register.json()["role"] == "analyst"

    analyst_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@example.com", "password": "StrongPass123"},
    )
    analyst_headers = {"Authorization": f"Bearer {analyst_login.json()['access_token']}"}

    forbidden_create = await client.post(
        "/api/v1/brand",
        json={"name": "Forbidden Brand", "domains": ["forbidden.com"]},
        headers=analyst_headers,
    )
    assert forbidden_create.status_code == 403
