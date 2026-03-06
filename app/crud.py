from typing import List, Optional
from app.database import get_connection
from app.schemas import TransactionCreate
import hashlib
from datetime import datetime


PRICE_BW = 2.0
PRICE_COLOR = 5.0
PRICE_PHOTO = 30.0


def compute_total(data: TransactionCreate) -> float:
    return data.pages_bw * PRICE_BW + data.pages_color * PRICE_COLOR + data.photo_pages * PRICE_PHOTO


def compute_hash(data: TransactionCreate, total: float) -> str:
    s = f"{data.customer_name}|{data.pages_bw}|{data.pages_color}|{data.photo_pages}|{total}"
    return hashlib.sha256(s.encode()).hexdigest()


def create_transaction(data: TransactionCreate) -> dict:
    total = compute_total(data)
    txn_hash = compute_hash(data, total)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM transactions WHERE txn_hash = ?", (txn_hash,))
    row = cur.fetchone()
    if row:
        conn.close()
        return dict(row)
    created_at = datetime.utcnow().isoformat()
    cur.execute(
        "INSERT INTO transactions (customer_name, pages_bw, pages_color, photo_pages, total, txn_hash, created_at, cancelled, status) VALUES (?,?,?,?,?,?,?,?,?)",
        (data.customer_name, data.pages_bw, data.pages_color, data.photo_pages, total, txn_hash, created_at, 0, 'pending'),
    )
    conn.commit()
    last_id = cur.lastrowid
    cur.execute("SELECT * FROM transactions WHERE id = ?", (last_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else {}


def list_transactions() -> List[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM transactions WHERE status != 'cancelled' ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_transaction(txn_id: int) -> Optional[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM transactions WHERE id = ? AND status != 'cancelled'", (txn_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None



def cancel_transaction(txn_id: int) -> Optional[dict]:
    """Mark a transaction as cancelled. Returns updated record or None if not found/already cancelled."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM transactions WHERE id = ? AND status != 'cancelled'", (txn_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    cur.execute("UPDATE transactions SET cancelled = 1, status = 'cancelled' WHERE id = ?", (txn_id,))
    conn.commit()
    cur.execute("SELECT * FROM transactions WHERE id = ?", (txn_id,))
    updated = cur.fetchone()
    conn.close()
    return dict(updated) if updated else None


def update_transaction(txn_id: int, data) -> Optional[dict]:
    """Update transaction fields. Recompute total/hash if pages or customer_name change."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM transactions WHERE id = ? AND status != 'cancelled'", (txn_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None

    # current values
    current = dict(row)
    new_customer = data.customer_name if getattr(data, "customer_name", None) is not None else current["customer_name"]
    new_bw = data.pages_bw if getattr(data, "pages_bw", None) is not None else current["pages_bw"]
    new_color = data.pages_color if getattr(data, "pages_color", None) is not None else current["pages_color"]
    new_photo = data.photo_pages if getattr(data, "photo_pages", None) is not None else current["photo_pages"]
    new_status = data.status if getattr(data, "status", None) is not None else current.get("status", "pending")

    # recompute total and hash if pages or customer changed
    total = new_bw * PRICE_BW + new_color * PRICE_COLOR + new_photo * PRICE_PHOTO
    txn_hash = compute_hash(TransactionCreate(customer_name=new_customer, pages_bw=new_bw, pages_color=new_color, photo_pages=new_photo), total)

    cur.execute(
        "UPDATE transactions SET customer_name = ?, pages_bw = ?, pages_color = ?, photo_pages = ?, total = ?, txn_hash = ?, status = ? WHERE id = ?",
        (new_customer, new_bw, new_color, new_photo, total, txn_hash, new_status, txn_id),
    )
    conn.commit()
    cur.execute("SELECT * FROM transactions WHERE id = ?", (txn_id,))
    updated = cur.fetchone()
    conn.close()
    return dict(updated) if updated else None


def total_income() -> dict:
    """Return total income and transaction count."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as count, COALESCE(SUM(total), 0) as total FROM transactions WHERE status != 'cancelled'")
    row = cur.fetchone()
    conn.close()
    # sqlite returns numbers; ensure types are python native
    return {"count": int(row["count"]), "total_income": float(row["total"])}
