"""Loads the mock data from seed_data.py into the database tables."""
import json
from .seed_data import seed


def seed_all(conn):
    d = seed()
    c = conn
    c.executemany("INSERT INTO nodes VALUES (?,?)", [(k, v["name"]) for k, v in d["nodes"].items()])
    c.executemany("INSERT INTO products VALUES (?,?,?,?)",
                  [(k, v["name"], v["category"], v["primary_supplier"]) for k, v in d["products"].items()])
    c.executemany("INSERT INTO suppliers VALUES (?,?,?)",
                  [(k, v["name"], v["reliability"]) for k, v in d["suppliers"].items()])
    c.executemany("INSERT INTO inventory VALUES (?,?,?,?,?)",
                  [(sku, node, i["on_hand"], i["safety_stock"], i["storage_capacity"])
                   for sku, nodes in d["inventory"].items() for node, i in nodes.items()])
    c.executemany("INSERT INTO demand VALUES (?,?,?,?)",
                  [(sku, node, x["forecast_daily"], json.dumps(x["sales_last_14_days"]))
                   for sku, nodes in d["demand"].items() for node, x in nodes.items()])
    c.executemany("INSERT INTO supplier_items VALUES (?,?,?,?,?,?,?,?)",
                  [(i["supplier_id"], i["sku"], i["unit_price"], i["lead_time_days"], i["moq"], i["pack_size"],
                    i["available_qty"], json.dumps(i["inject"]) if i.get("inject") else None)
                   for i in d["supplier_items"]])
    c.executemany("INSERT INTO budgets VALUES (?,?,?)",
                  [(k, b["total"], b["remaining"]) for k, b in d["budgets"].items()])
    c.executemany("INSERT INTO purchase_orders VALUES (?,?,?,?,?,?,?,?,?,?)",
                  [(p["id"], p["sku"], p["node"], p["supplier_id"], p["qty"], p["unit_price"], p["status"],
                    p["supplier_confirmed_qty"], p["eta_days"], p["created_by"]) for p in d["pos"].values()])
    c.execute("INSERT INTO meta VALUES ('next_po', ?)", (str(d["next_po"]),))
    c.commit()
