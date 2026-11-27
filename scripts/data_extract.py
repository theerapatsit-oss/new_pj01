print("hello world")
"""
E + L ของ ELT: อ่านไฟล์ CSV ของ Northwind จาก 2 ระบบ แล้วโหลดเข้า DuckDB โดยไม่แก้ไขเนื้อหา

รัน:
python3 scripts/data_exteact.py

ผลลัพธ์: ไฟล์ northwind.duckdb ที่มี schema ชื่อ raw และตาราง 9 ตาราง (จากระบบขายปัจจุบัน 7 และระบบขายเดิม 2)
รันซ้ำได้กี่ครั้งก็ได้ (CREATE OR REPLACE) ผลลัพธ์เหมือนเดิมทุกครั้ง
"""

import sys
from pathlib import Path
import duckdb

# ให้พิมพ์ภาษาไทยได้บน Windows ทุกรุ่น
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ไฟล์อยู่ที่ scripts/xxx.py -> .parent.parent คือโฟลเดอร์หลักของโปรเจกต์ (/workspaces/new_pj01)
ROOT = Path(__file__).resolve().parent.parent
print("ROOT:", ROOT)

DATA_DIR = ROOT / "Data"
DB_PATH = ROOT / "northwind.duckdb"

# ตารางใน schema raw → ไฟล์ต้นทาง (มาจาก 2 ระบบ)
SOURCES = {
    # แหล่ง A: ระบบขายปัจจุบัน
    "customer": "raw/customer.csv",
    "employees": "raw/employees.csv",
    "order_details": "raw/order_details.csv",
    "orders": "raw/orders.csv",
    "products": "raw/products.csv",
    "shippers": "raw/shippers.csv",
    "suppliers": "raw/suppliers.csv",
    # แหล่ง B: ระบบขายเดิม (มีเฉพาะใบสั่งซื้อและรายการสินค้า)
    "legacy_orders": "legacy/orders.csv",
    "legacy_order_details": "legacy/order_details.csv",
}


def main() -> None:
    con = duckdb.connect(str(DB_PATH))
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")

    print(f"โหลดข้อมูลเข้า {DB_PATH.name}")
    for table, relative_path in SOURCES.items():
        csv_path = DATA_DIR / relative_path
        if not csv_path.exists():
            raise FileNotFoundError(f"ไม่พบไฟล์ {csv_path}")

        # Extract: read_csv อ่านไฟล์และเดาชนิดข้อมูลให้
        # Load: CREATE OR REPLACE TABLE เขียนทับตารางเดิมทั้งตาราง (full refresh)
        con.execute(
            f"""
            CREATE OR REPLACE TABLE raw.{table} AS
            SELECT *
            FROM read_csv('{csv_path.as_posix()}', header = true)
            """
        )
        n = con.execute(f"SELECT COUNT(*) FROM raw.{table}").fetchall()[0][0]
        print(f"  raw.{table:<22} {n:>6,} แถว")

    con.close()
    print("เสร็จแล้ว — ขั้นต่อไป: dbt run")


if __name__ == "__main__":
    main()