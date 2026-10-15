"""All mock data lives here: products, stock, demand, suppliers, budgets, open POs
and the list of test CASES (one per scenario). Edit numbers to create new situations."""


def steady(base):
    """14 days of normal sales around `base`."""
    offs = [0, 1, -1, 0, 2, -2, 0, 1, -1, 0, 1, -1, 0, 1]
    return [base + o for o in offs]


def _inv(on_hand, safety, cap):
    return {"on_hand": on_hand, "safety_stock": safety, "storage_capacity": cap}


def _dem(forecast, history=None):
    return {"forecast_daily": forecast, "sales_last_14_days": history or steady(forecast)}


def _item(sup, sku, price, lead, moq, pack, avail, **extra):
    return {"supplier_id": sup, "sku": sku, "unit_price": price, "lead_time_days": lead,
            "moq": moq, "pack_size": pack, "available_qty": avail, **extra}


def _po(pid, sku, sup, qty, price, status, conf, eta):
    return {"id": pid, "sku": sku, "node": "NODE-A", "supplier_id": sup, "qty": qty,
            "unit_price": price, "status": status, "supplier_confirmed_qty": conf,
            "eta_days": eta, "created_by": "system"}


def seed():
    return {
        "nodes": {"NODE-A": {"name": "Bogota North dark store"},
                  "NODE-B": {"name": "Bogota South dark store"}},
        "products": {
            "SKU-1001": {"name": "Whole Milk 1L", "category": "Dairy", "primary_supplier": "SUP-1"},
            "SKU-1002": {"name": "Instant Coffee 200g", "category": "Grocery", "primary_supplier": "SUP-9"},
            "SKU-1003": {"name": "Pasta 500g", "category": "Grocery", "primary_supplier": "SUP-9"},
            "SKU-2001": {"name": "Bottled Water 6-pack", "category": "Beverages", "primary_supplier": "SUP-2"},
            "SKU-2002": {"name": "Rice 5kg", "category": "Grocery", "primary_supplier": "SUP-9"},
            "SKU-3001": {"name": "Energy Drink 250ml", "category": "Beverages", "primary_supplier": "SUP-5"},
            "SKU-3002": {"name": "Potato Chips 150g", "category": "Grocery", "primary_supplier": "SUP-9"},
            "SKU-4001": {"name": "Extra Virgin Olive Oil 1L", "category": "Specialty", "primary_supplier": "SUP-7"},
            "SKU-4002": {"name": "Sunflower Oil 1L", "category": "Oils", "primary_supplier": "SUP-8"},
        },
        # inventory[sku][node] = on hand, safety stock, storage slots allocated to this SKU
        "inventory": {
            "SKU-1001": {"NODE-A": _inv(110, 140, 1500), "NODE-B": _inv(650, 100, 1200)},
            "SKU-1002": {"NODE-A": _inv(250, 60, 1500)},
            "SKU-1003": {"NODE-A": _inv(80, 80, 1500)},
            "SKU-2001": {"NODE-A": _inv(110, 100, 1200)},
            "SKU-2002": {"NODE-A": _inv(300, 40, 1200)},
            "SKU-3001": {"NODE-A": _inv(120, 60, 1000)},
            "SKU-3002": {"NODE-A": _inv(200, 80, 1000)},
            "SKU-4001": {"NODE-A": _inv(220, 120, 1000)},
            "SKU-4002": {"NODE-A": _inv(90, 100, 1500)},
        },
        # demand[sku][node] = system forecast per day + the last 14 days of real sales
        "demand": {
            "SKU-1001": {"NODE-A": _dem(70), "NODE-B": _dem(40)},
            "SKU-1002": {"NODE-A": _dem(30)},
            "SKU-1003": {"NODE-A": _dem(50)},
            "SKU-2001": {"NODE-A": _dem(50)},
            "SKU-2002": {"NODE-A": _dem(20)},
            "SKU-3001": {"NODE-A": _dem(30, [30, 31, 29, 30, 32, 28, 30, 62, 68, 71, 74, 69, 72, 70])},
            "SKU-3002": {"NODE-A": _dem(40, steady(40)[:7] + [41, 39, 40, 42, 38, 40, 190])},
            "SKU-4001": {"NODE-A": _dem(60)},
            "SKU-4002": {"NODE-A": _dem(50)},
        },
        "suppliers": {
            "SUP-1": {"name": "Lacteos Andina", "reliability": 0.97},
            "SUP-2": {"name": "AquaPura", "reliability": 0.92},
            "SUP-3": {"name": "Fontana Beverages", "reliability": 0.95},
            "SUP-4": {"name": "QuickDrop Traders", "reliability": 0.60},
            "SUP-5": {"name": "Redwave Drinks", "reliability": 0.93},
            "SUP-6": {"name": "Mediterra Imports", "reliability": 0.90},
            "SUP-7": {"name": "Olivar Gourmet", "reliability": 0.96},
            "SUP-8": {"name": "SunGold Oils", "reliability": 0.94},
            "SUP-9": {"name": "Pantry Co", "reliability": 0.95},
        },
        # what each supplier sells: price, lead time, MOQ, case size, stock they can ship now
        "supplier_items": [
            _item("SUP-1", "SKU-1001", 1.20, 4, 100, 20, 5000),
            _item("SUP-9", "SKU-1002", 4.50, 7, 100, 10, 3000),
            _item("SUP-9", "SKU-1003", 0.90, 5, 200, 24, 5000),
            _item("SUP-2", "SKU-2001", 3.00, 3, 100, 10, 0),      # nothing left: already committed
            _item("SUP-3", "SKU-2001", 3.40, 4, 100, 10, 1000),
            _item("SUP-4", "SKU-2001", 3.10, 2, 50, 10, 500),      # cheap but unreliable
            _item("SUP-9", "SKU-2002", 2.00, 4, 100, 10, 0),
            _item("SUP-5", "SKU-3001", 1.50, 5, 120, 24, 5000),
            _item("SUP-9", "SKU-3002", 0.80, 4, 200, 20, 5000),
            _item("SUP-7", "SKU-4001", 8.00, 8, 100, 10, 2000),
            _item("SUP-6", "SKU-4001", 7.20, 8, 300, 10, 1500),
            # failure injection: the quote is stale, price jumps to 5.00 when we order
            _item("SUP-8", "SKU-4002", 4.00, 4, 100, 20, 3000,
                  inject={"type": "price_change", "new_price": 5.00}),
        ],
        # remaining budget per category (already net of existing open POs)
        "budgets": {
            "Dairy": {"total": 50000.0, "remaining": 20000.0},
            "Grocery": {"total": 30000.0, "remaining": 25000.0},
            "Beverages": {"total": 50000.0, "remaining": 20000.0},
            "Specialty": {"total": 20000.0, "remaining": 3600.0},
            "Oils": {"total": 10000.0, "remaining": 2800.0},
        },
        "pos": {
            "PO-9001": _po("PO-9001", "SKU-2001", "SUP-2", 500, 3.00, "partial", 250, 2),
            "PO-9002": _po("PO-9002", "SKU-2002", "SUP-9", 500, 2.00, "partial", 250, 3),
            "PO-9003": _po("PO-9003", "SKU-3001", "SUP-5", 300, 1.50, "confirmed", 300, 3),
            "PO-9004": _po("PO-9004", "SKU-3002", "SUP-9", 400, 0.80, "confirmed", 400, 2),
            "PO-9005": _po("PO-9005", "SKU-1002", "SUP-9", 600, 4.50, "confirmed", 600, 3),
        },
        "promotions": {},
        "escalations": [],
        "audit": [],
        "next_po": 10001,
    }


def _case(cid, scenario, title, ctype, sku, node, trigger, **extra):
    return {"id": cid, "scenario": scenario, "title": title, "type": ctype,
            "sku": sku, "node": node, "trigger": trigger, **extra}


CASES = [
    _case("S1a", 1, "Recommendation is sound", "purchase_recommendation", "SKU-1001", "NODE-A",
          "Purchasing system recommends buying 800 units of Whole Milk.",
          supplier_id="SUP-1", recommended_qty=800),
    _case("S1b", 1, "Recommendation ignores an open PO", "purchase_recommendation", "SKU-1002", "NODE-A",
          "Purchasing system recommends buying 800 units of Instant Coffee.",
          supplier_id="SUP-9", recommended_qty=800),
    _case("S1c", 1, "Recommendation is too large", "purchase_recommendation", "SKU-1003", "NODE-A",
          "Purchasing system recommends buying 800 units of Pasta.",
          supplier_id="SUP-9", recommended_qty=800),
    _case("S1d", 1, "Same product, other node, plenty of stock", "purchase_recommendation", "SKU-1001", "NODE-B",
          "Purchasing system recommends buying 800 units of Whole Milk for the south store.",
          supplier_id="SUP-1", recommended_qty=800),
    _case("S2a", 2, "Supplier ships half, stock is low", "supplier_shortfall", "SKU-2001", "NODE-A",
          "PO-9001 asked for 500 Bottled Water. Supplier can only supply 250.", po_id="PO-9001"),
    _case("S2b", 2, "Supplier ships half, stock is enough", "supplier_shortfall", "SKU-2002", "NODE-A",
          "PO-9002 asked for 500 Rice. Supplier can only supply 250.", po_id="PO-9002"),
    _case("S3a", 3, "Real demand surge", "demand_alert", "SKU-3001", "NODE-A",
          "Energy Drink sales are more than double the forecast. PO-9003 (300 units) is open."),
    _case("S3b", 3, "One-day spike, not a trend", "demand_alert", "SKU-3002", "NODE-A",
          "Potato Chips sales jumped last week. PO-9004 (400 units) is open."),
    _case("S4a", 4, "Budget blocks the full purchase", "purchase_recommendation", "SKU-4001", "NODE-A",
          "Purchasing system recommends buying 800 units of Olive Oil from Olivar Gourmet.",
          supplier_id="SUP-7", recommended_qty=800),
    _case("S4b", 4, "Supplier rejects the first order", "purchase_recommendation", "SKU-4002", "NODE-A",
          "Purchasing system recommends buying 560 units of Sunflower Oil.",
          supplier_id="SUP-8", recommended_qty=560),
]
