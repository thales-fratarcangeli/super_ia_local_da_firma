# Suíte rápida: 14 tarefas pequenas (1 arquivo `solution.py` cada), com testes escondidos e solução de referência.
# Cada tarefa cobre um tipo de erro que o qwen3:8b cometeu na tarefa grande.
# Formato: id, prompt (o que o modelo recebe, sem sufixo), test (pytest), ref (solução correta p/ validar os testes).

TASKS = []


def task(id, prompt, test, ref):
    TASKS.append({"id": id, "prompt": prompt.strip(), "test": test.strip() + "\n", "ref": ref.strip() + "\n"})


task("t01_slugify",
     '''Implemente `slugify(text: str) -> str`: minúsculas, remove acentos (ex.: "Ação" -> "acao"), troca qualquer sequência de caracteres não alfanuméricos por um único "-", e remove "-" no início e no fim.''',
     '''
from solution import slugify

def test_basic():
    assert slugify("Hello World") == "hello-world"

def test_accents():
    assert slugify("Ação e Coração") == "acao-e-coracao"

def test_symbols_and_edges():
    assert slugify("  --Foo!!  Bar__baz--  ") == "foo-bar-baz"

def test_empty():
    assert slugify("!!!") == ""
''',
     '''
import re
import unicodedata

def slugify(text: str) -> str:
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
''')

task("t02_paginate",
     '''Implemente `paginate(items: list, page: int = 1, page_size: int = 10) -> dict` que devolve `{"items": [...], "total": int, "page": int, "page_size": int}`. `page` começa em 1. Se `page < 1` ou `page_size` fora de 1..50, levante `ValueError`. Página além do fim devolve `items` vazio.''',
     '''
import pytest
from solution import paginate

def test_first_page():
    r = paginate(list(range(25)))
    assert r == {"items": list(range(10)), "total": 25, "page": 1, "page_size": 10}

def test_last_partial():
    assert paginate(list(range(25)), 3, 10)["items"] == [20, 21, 22, 23, 24]

def test_beyond():
    assert paginate(list(range(5)), 9, 10)["items"] == []

@pytest.mark.parametrize("p,s", [(0, 10), (1, 0), (1, 51), (-1, 5)])
def test_invalid(p, s):
    with pytest.raises(ValueError):
        paginate([1], p, s)
''',
     '''
def paginate(items, page=1, page_size=10):
    if page < 1 or not 1 <= page_size <= 50:
        raise ValueError("invalid")
    start = (page - 1) * page_size
    return {"items": items[start:start + page_size], "total": len(items), "page": page, "page_size": page_size}
''')

task("t03_querystring",
     '''Implemente `parse_qs(qs: str) -> dict[str, list[str]]`. Sem usar `urllib.parse`. Aceita opcional "?" inicial, pares separados por "&", chave e valor separados pelo primeiro "=", decodifica "%XX" e "+" (espaço). Chaves repetidas acumulam valores na ordem. Chave sem "=" tem valor "". String vazia devolve {}.''',
     '''
from solution import parse_qs

def test_basic():
    assert parse_qs("a=1&b=2") == {"a": ["1"], "b": ["2"]}

def test_leading_question_and_empty():
    assert parse_qs("?x=1") == {"x": ["1"]}
    assert parse_qs("") == {}

def test_repeated_and_decoding():
    assert parse_qs("t=a+b&t=c%20d&t=%C3%A7") == {"t": ["a b", "c d", "ç"]}

def test_no_equals_and_first_equals():
    assert parse_qs("flag&k=a=b") == {"flag": [""], "k": ["a=b"]}
''',
     '''
def _dec(s):
    s = s.replace("+", " ")
    out = bytearray()
    i = 0
    b = s.encode()
    while i < len(b):
        if b[i] == 37 and i + 2 < len(b) + 0 and i + 2 <= len(b) - 1:
            try:
                out.append(int(b[i + 1:i + 3], 16))
                i += 3
                continue
            except ValueError:
                pass
        out.append(b[i])
        i += 1
    return out.decode("utf-8", "replace")

def parse_qs(qs):
    qs = qs[1:] if qs.startswith("?") else qs
    res = {}
    for part in qs.split("&"):
        if not part:
            continue
        k, _, v = part.partition("=")
        res.setdefault(_dec(k), []).append(_dec(v))
    return res
''')

task("t04_lru",
     '''Implemente a classe `LRUCache(capacity: int)` com `get(key)` (devolve o valor ou `None`, e marca a chave como recém-usada) e `put(key, value)` (insere/atualiza; ao exceder a capacidade remove a chave menos recentemente usada). Também `__len__`. `capacity <= 0` levanta `ValueError`. Operações em O(1).''',
     '''
import pytest
from solution import LRUCache

def test_eviction_order():
    c = LRUCache(2)
    c.put("a", 1); c.put("b", 2)
    assert c.get("a") == 1
    c.put("c", 3)
    assert c.get("b") is None and c.get("a") == 1 and c.get("c") == 3

def test_update_refreshes():
    c = LRUCache(2)
    c.put("a", 1); c.put("b", 2); c.put("a", 10); c.put("c", 3)
    assert c.get("a") == 10 and c.get("b") is None

def test_len_and_invalid():
    c = LRUCache(3)
    for i in range(5):
        c.put(i, i)
    assert len(c) == 3
    with pytest.raises(ValueError):
        LRUCache(0)
''',
     '''
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError("capacity")
        self.capacity = capacity
        self._d = OrderedDict()

    def get(self, key):
        if key not in self._d:
            return None
        self._d.move_to_end(key)
        return self._d[key]

    def put(self, key, value):
        self._d[key] = value
        self._d.move_to_end(key)
        if len(self._d) > self.capacity:
            self._d.popitem(last=False)

    def __len__(self):
        return len(self._d)
''')

task("t05_password",
     '''Usando apenas a biblioteca padrão (hashlib, os, hmac, base64), implemente `hash_password(password: str) -> str` e `verify_password(password: str, stored: str) -> bool`. Use PBKDF2-HMAC-SHA256 com 100000 iterações e salt aleatório de 16 bytes. Formato guardado: `pbkdf2$<iterações>$<salt em base64>$<hash em base64>`. Dois hashes da mesma senha devem ser diferentes. `verify_password` devolve False (sem levantar exceção) se `stored` estiver malformado e deve comparar em tempo constante.''',
     '''
import base64
from solution import hash_password, verify_password

def test_roundtrip():
    h = hash_password("secret123")
    assert verify_password("secret123", h)
    assert not verify_password("wrong", h)

def test_format_and_salt():
    h1, h2 = hash_password("x"), hash_password("x")
    assert h1 != h2
    parts = h1.split("$")
    assert parts[0] == "pbkdf2" and parts[1] == "100000" and len(parts) == 4
    assert len(base64.b64decode(parts[2])) == 16

def test_malformed():
    for bad in ["", "abc", "pbkdf2$x$y", "pbkdf2$abc$!!$!!"]:
        assert verify_password("x", bad) is False
''',
     '''
import base64
import hashlib
import hmac
import os

def hash_password(password):
    salt = os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return "pbkdf2$100000$" + base64.b64encode(salt).decode() + "$" + base64.b64encode(h).decode()

def verify_password(password, stored):
    try:
        scheme, it, salt, h = stored.split("$")
        if scheme != "pbkdf2":
            return False
        calc = hashlib.pbkdf2_hmac("sha256", password.encode(), base64.b64decode(salt, validate=True), int(it))
        return hmac.compare_digest(calc, base64.b64decode(h, validate=True))
    except Exception:
        return False
''')

task("t06_jwt",
     '''Usando PyJWT, implemente `create_token(user_id: int, secret: str, minutes: int = 60) -> str` (HS256, claim "sub" como string do id e "exp" em UTC) e `decode_token(token: str, secret: str) -> int | None` que devolve o user_id (int) ou `None` se o token for inválido, expirado, assinado com outro segredo ou não tiver "sub". Nunca levanta exceção.''',
     '''
import datetime
import jwt
from solution import create_token, decode_token

def test_roundtrip():
    t = create_token(42, "s" * 32)
    assert decode_token(t, "s" * 32) == 42
    p = jwt.decode(t, "s" * 32, algorithms=["HS256"])
    assert p["sub"] == "42" and "exp" in p

def test_wrong_secret_and_garbage():
    t = create_token(1, "a" * 32)
    assert decode_token(t, "b" * 32) is None
    assert decode_token("garbage", "a" * 32) is None
    assert decode_token("", "a" * 32) is None

def test_expired():
    t = create_token(1, "a" * 32, minutes=-5)
    assert decode_token(t, "a" * 32) is None

def test_no_sub():
    t = jwt.encode({"exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5)}, "a" * 32, algorithm="HS256")
    assert decode_token(t, "a" * 32) is None
''',
     '''
import datetime
import jwt

def create_token(user_id, secret, minutes=60):
    exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=minutes)
    return jwt.encode({"sub": str(user_id), "exp": exp}, secret, algorithm="HS256")

def decode_token(token, secret):
    try:
        return int(jwt.decode(token, secret, algorithms=["HS256"])["sub"])
    except Exception:
        return None
''')

task("t07_sqlite_repo",
     '''Usando apenas `sqlite3`, implemente a classe `TodoRepo(path: str = ":memory:")` que cria a tabela `todos(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0)` no construtor. Métodos: `add(title) -> int` (id novo; título vazio/só espaços levanta `ValueError`), `get(id) -> dict | None` (`{"id","title","done"}` com `done` booleano), `list(done: bool | None = None) -> list[dict]` ordenado por id, `set_done(id, done: bool) -> bool` (False se não existe), `delete(id) -> bool`. Use consultas parametrizadas (`?`), nunca f-string em SQL.''',
     '''
import pytest
from solution import TodoRepo

def test_add_get():
    r = TodoRepo()
    i = r.add("a")
    assert r.get(i) == {"id": i, "title": "a", "done": False}
    assert r.get(999) is None

def test_validation():
    r = TodoRepo()
    for bad in ["", "   "]:
        with pytest.raises(ValueError):
            r.add(bad)

def test_list_filter_and_done():
    r = TodoRepo()
    a, b, c = r.add("a"), r.add("b"), r.add("c")
    assert r.set_done(b, True) is True and r.set_done(999, True) is False
    assert [t["id"] for t in r.list()] == [a, b, c]
    assert [t["id"] for t in r.list(done=True)] == [b]
    assert [t["id"] for t in r.list(done=False)] == [a, c]
    assert r.get(b)["done"] is True

def test_delete_and_injection_safe():
    r = TodoRepo()
    i = r.add("x'); DROP TABLE todos;--")
    assert r.get(i)["title"] == "x'); DROP TABLE todos;--"
    assert r.delete(i) is True and r.delete(i) is False
    assert r.list() == []
''',
     '''
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
''')

task("t08_sqlalchemy_models",
     '''Usando SQLAlchemy 2.0 (DeclarativeBase, Mapped, mapped_column), crie no arquivo os modelos `Base`, `User` (id, name), `Project` (id, name, owner_id FK para users) e `Task` (id, title, project_id FK para projects). `User.projects` e `Project.owner` formam relação bidirecional; `Project.tasks` e `Task.project` também. Apagar um `Project` deve apagar suas `Task`s (cascade). Defina também `make_session(url: str = "sqlite://")` que cria o engine, cria as tabelas e devolve uma `Session`.''',
     '''
from solution import Base, User, Project, Task, make_session

def test_relationships_and_cascade():
    s = make_session()
    u = User(name="ana")
    p = Project(name="p", owner=u)
    p.tasks.append(Task(title="t1"))
    p.tasks.append(Task(title="t2"))
    s.add(u)
    s.commit()
    assert u.projects[0].name == "p"
    assert p.owner_id == u.id
    assert all(t.project is p for t in p.tasks)
    s.delete(p)
    s.commit()
    assert s.query(Task).count() == 0
    assert s.query(User).count() == 1

def test_tables():
    assert {"users", "projects", "tasks"} <= set(Base.metadata.tables)
''',
     '''
from sqlalchemy import ForeignKey, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    projects: Mapped[list["Project"]] = relationship(back_populates="owner")

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped[User] = relationship(back_populates="projects")
    tasks: Mapped[list["Task"]] = relationship(back_populates="project", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped[Project] = relationship(back_populates="tasks")

def make_session(url="sqlite://"):
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    return Session(engine)
''')

task("t09_fastapi_auth",
     '''Crie uma aplicação FastAPI `app` com a rota `GET /me` protegida por `Authorization: Bearer <token>`. O token válido é exatamente a string "secret-token" e a rota devolve `{"user": "admin"}`. Sem o header, com esquema errado ou token incorreto, responda **401** (não 403 nem 422) com o header `WWW-Authenticate: Bearer`. Também `GET /health` público devolvendo `{"status": "ok"}`.''',
     '''
from fastapi.testclient import TestClient
from solution import app

c = TestClient(app)

def test_ok():
    r = c.get("/me", headers={"Authorization": "Bearer secret-token"})
    assert r.status_code == 200 and r.json() == {"user": "admin"}

def test_missing_header_is_401():
    r = c.get("/me")
    assert r.status_code == 401
    assert "bearer" in r.headers.get("www-authenticate", "").lower()

def test_wrong_token_and_scheme():
    assert c.get("/me", headers={"Authorization": "Bearer nope"}).status_code == 401
    assert c.get("/me", headers={"Authorization": "Basic secret-token"}).status_code == 401
    assert c.get("/me", headers={"Authorization": "secret-token"}).status_code == 401

def test_health_public():
    assert c.get("/health").json() == {"status": "ok"}
''',
     '''
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

app = FastAPI()
bearer = HTTPBearer(auto_error=False)

def auth(creds: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if creds is None or creds.credentials != "secret-token":
        raise HTTPException(401, "Unauthorized", headers={"WWW-Authenticate": "Bearer"})
    return "admin"

@app.get("/me")
def me(user: str = Depends(auth)):
    return {"user": user}

@app.get("/health")
def health():
    return {"status": "ok"}
''')

task("t10_fastapi_pagination",
     '''Crie uma aplicação FastAPI `app` com `GET /items` que pagina uma lista fixa de 35 números inteiros de 1 a 35. Query `page` (padrão 1, mínimo 1) e `page_size` (padrão 10, mínimo 1, máximo 50), validados pelo próprio FastAPI (valores inválidos => 422). Resposta: `{"items": [...], "total": 35, "page": int, "page_size": int}`. Query opcional `min` (inteiro) filtra itens >= min antes de paginar; `total` reflete o filtro.''',
     '''
import pytest
from fastapi.testclient import TestClient
from solution import app

c = TestClient(app)

def test_default():
    r = c.get("/items").json()
    assert r == {"items": list(range(1, 11)), "total": 35, "page": 1, "page_size": 10}

def test_page_and_size():
    r = c.get("/items?page=2&page_size=20").json()
    assert r["items"] == list(range(21, 36)) and r["total"] == 35

def test_filter():
    r = c.get("/items?min=30").json()
    assert r["items"] == [30, 31, 32, 33, 34, 35] and r["total"] == 6

@pytest.mark.parametrize("q", ["page=0", "page_size=0", "page_size=51", "page=x", "min=abc"])
def test_422(q):
    assert c.get("/items?" + q).status_code == 422
''',
     '''
from typing import Optional
from fastapi import FastAPI, Query

app = FastAPI()
DATA = list(range(1, 36))

@app.get("/items")
def items(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=50), min: Optional[int] = None):
    data = [x for x in DATA if min is None or x >= min]
    s = (page - 1) * page_size
    return {"items": data[s:s + page_size], "total": len(data), "page": page, "page_size": page_size}
''')

task("t11_intervals",
     '''Implemente `merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]`: junta intervalos que se sobrepõem ou se tocam (ex.: (1,3) e (3,5) viram (1,5)), devolve ordenado, sem alterar a lista de entrada. Um intervalo com início > fim levanta `ValueError`.''',
     '''
import pytest
from solution import merge_intervals

def test_merge():
    assert merge_intervals([(5, 8), (1, 3), (2, 4)]) == [(1, 4), (5, 8)]

def test_touching_and_contained():
    assert merge_intervals([(1, 3), (3, 5), (2, 2), (10, 12), (11, 11)]) == [(1, 5), (10, 12)]

def test_empty_and_input_untouched():
    assert merge_intervals([]) == []
    x = [(3, 4), (1, 2)]
    merge_intervals(x)
    assert x == [(3, 4), (1, 2)]

def test_invalid():
    with pytest.raises(ValueError):
        merge_intervals([(4, 1)])
''',
     '''
def merge_intervals(intervals):
    for a, b in intervals:
        if a > b:
            raise ValueError("invalid")
    out = []
    for a, b in sorted(intervals):
        if out and a <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out
''')

task("t12_token_bucket",
     '''Implemente `RateLimiter(rate: float, capacity: int, clock=time.monotonic)`: balde de fichas. Começa cheio (`capacity` fichas), recebe `rate` fichas por segundo (sem passar de `capacity`), e `allow(cost: int = 1) -> bool` consome `cost` fichas se houver e devolve True, senão devolve False sem consumir. O tempo vem SEMPRE do parâmetro `clock` (função sem argumentos que devolve segundos).''',
     '''
from solution import RateLimiter

class Clock:
    def __init__(self): self.t = 100.0
    def __call__(self): return self.t

def test_burst_and_refill():
    clk = Clock()
    r = RateLimiter(rate=2, capacity=3, clock=clk)
    assert [r.allow() for _ in range(4)] == [True, True, True, False]
    clk.t += 0.5
    assert r.allow() is True and r.allow() is False
    clk.t += 10
    assert [r.allow() for _ in range(4)] == [True, True, True, False]

def test_cost_does_not_consume_on_fail():
    clk = Clock()
    r = RateLimiter(rate=1, capacity=5, clock=clk)
    assert r.allow(4) is True
    assert r.allow(2) is False
    assert r.allow(1) is True
''',
     '''
import time

class RateLimiter:
    def __init__(self, rate, capacity, clock=time.monotonic):
        self.rate, self.capacity, self.clock = rate, capacity, clock
        self.tokens = float(capacity)
        self.last = clock()

    def allow(self, cost=1):
        now = self.clock()
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False
''')

task("t13_toposort",
     '''Implemente `toposort(deps: dict[str, list[str]]) -> list[str]` onde `deps[x]` lista o que `x` precisa ANTES dele. Devolve uma ordem válida contendo todos os nós (inclusive os que só aparecem como dependência). Empates em ordem alfabética (determinístico). Ciclo levanta `ValueError`.''',
     '''
import pytest
from solution import toposort

def test_basic():
    assert toposort({"app": ["lib", "db"], "lib": ["core"], "db": ["core"]}) == ["core", "db", "lib", "app"]

def test_implicit_nodes_and_ties():
    assert toposort({"b": ["a"], "c": []}) == ["a", "b", "c"]

def test_empty():
    assert toposort({}) == []

def test_cycle():
    with pytest.raises(ValueError):
        toposort({"a": ["b"], "b": ["c"], "c": ["a"]})
    with pytest.raises(ValueError):
        toposort({"a": ["a"]})
''',
     '''
import heapq

def toposort(deps):
    nodes = set(deps)
    for v in deps.values():
        nodes.update(v)
    indeg = {n: 0 for n in nodes}
    rev = {n: [] for n in nodes}
    for n, ds in deps.items():
        for d in set(ds):
            indeg[n] += 1
            rev[d].append(n)
    heap = [n for n in nodes if indeg[n] == 0]
    heapq.heapify(heap)
    out = []
    while heap:
        n = heapq.heappop(heap)
        out.append(n)
        for m in rev[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                heapq.heappush(heap, m)
    if len(out) != len(nodes):
        raise ValueError("cycle")
    return out
''')

task("t14_pydantic",
     '''Usando Pydantic v2, crie `class SignUp(BaseModel)` com: `username` (str, 3 a 20 caracteres, só letras, números e "_"), `password` (str, mínimo 6 caracteres), `age` (int, opcional, entre 13 e 120) e `role` (Literal "member" ou "admin", padrão "member"). `username` deve ser normalizado para minúsculas. Use `field_validator` onde precisar. Dados inválidos levantam `pydantic.ValidationError`.''',
     '''
import pytest
from pydantic import ValidationError
from solution import SignUp

def test_ok_and_normalization():
    u = SignUp(username="Ana_01", password="secret1")
    assert u.username == "ana_01" and u.role == "member" and u.age is None

def test_username_rules():
    for bad in ["ab", "x" * 21, "a b c", "ana!", ""]:
        with pytest.raises(ValidationError):
            SignUp(username=bad, password="secret1")

def test_password_age_role():
    with pytest.raises(ValidationError):
        SignUp(username="ana", password="123")
    for age in (12, 121):
        with pytest.raises(ValidationError):
            SignUp(username="ana", password="secret1", age=age)
    assert SignUp(username="ana", password="secret1", age=13, role="admin").role == "admin"
    with pytest.raises(ValidationError):
        SignUp(username="ana", password="secret1", role="root")
''',
     '''
import re
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator

class SignUp(BaseModel):
    username: str
    password: str = Field(min_length=6)
    age: Optional[int] = Field(default=None, ge=13, le=120)
    role: Literal["member", "admin"] = "member"

    @field_validator("username")
    @classmethod
    def check_username(cls, v):
        if not 3 <= len(v) <= 20 or not re.fullmatch(r"[A-Za-z0-9_]+", v):
            raise ValueError("invalid username")
        return v.lower()
''')
