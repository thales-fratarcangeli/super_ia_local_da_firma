
import sqlite3, sys
SETUP = "\nCREATE TABLE employees(id INTEGER PRIMARY KEY, name TEXT, dept TEXT, salary INTEGER);\nINSERT INTO employees VALUES (1,'Ana','TI',5000),(2,'Bia','TI',7000),(3,'Caio','RH',4000),(4,'Duda','RH',4400),(5,'Edu','FIN',9000),(6,'Fabi','TI',6000),(7,'Gabi','RH',4400);\n"
EXPECTED = [('FIN', 'Edu', 9000), ('RH', 'Duda', 4400), ('TI', 'Bia', 7000)]
q = open("solution.sql", encoding="utf-8").read().strip().rstrip(";")
db = sqlite3.connect(":memory:")
db.executescript(SETUP)
rows = [tuple(round(x, 2) if isinstance(x, float) else x for x in r) for r in db.execute(q).fetchall()]
if rows != EXPECTED:
    print("esperado:", EXPECTED); print("obtido:  ", rows); sys.exit(1)
print("OK")
