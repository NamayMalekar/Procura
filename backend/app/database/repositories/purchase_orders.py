from app.commons.enums import POStatus
from ._base import Repo


class PurchaseOrderRepo(Repo):
    def get(self, po_id):
        r = self.one("SELECT * FROM purchase_orders WHERE id=?", (po_id,))
        if not r:
            raise KeyError(po_id)
        return r

    def find(self, po_id):
        return self.one("SELECT * FROM purchase_orders WHERE id=?", (po_id,))

    def all(self):
        return self.many("SELECT * FROM purchase_orders ORDER BY rowid")

    def open_for(self, sku, node):
        marks = ",".join("?" * len(POStatus.OPEN))
        return self.many(f"SELECT * FROM purchase_orders WHERE sku=? AND node=? AND status IN ({marks}) ORDER BY rowid",
                         (sku, node, *POStatus.OPEN))

    def insert(self, po):
        cols = ", ".join(po)
        self.run(f"INSERT INTO purchase_orders ({cols}) VALUES ({','.join('?' * len(po))})", tuple(po.values()))

    def update(self, po_id, **fields):
        cols = ", ".join(f"{k}=?" for k in fields)
        self.run(f"UPDATE purchase_orders SET {cols} WHERE id=?", (*fields.values(), po_id))

    def next_id(self):
        n = int(self.one("SELECT value FROM meta WHERE key='next_po'")["value"])
        self.run("UPDATE meta SET value=? WHERE key='next_po'", (str(n + 1),))
        return f"PO-{n}"
