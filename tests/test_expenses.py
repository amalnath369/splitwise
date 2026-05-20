from __future__ import annotations
import pytest
from httpx import AsyncClient


async def _register_and_login(client: AsyncClient, email: str, password: str = "Test@1234") -> str:
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    response = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return response.json()["access_token"]


async def _get_user_id(client: AsyncClient, token: str, email: str) -> str:
    """Helper to get user id via register response."""
    resp = await client.post("/api/v1/auth/register", json={"email": email, "password": "Test@1234"})
    if resp.status_code == 201:
        return resp.json()["id"]
    login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": "Test@1234"})
    token = login_resp.json()["access_token"]
    return token


@pytest.mark.asyncio
async def test_balance_with_three_users_two_expenses(client: AsyncClient):
    """
    A pays 90 split equally between A, B, C -> A=+60, B=-30, C=-30
    B pays 30 split equally between B, C    -> B=+15, C=-15
    Final: A=+60, B=-15, C=-45
    """
    reg_a = await client.post("/api/v1/auth/register", json={"email": "a@test.com", "password": "Test@1234"})
    reg_b = await client.post("/api/v1/auth/register", json={"email": "b@test.com", "password": "Test@1234"})
    reg_c = await client.post("/api/v1/auth/register", json={"email": "c@test.com", "password": "Test@1234"})

    id_a = reg_a.json()["id"]
    id_b = reg_b.json()["id"]
    id_c = reg_c.json()["id"]

    token_a = (await client.post("/api/v1/auth/login", json={"email": "a@test.com", "password": "Test@1234"})).json()["access_token"]
    token_b = (await client.post("/api/v1/auth/login", json={"email": "b@test.com", "password": "Test@1234"})).json()["access_token"]

    group_resp = await client.post(
        "/api/v1/groups",
        json={"name": "Balance Test Group"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    group_id = group_resp.json()["id"]

    await client.post(f"/api/v1/groups/{group_id}/members", json={"email": "b@test.com"}, headers={"Authorization": f"Bearer {token_a}"})
    await client.post(f"/api/v1/groups/{group_id}/members", json={"email": "c@test.com"}, headers={"Authorization": f"Bearer {token_a}"})

    await client.post(
        f"/api/v1/groups/{group_id}/expenses",
        json={
            "paid_by": id_a,
            "amount": "90.00",
            "description": "Dinner",
            "split_type": "equal",
            "split_between": [id_a, id_b, id_c],
        },
        headers={"Authorization": f"Bearer {token_a}"},
    )

    await client.post(
        f"/api/v1/groups/{group_id}/expenses",
        json={
            "paid_by": id_b,
            "amount": "30.00",
            "description": "Cab",
            "split_type": "equal",
            "split_between": [id_b, id_c],
        },
        headers={"Authorization": f"Bearer {token_b}"},
    )

    response = await client.get(
        f"/api/v1/groups/{group_id}/balances",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert response.status_code == 200
    balances = {item["user_id"]: float(item["balance"]) for item in response.json()}

    assert balances[id_a] == pytest.approx(60.0)
    assert balances[id_b] == pytest.approx(-15.0)
    assert balances[id_c] == pytest.approx(-45.0)


@pytest.mark.asyncio
async def test_soft_delete_recomputes_balance(client: AsyncClient):
    reg_a = await client.post("/api/v1/auth/register", json={"email": "del_a@test.com", "password": "Test@1234"})
    reg_b = await client.post("/api/v1/auth/register", json={"email": "del_b@test.com", "password": "Test@1234"})
    id_a = reg_a.json()["id"]
    id_b = reg_b.json()["id"]

    token_a = (await client.post("/api/v1/auth/login", json={"email": "del_a@test.com", "password": "Test@1234"})).json()["access_token"]

    group_resp = await client.post(
        "/api/v1/groups",
        json={"name": "Delete Test Group"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    group_id = group_resp.json()["id"]
    await client.post(f"/api/v1/groups/{group_id}/members", json={"email": "del_b@test.com"}, headers={"Authorization": f"Bearer {token_a}"})

    expense_resp = await client.post(
        f"/api/v1/groups/{group_id}/expenses",
        json={
            "paid_by": id_a,
            "amount": "100.00",
            "description": "Test expense",
            "split_type": "equal",
            "split_between": [id_a, id_b],
        },
        headers={"Authorization": f"Bearer {token_a}"},
    )
    expense_id = expense_resp.json()["id"]

    balances_before = {
        item["user_id"]: float(item["balance"])
        for item in (await client.get(f"/api/v1/groups/{group_id}/balances", headers={"Authorization": f"Bearer {token_a}"})).json()
    }
    assert balances_before[id_a] == pytest.approx(50.0)
    assert balances_before[id_b] == pytest.approx(-50.0)

    await client.delete(f"/api/v1/groups/expenses/{expense_id}", headers={"Authorization": f"Bearer {token_a}"})

    balances_after = {
        item["user_id"]: float(item["balance"])
        for item in (await client.get(f"/api/v1/groups/{group_id}/balances", headers={"Authorization": f"Bearer {token_a}"})).json()
    }
    assert balances_after.get(id_a, 0.0) == pytest.approx(0.0)
    assert balances_after.get(id_b, 0.0) == pytest.approx(0.0)
