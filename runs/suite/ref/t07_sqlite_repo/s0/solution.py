import sqlite3

class TodoRepo:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path)
        self.db.execute("CREATE TABLE IF NOT EXISTS todos(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0)")
        self.db.commit()

    @staticmethod
    def _row(r):
        return {"id": r[0], "title": r[1], "done": bool(r[2])}

    def add(self, title):
        if not title or not title.strip():
            raise ValueError("title")
        cur = self.db.execute("INSERT INTO todos(title) VALUES (?)", (title,))
        self.db.commit()
        return cur.lastrowid

    def get(self, id):
        r = self.db.execute("SELECT id,title,done FROM todos WHERE id=?", (id,)).fetchone()
        return self._row(r) if r else None

    def list(self, done=None):
        if done is None:
            rows = self.db.execute("SELECT id,title,done FROM todos ORDER BY id").fetchall()
        else:
            rows = self.db.execute("SELECT id,title,done FROM todos WHERE done=? ORDER BY id", (int(done),)).fetchall()
        return [self._row(r) for r in rows]

    def set_done(self, id, done):
        cur = self.db.execute("UPDATE todos SET done=? WHERE id=?", (int(done), id))
        self.db.commit()
        return cur.rowcount > 0

    def delete(self, id):
        cur = self.db.execute("DELETE FROM todos WHERE id=?", (id,))
        self.db.commit()
        return cur.rowcount > 0
