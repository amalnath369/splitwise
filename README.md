# Splitwise API

A REST API for splitting expenses between groups of people. Built with FastAPI, async SQLAlchemy, and SQLite.

## Stack

- FastAPI + Pydantic v2
- Async SQLAlchemy + SQLite
- JWT auth (python-jose) + bcrypt (passlib)
- Pytest + httpx for testing

## Getting Started

```bash
# copy env and fill in your secret key
cp .env.example .env

# run with docker
docker-compose up --build

# or locally
pip install -r requirements.txt
uvicorn app.core.main:app --reload
```

API docs at `http://localhost:8000/docs`

## Endpoints

```
POST   /api/v1/auth/register
POST   /api/v1/auth/login

POST   /api/v1/groups
POST   /api/v1/groups/{id}/members
GET    /api/v1/groups/{id}

POST   /api/v1/groups/{id}/expenses
GET    /api/v1/groups/{id}/expenses
DELETE /api/v1/groups/expenses/{id}
GET    /api/v1/groups/{id}/balances
GET    /api/v1/groups/{id}/settlements
```

## Running Tests

```bash
pytest tests/ -v
```

## Notes

- Balances are computed on the fly from expenses, not stored. In production this would move to a Celery + Redis reconciliation job once groups hit scale.
- Settlement uses a greedy algorithm — matches largest debtor against largest creditor each round, giving the minimum number of transactions.
- Money is stored as `NUMERIC` in SQLite and handled as `Decimal` throughout — no floats anywhere.
