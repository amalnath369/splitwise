from __future__ import annotations
import pytest
from httpx import AsyncClient


async def _register_and_login(client: AsyncClient, email: str, password: str = "Test@1234") -> str:
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    response = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_group(client: AsyncClient):
    token = await _register_and_login(client, "group_owner@example.com")
    response = await client.post(
        "/api/v1/groups",
        json={"name": "Trip to Goa", "description": "Beach vacation"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Trip to Goa"
    assert len(data["members"]) == 1


@pytest.mark.asyncio
async def test_get_group_unauthorized(client: AsyncClient):
    owner_token = await _register_and_login(client, "owner2@example.com")
    create_resp = await client.post(
        "/api/v1/groups",
        json={"name": "Private Group"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    group_id = create_resp.json()["id"]

    outsider_token = await _register_and_login(client, "outsider@example.com")
    response = await client.get(
        f"/api/v1/groups/{group_id}",
        headers={"Authorization": f"Bearer {outsider_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_add_member(client: AsyncClient):
    owner_token = await _register_and_login(client, "owner3@example.com")
    await client.post("/api/v1/auth/register", json={"email": "newmember@example.com", "password": "Test@1234"})

    create_resp = await client.post(
        "/api/v1/groups",
        json={"name": "Flatmates"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    group_id = create_resp.json()["id"]

    response = await client.post(
        f"/api/v1/groups/{group_id}/members",
        json={"email": "newmember@example.com"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert response.status_code == 201
    assert len(response.json()["members"]) == 2
