# Printing Management System (FastAPI)

Minimal FastAPI backend for the Printing Management System (conceptual prototype).

Quick start

1. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Run the app with uvicorn:

```bash
uvicorn main:app --reload
```

3. Open docs in your browser: http://127.0.0.1:8000/docs

Endpoints

- `POST /transactions/` — create transaction (total computed automatically)
- `GET /transactions/` — list transactions (excludes cancelled)
- `GET /transactions/{id}` — get a transaction (if not cancelled)
- `PUT /transactions/{id}` — update transaction fields or `status` (`pending`, `completed`, `cancelled`)
- `POST /transactions/{id}/cancel` — client cancels their order (marks as cancelled)
- `GET /transactions/prices` — view price list
- `GET /transactions/summary` — total income and transaction count (excludes cancelled)

Notes

- There is no physical delete. Records are archived/cancelled via the `status` field (value: `cancelled`).
- Updating pages or customer name will recompute the `total` and `txn_hash`.

Examples

```bash
# cancel transaction with id 3
curl -X POST http://127.0.0.1:8000/transactions/3/cancel

# update transaction status or pages
curl -X PUT http://127.0.0.1:8000/transactions/3 -H "Content-Type: application/json" -d '{"status":"completed"}'

# check total income
curl http://127.0.0.1:8000/transactions/summary
```

Sample response

```json
[
	{
		"customer_name": "FRANZIN",
		"pages_bw": 0,
		"pages_color": 0,
		"photo_pages": 5,
		"id": 5,
		"total": 150,
		"created_at": "2026-03-06T14:48:51.022064",
		"status": "pending"
	},
	{
		"customer_name": "Frank Joseph",
		"pages_bw": 0,
		"pages_color": 0,
		"photo_pages": 4,
		"id": 3,
		"total": 120,
		"created_at": "2026-03-06T14:17:54.840849",
		"status": "completed"
	}
]
```

Status values

- `pending`: order received, not yet completed or cancelled
- `completed`: order finished and paid
- `cancelled`: order was cancelled (archived; excluded from summaries)

Terminology

- `txn_id` / `id`: internal transaction identifier
- `txn_hash`: internal fingerprint used to avoid duplicate identical transactions

Files

- [main.py](main.py) - app entrypoint
- [app/database.py](app/database.py) - SQLite helper + migrations
- [app/crud.py](app/crud.py) - CRUD helpers
- [app/schemas.py](app/schemas.py) - Pydantic schemas
- [app/routers/transactions.py](app/routers/transactions.py) - transactions endpoints
- [requirements.txt](requirements.txt)
