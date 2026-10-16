import json
from ._base import Repo


class InventoryRepo(Repo):
    """Stock levels, demand history and promotions."""

    def get(self, sku, node):
        r = self.one("SELECT * FROM inventory WHERE sku=? AND node=?", (sku, node))
        if not r:
            raise KeyError(f"no inventory for {sku} at {node}")
        return r

    def all(self):
        return self.many("""SELECT i.*, p.name FROM inventory i JOIN products p ON p.sku=i.sku
                            ORDER BY i.sku, i.node""")

    def demand(self, sku, node):
        r = self.one("SELECT * FROM demand WHERE sku=? AND node=?", (sku, node))
        if not r:
            raise KeyError(f"no demand data for {sku} at {node}")
        return {"forecast_daily": r["forecast_daily"], "sales_last_14_days": json.loads(r["sales_json"])}

    def promotions(self, sku):
        return self.many("SELECT name, uplift FROM promotions WHERE sku=?", (sku,))
