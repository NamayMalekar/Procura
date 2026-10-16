"""The database layer: seed, clone isolation, budget accounting, persistence."""
from app.database.store import Store


def test_seed_loads_expected_tables():
    s = Store()
    snap = s.snapshot()
    assert len(snap["inventory"]) == 10 and len(snap["purchase_orders"]) == 5
    assert s.supplier_item("SUP-8", "SKU-4002")["inject"]["type"] == "price_change"


def test_clone_is_isolated_from_the_original():
    s = Store()
    c = s.clone()
    c.adjust_budget("SKU-4001", -1000)
    assert s.budget("SKU-4001")["remaining"] == 3600.0 and c.budget("SKU-4001")["remaining"] == 2600.0


def test_reset_restores_seed_data():
    s = Store()
    s.adjust_budget("SKU-4001", -500)
    s.reset()
    assert s.budget("SKU-4001")["remaining"] == 3600.0


def test_file_database_persists(tmp_path):
    path = str(tmp_path / "p.db")
    a = Store.open(path)
    a.adjust_budget("SKU-4001", -100)
    a.conn.close()
    assert Store.open(path).budget("SKU-4001")["remaining"] == 3500.0
