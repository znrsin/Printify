from pathlib import Path
import sqlite3

DB_FILE = Path(__file__).parent.parent / "database.db"


def get_connection():
	DB_FILE.parent.mkdir(parents=True, exist_ok=True)
	conn = sqlite3.connect(DB_FILE)
	conn.row_factory = sqlite3.Row
	return conn


def init_db():
	conn = get_connection()
	cur = conn.cursor()
	cur.execute(
		"""
	CREATE TABLE IF NOT EXISTS transactions (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		customer_name TEXT NOT NULL,
		pages_bw INTEGER DEFAULT 0,
		pages_color INTEGER DEFAULT 0,
		photo_pages INTEGER DEFAULT 0,
		total REAL NOT NULL,
		txn_hash TEXT UNIQUE NOT NULL,
		created_at TEXT NOT NULL,
		cancelled INTEGER DEFAULT 0
	)
	"""
	)
	# Ensure `cancelled` and `status` columns exist for older DBs
	conn.commit()
	cur.execute("PRAGMA table_info(transactions)")
	cols = [row[1] for row in cur.fetchall()]
	if "cancelled" not in cols:
		cur.execute("ALTER TABLE transactions ADD COLUMN cancelled INTEGER DEFAULT 0")
		conn.commit()
	# Add status column and migrate from cancelled if needed
	if "status" not in cols:
		cur.execute("ALTER TABLE transactions ADD COLUMN status TEXT DEFAULT 'pending'")
		# if cancelled column exists, mark those rows as cancelled in new status column
		if "cancelled" in cols:
			cur.execute("UPDATE transactions SET status = 'cancelled' WHERE cancelled = 1")
		conn.commit()
	conn.close()
