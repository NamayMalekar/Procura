from ._base import Repo


class CatalogRepo(Repo):
    """Products, nodes (fulfilment centres) and suppliers."""

    def product(self, sku):
        return self.one("SELECT * FROM products WHERE sku=?", (sku,))

    def products(self):
        return self.many("SELECT * FROM products ORDER BY sku")

    def supplier(self, sid):
        return self.one("SELECT * FROM suppliers WHERE id=?", (sid,))

    def nodes(self):
        return self.many("SELECT * FROM nodes")
