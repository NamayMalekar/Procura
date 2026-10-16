"""The test situations (one per scenario): what a buyer's system hands to the agent."""


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
