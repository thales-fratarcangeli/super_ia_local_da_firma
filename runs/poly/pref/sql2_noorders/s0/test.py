
import sqlite3, sys
SETUP = "\nCREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT);\nCREATE TABLE orders(id INTEGER PRIMARY KEY, customer_id INTEGER, total INTEGER, created_at TEXT);\nINSERT INTO customers VALUES (1,'Ana'),(2,'Bruno'),(3,'Carla'),(4,'Davi');\nINSERT INTO orders VALUES (1,1,100,'2026-01-01'),(2,1,50,'2026-01-03'),(3,3,70,'2026-01-02'),(4,1,25,'2026-01-03'),(5,3,30,'2026-01-05');\n"
EXPECTED = [(2, 'Bruno'), (4, 'Davi')]
q = open("solution.sql", encoding="utf-8").read().strip().rstrip(";")
db = sqlite3.connect(":memory:")
db.executescript(SETUP)
rows = [tuple(round(x, 2) if isinstance(x, float) else x for x in r) for r in db.execute(q).fetchall()]
if rows != EXPECTED:
    print("esperado:", EXPECTED); print("obtido:  ", rows); sys.exit(1)
print("OK")
