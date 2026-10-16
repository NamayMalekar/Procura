"""The Store is the single door to the database. It gathers all repositories behind
simple method names so the agent code reads like plain English."""
from . import schema
from .connection import clone_in_memory, connect
from .repositories.audit import AuditRepo
from .repositories.budgets import BudgetRepo
from .repositories.catalog import CatalogRepo
from .repositories.escalations import EscalationRepo
from .repositories.inventory import InventoryRepo
from .repositories.purchase_orders import PurchaseOrderRepo
from .repositories.runs import RunRepo
from .repositories.supplier_items import SupplierItemRepo
from .seed import seed_all


class Store:
    def __init__(self, conn=None):
        """Store() gives a fresh seeded in-memory database (handy for tests)."""
        if conn is None:
            conn = connect(":memory:")
            schema.create_all(conn)
            seed_all(conn)
        self._bind(conn)

    @classmethod
    def open(cls, path):
        """Open (and seed on first run) a database file."""
        conn = connect(path)
        schema.create_all(conn)
        if not conn.execute("SELECT 1 FROM products LIMIT 1").fetchone():
            seed_all(conn)
        return cls(conn)

    def _bind(self, conn):
        self.conn = conn
        self.catalog, self.stock = CatalogRepo(conn), InventoryRepo(conn)
        self.items, self.budgets = SupplierItemRepo(conn), BudgetRepo(conn)
        self.pos, self.tickets = PurchaseOrderRepo(conn), EscalationRepo(conn)
        self.audit_log, self.runs = AuditRepo(conn), RunRepo(conn)

    def clone(self):
        """A throw-away copy for what-if simulations. Changes never touch the real data."""
        return Store(clone_in_memory(self.conn))

    def reset(self):
        schema.drop_all(self.conn)
        schema.create_all(self.conn)
        seed_all(self.conn)

    # ---- reads -------------------------------------------------------------
    def product(self, sku):
        return self.catalog.product(sku)

    def supplier(self, sid):
        return self.catalog.supplier(sid)

    def inventory(self, sku, node):
        return self.stock.get(sku, node)

    def demand(self, sku, node):
        return self.stock.demand(sku, node)

    def promotions(self, sku):
        return self.stock.promotions(sku)

    def supplier_items(self, sku):
        return self.items.for_sku(sku)

    def supplier_item(self, sid, sku):
        return self.items.get(sid, sku)

    def budget(self, sku):
        return self.budgets.get(self.product(sku)["category"])

    def po(self, po_id):
        return self.pos.get(po_id)

    def find_po(self, po_id):
        return self.pos.find(po_id)

    def all_pos(self):
        return self.pos.all()

    def open_pos(self, sku, node):
        return self.pos.open_for(sku, node)

    @staticmethod
    def po_qty(po):
        """Quantity we will really receive (what the supplier confirmed, else what we ordered)."""
        c = po.get("supplier_confirmed_qty")
        return po["qty"] if c is None else c

    def incoming(self, sku, node):
        return sum(self.po_qty(p) for p in self.open_pos(sku, node))

    def storage_free(self, sku, node):
        return self.inventory(sku, node)["storage_capacity"] - self.inventory(sku, node)["on_hand"] \
            - self.incoming(sku, node)

    # ---- writes ------------------------------------------------------------
    def adjust_budget(self, sku, delta):
        self.budgets.adjust(self.product(sku)["category"], delta)

    def insert_po(self, po):
        self.pos.insert(po)

    def update_po(self, po_id, **fields):
        self.pos.update(po_id, **fields)

    def new_po_id(self):
        return self.pos.next_id()

    def update_supplier_item(self, sid, sku, **fields):
        self.items.update(sid, sku, **fields)

    def log(self, event, **kw):
        self.audit_log.add(event, **kw)

    def add_ticket(self, run_id, sku, node, reason, follow_up):
        return self.tickets.add(run_id, sku, node, reason, follow_up)

    # ---- everything the UI needs in one call -------------------------------------
    def snapshot(self):
        rows = [{"sku": r["sku"], "name": r["name"], "node": r["node"], "on_hand": r["on_hand"],
                 "incoming": self.incoming(r["sku"], r["node"]), "capacity": r["storage_capacity"],
                 "safety_stock": r["safety_stock"]} for r in self.stock.all()]
        return {"inventory": rows, "purchase_orders": self.all_pos(), "budgets": self.budgets.all(),
                "escalations": self.tickets.all(), "audit": self.audit_log.all()}
