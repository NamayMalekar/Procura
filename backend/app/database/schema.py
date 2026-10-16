"""Table definitions (SQLite). Think of this as the data model of the whole system."""

TABLES = ["agent_runs", "audit_log", "escalations", "purchase_orders", "budgets", "supplier_items",
          "promotions", "demand", "inventory", "suppliers", "products", "nodes", "meta"]

DDL = """
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS nodes (id TEXT PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS products (sku TEXT PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL,
  primary_supplier TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS suppliers (id TEXT PRIMARY KEY, name TEXT NOT NULL, reliability REAL NOT NULL);
CREATE TABLE IF NOT EXISTS inventory (sku TEXT NOT NULL REFERENCES products(sku), node TEXT NOT NULL REFERENCES nodes(id),
  on_hand INTEGER NOT NULL, safety_stock INTEGER NOT NULL, storage_capacity INTEGER NOT NULL, PRIMARY KEY (sku, node));
CREATE TABLE IF NOT EXISTS demand (sku TEXT NOT NULL, node TEXT NOT NULL, forecast_daily INTEGER NOT NULL,
  sales_json TEXT NOT NULL, PRIMARY KEY (sku, node));
CREATE TABLE IF NOT EXISTS promotions (id INTEGER PRIMARY KEY AUTOINCREMENT, sku TEXT NOT NULL, name TEXT NOT NULL,
  uplift REAL NOT NULL);
CREATE TABLE IF NOT EXISTS supplier_items (supplier_id TEXT NOT NULL REFERENCES suppliers(id),
  sku TEXT NOT NULL REFERENCES products(sku), unit_price REAL NOT NULL, lead_time_days INTEGER NOT NULL,
  moq INTEGER NOT NULL, pack_size INTEGER NOT NULL, available_qty INTEGER NOT NULL, inject TEXT,
  PRIMARY KEY (supplier_id, sku));
CREATE TABLE IF NOT EXISTS budgets (category TEXT PRIMARY KEY, total REAL NOT NULL, remaining REAL NOT NULL);
CREATE TABLE IF NOT EXISTS purchase_orders (id TEXT PRIMARY KEY, sku TEXT NOT NULL, node TEXT NOT NULL,
  supplier_id TEXT NOT NULL, qty INTEGER NOT NULL, unit_price REAL NOT NULL, status TEXT NOT NULL,
  supplier_confirmed_qty INTEGER, eta_days INTEGER, created_by TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS escalations (id TEXT PRIMARY KEY, run_id TEXT, sku TEXT, node TEXT, reason TEXT,
  follow_up TEXT);
CREATE TABLE IF NOT EXISTS audit_log (id INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL, payload TEXT);
CREATE TABLE IF NOT EXISTS agent_runs (run_id TEXT PRIMARY KEY, case_id TEXT, status TEXT, payload TEXT NOT NULL,
  seq INTEGER);
"""


def create_all(conn):
    conn.executescript(DDL)
    conn.commit()


def drop_all(conn):
    for t in TABLES:
        conn.execute(f"DROP TABLE IF EXISTS {t}")
    conn.commit()
