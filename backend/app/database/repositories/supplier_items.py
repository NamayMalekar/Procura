import json
from ._base import Repo


def _load(r):
    if r:
        r["inject"] = json.loads(r["inject"]) if r["inject"] else None
    return r


class SupplierItemRepo(Repo):
    """What each supplier sells: price, lead time, MOQ, case size, stock they can ship."""

    def get(self, sid, sku):
        r = _load(self.one("SELECT * FROM supplier_items WHERE supplier_id=? AND sku=?", (sid, sku)))
        if not r:
            raise KeyError(f"{sid} does not sell {sku}")
        return r

    def for_sku(self, sku):
        return [_load(r) for r in self.many("SELECT * FROM supplier_items WHERE sku=? ORDER BY supplier_id", (sku,))]

    def update(self, sid, sku, **fields):
        if "inject" in fields and fields["inject"] is not None:
            fields["inject"] = json.dumps(fields["inject"])
        cols = ", ".join(f"{k}=?" for k in fields)
        self.run(f"UPDATE supplier_items SET {cols} WHERE supplier_id=? AND sku=?", (*fields.values(), sid, sku))
