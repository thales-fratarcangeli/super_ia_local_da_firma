# Suíte INÉDITA (heldout), escrita pelo professor (Claude). Regra: NÃO usar estas tarefas para criar notas de RAG nem dados de treino.
# Serve só para medir se a melhora generaliza. Mesmo formato de suite/tasks.py.

TASKS = []


def task(id, prompt, test, ref):
    TASKS.append({"id": id, "prompt": prompt.strip(), "test": test.strip() + "\n", "ref": ref.strip() + "\n"})


task("h01_roman",
     '''Implemente `to_roman(n: int) -> str` (1 a 3999, notação subtrativa: 4 = "IV", 9 = "IX", 40 = "XL", 90 = "XC", 400 = "CD", 900 = "CM") e `from_roman(s: str) -> int`. Fora do intervalo em `to_roman` levanta `ValueError`. `from_roman` aceita só numerais romanos válidos em maiúsculas e levanta `ValueError` para qualquer outra coisa (ex.: "IIII", "VX", "", "abc").''',
     '''
import pytest
from solution import to_roman, from_roman

def test_known():
    assert to_roman(1994) == "MCMXCIV"
    assert to_roman(4) == "IV" and to_roman(3999) == "MMMCMXCIX" and to_roman(58) == "LVIII"

def test_roundtrip():
    for n in range(1, 4000):
        assert from_roman(to_roman(n)) == n

@pytest.mark.parametrize("n", [0, -1, 4000])
def test_to_invalid(n):
    with pytest.raises(ValueError):
        to_roman(n)

@pytest.mark.parametrize("s", ["IIII", "VX", "", "abc", "IC", "mcm"])
def test_from_invalid(s):
    with pytest.raises(ValueError):
        from_roman(s)
''',
     '''
_P = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]

def to_roman(n):
    if not 1 <= n <= 3999:
        raise ValueError("range")
    out = ""
    for v, s in _P:
        while n >= v:
            out += s
            n -= v
    return out

def from_roman(s):
    if not s or not all(c in "IVXLCDM" for c in s):
        raise ValueError("invalid")
    i, total = 0, 0
    for v, sym in _P:
        while s.startswith(sym, i):
            total += v
            i += len(sym)
    if i != len(s) or to_roman(total) != s:
        raise ValueError("invalid")
    return total
''')

task("h02_brackets",
     '''Implemente `check_brackets(text: str) -> int`: considera os pares (), [] e {} e ignora todos os outros caracteres. Devolve `-1` se estiver tudo balanceado e corretamente aninhado; senão devolve o **índice (base 0) do primeiro caractere problemático**: um fechamento sem abertura ou do tipo errado, ou, se sobrar abertura sem fechar, o índice da abertura mais antiga que ficou aberta.''',
     '''
from solution import check_brackets

def test_ok():
    assert check_brackets("") == -1
    assert check_brackets("a(b[c]{d})e") == -1

def test_wrong_close():
    assert check_brackets("(]") == 1
    assert check_brackets("a)") == 1
    assert check_brackets("([)]") == 2

def test_unclosed_reports_oldest_open():
    assert check_brackets("((") == 0
    assert check_brackets("x{[a]") == 1
''',
     '''
def check_brackets(text):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for i, c in enumerate(text):
        if c in "([{":
            stack.append((c, i))
        elif c in pairs:
            if not stack or stack[-1][0] != pairs[c]:
                return i
            stack.pop()
    return stack[0][1] if stack else -1
''')

task("h03_csv_line",
     '''Implemente `parse_csv_line(line: str) -> list[str]` sem usar o módulo `csv`. Campos separados por vírgula; um campo pode estar entre aspas duplas e então pode conter vírgulas e aspas escapadas como `""` (que viram uma aspa). Espaços fora de aspas são preservados. Linha vazia devolve `[""]`. Aspas não fechadas levantam `ValueError`.''',
     '''
import pytest
from solution import parse_csv_line

def test_simple():
    assert parse_csv_line("a,b,c") == ["a", "b", "c"]
    assert parse_csv_line("a,,c") == ["a", "", "c"]
    assert parse_csv_line("") == [""]

def test_quotes():
    assert parse_csv_line('"a,b",c') == ["a,b", "c"]
    assert parse_csv_line('"he said ""hi""",x') == ['he said "hi"', "x"]
    assert parse_csv_line('""') == [""]

def test_spaces_and_trailing():
    assert parse_csv_line(" a , b ,") == [" a ", " b ", ""]

def test_unclosed():
    with pytest.raises(ValueError):
        parse_csv_line('"abc')
''',
     '''
def parse_csv_line(line):
    out, cur, i, n = [], [], 0, len(line)
    in_q = False
    while i < n:
        c = line[i]
        if in_q:
            if c == '"':
                if i + 1 < n and line[i + 1] == '"':
                    cur.append('"')
                    i += 1
                else:
                    in_q = False
            else:
                cur.append(c)
        elif c == '"' and not cur:
            in_q = True
        elif c == ",":
            out.append("".join(cur))
            cur = []
        else:
            cur.append(c)
        i += 1
    if in_q:
        raise ValueError("unclosed quote")
    out.append("".join(cur))
    return out
''')

task("h04_kv_ttl",
     '''Implemente a classe `TTLStore(clock=time.monotonic)`, um dicionário com expiração. `set(key, value, ttl: float | None = None)` (sem ttl = não expira; `ttl <= 0` levanta `ValueError`), `get(key, default=None)` (devolve o padrão se não existe ou expirou; uma chave expira quando `clock() >= instante_de_criação + ttl`), `delete(key) -> bool` e `__len__` que conta **apenas chaves não expiradas**. O tempo vem sempre de `clock`, e chaves expiradas devem ser removidas da memória quando encontradas.''',
     '''
import pytest
from solution import TTLStore

class Clock:
    def __init__(self): self.t = 10.0
    def __call__(self): return self.t

def test_basic_and_default():
    c = Clock(); s = TTLStore(clock=c)
    s.set("a", 1)
    assert s.get("a") == 1 and s.get("zz") is None and s.get("zz", 7) == 7

def test_expiry_boundary():
    c = Clock(); s = TTLStore(clock=c)
    s.set("a", 1, ttl=5)
    c.t += 4.5
    assert s.get("a") == 1
    c.t += 0.5
    assert s.get("a") is None

def test_len_counts_only_alive_and_delete():
    c = Clock(); s = TTLStore(clock=c)
    s.set("a", 1, ttl=1); s.set("b", 2); s.set("c", 3, ttl=100)
    c.t += 2
    assert len(s) == 2
    assert s.delete("a") is False and s.delete("b") is True and len(s) == 1

def test_overwrite_resets_ttl_and_invalid():
    c = Clock(); s = TTLStore(clock=c)
    s.set("a", 1, ttl=2); c.t += 1.5; s.set("a", 2, ttl=2); c.t += 1.5
    assert s.get("a") == 2
    with pytest.raises(ValueError):
        s.set("x", 1, ttl=0)
''',
     '''
import time

class TTLStore:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self._d = {}

    def set(self, key, value, ttl=None):
        if ttl is not None and ttl <= 0:
            raise ValueError("ttl")
        self._d[key] = (value, None if ttl is None else self.clock() + ttl)

    def _alive(self, key):
        item = self._d.get(key)
        if item is None:
            return False
        if item[1] is not None and self.clock() >= item[1]:
            del self._d[key]
            return False
        return True

    def get(self, key, default=None):
        return self._d[key][0] if self._alive(key) else default

    def delete(self, key):
        if self._alive(key):
            del self._d[key]
            return True
        return False

    def __len__(self):
        for k in list(self._d):
            self._alive(k)
        return len(self._d)
''')

task("h05_fastapi_notes",
     '''Crie uma aplicação FastAPI `app` com um CRUD de notas em memória. Modelo de entrada `{"title": str (1 a 50 caracteres), "body": str (padrão "")}`. Rotas: `POST /notes` (201, devolve `{"id", "title", "body"}` com id inteiro crescente a partir de 1), `GET /notes/{id}` (404 com `{"detail": ...}` se não existe), `PUT /notes/{id}` (substitui título e corpo; 404 se não existe), `DELETE /notes/{id}` (204 sem corpo; 404 se não existe), `GET /notes` (lista ordenada por id; aceita `?q=texto` que filtra notas cujo título contenha o texto, sem diferenciar maiúsculas). Título vazio ou com mais de 50 caracteres: 422.''',
     '''
from fastapi.testclient import TestClient
from solution import app

c = TestClient(app)

def test_create_and_get():
    r = c.post("/notes", json={"title": "Compras", "body": "leite"})
    assert r.status_code == 201
    d = r.json()
    assert set(d) == {"id", "title", "body"} and d["title"] == "Compras"
    assert c.get(f"/notes/{d['id']}").json() == d

def test_default_body_and_ids_increase():
    a = c.post("/notes", json={"title": "x"}).json()
    b = c.post("/notes", json={"title": "y"}).json()
    assert a["body"] == "" and b["id"] == a["id"] + 1

def test_validation():
    assert c.post("/notes", json={"title": ""}).status_code == 422
    assert c.post("/notes", json={"title": "a" * 51}).status_code == 422
    assert c.post("/notes", json={"title": "a" * 50}).status_code == 201

def test_put_delete_404():
    n = c.post("/notes", json={"title": "orig"}).json()
    r = c.put(f"/notes/{n['id']}", json={"title": "novo", "body": "b"})
    assert r.status_code == 200 and r.json()["title"] == "novo"
    assert c.delete(f"/notes/{n['id']}").status_code == 204
    assert c.get(f"/notes/{n['id']}").status_code == 404
    assert c.put(f"/notes/{n['id']}", json={"title": "z"}).status_code == 404
    assert c.delete(f"/notes/{n['id']}").status_code == 404

def test_list_and_search():
    c.post("/notes", json={"title": "Reunião SEMANAL"})
    ids = [n["id"] for n in c.get("/notes").json()]
    assert ids == sorted(ids)
    found = c.get("/notes?q=semanal").json()
    assert found and all("semanal" in n["title"].lower() for n in found)
''',
     '''
from typing import Optional
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field

app = FastAPI()
DB = {}
_next = [1]

class NoteIn(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    body: str = ""

@app.post("/notes", status_code=201)
def create(n: NoteIn):
    i = _next[0]
    _next[0] += 1
    DB[i] = {"id": i, **n.model_dump()}
    return DB[i]

@app.get("/notes")
def list_notes(q: Optional[str] = None):
    return [v for k, v in sorted(DB.items()) if q is None or q.lower() in v["title"].lower()]

@app.get("/notes/{id}")
def get(id: int):
    if id not in DB:
        raise HTTPException(404, "not found")
    return DB[id]

@app.put("/notes/{id}")
def put(id: int, n: NoteIn):
    if id not in DB:
        raise HTTPException(404, "not found")
    DB[id] = {"id": id, **n.model_dump()}
    return DB[id]

@app.delete("/notes/{id}", status_code=204)
def delete(id: int):
    if id not in DB:
        raise HTTPException(404, "not found")
    del DB[id]
    return Response(status_code=204)
''')

task("h06_pydantic_range",
     '''Usando Pydantic v2, crie `class Booking(BaseModel)` com `guest: str` (não vazio), `start: date`, `end: date` e `nights: int | None = None`. Regras: `end` deve ser **posterior** a `start` (senão `ValidationError`); `nights` é sempre calculado como `(end - start).days` e **sobrescreve** qualquer valor recebido. Use `model_validator(mode="after")`. Datas podem vir como string ISO ("2026-03-01").''',
     '''
import pytest
from datetime import date
from pydantic import ValidationError
from solution import Booking

def test_ok_and_nights_computed():
    b = Booking(guest="Ana", start="2026-03-01", end="2026-03-05")
    assert b.nights == 4 and b.start == date(2026, 3, 1)

def test_nights_overridden():
    assert Booking(guest="Ana", start="2026-03-01", end="2026-03-02", nights=99).nights == 1

def test_end_must_be_after_start():
    for end in ["2026-03-01", "2026-02-28"]:
        with pytest.raises(ValidationError):
            Booking(guest="Ana", start="2026-03-01", end=end)

def test_guest_required():
    with pytest.raises(ValidationError):
        Booking(guest="", start="2026-03-01", end="2026-03-02")
''',
     '''
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, model_validator

class Booking(BaseModel):
    guest: str = Field(min_length=1)
    start: date
    end: date
    nights: Optional[int] = None

    @model_validator(mode="after")
    def check(self):
        if self.end <= self.start:
            raise ValueError("end must be after start")
        self.nights = (self.end - self.start).days
        return self
''')

task("h07_sqlalchemy_tags",
     '''Com SQLAlchemy 2.0, crie `Base`, `Post` (id, title) e `Tag` (id, name único) com relação **muitos-para-muitos** via tabela de associação `post_tags` (colunas `post_id`, `tag_id`, ambas chave estrangeira). `Post.tags` e `Tag.posts` são bidirecionais. Defina `make_session(url="sqlite://")` que cria as tabelas e devolve uma `Session`, e `tag_post(session, post, names: list[str])` que associa o post às tags com esses nomes, **reaproveitando tags que já existem** (sem duplicar) e sem associar a mesma tag duas vezes.''',
     '''
from solution import Base, Post, Tag, make_session, tag_post

def test_many_to_many_both_sides():
    s = make_session()
    p1, p2 = Post(title="a"), Post(title="b")
    s.add_all([p1, p2]); s.commit()
    tag_post(s, p1, ["python", "sql"])
    tag_post(s, p2, ["python"])
    s.commit()
    assert sorted(t.name for t in p1.tags) == ["python", "sql"]
    py = s.query(Tag).filter_by(name="python").one()
    assert sorted(p.title for p in py.posts) == ["a", "b"]

def test_reuse_and_no_duplicate_association():
    s = make_session()
    p = Post(title="x"); s.add(p); s.commit()
    tag_post(s, p, ["a", "a", "b"])
    tag_post(s, p, ["a"])
    s.commit()
    assert s.query(Tag).count() == 2
    assert sorted(t.name for t in p.tags) == ["a", "b"]

def test_table_exists():
    assert "post_tags" in Base.metadata.tables
''',
     '''
from sqlalchemy import Column, ForeignKey, String, Table, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

class Base(DeclarativeBase):
    pass

post_tags = Table("post_tags", Base.metadata,
                  Column("post_id", ForeignKey("posts.id"), primary_key=True),
                  Column("tag_id", ForeignKey("tags.id"), primary_key=True))

class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String)
    tags: Mapped[list["Tag"]] = relationship(secondary=post_tags, back_populates="posts")

class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    posts: Mapped[list[Post]] = relationship(secondary=post_tags, back_populates="tags")

def make_session(url="sqlite://"):
    e = create_engine(url)
    Base.metadata.create_all(e)
    return Session(e)

def tag_post(session, post, names):
    for name in dict.fromkeys(names):
        tag = session.scalar(select(Tag).where(Tag.name == name))
        if tag is None:
            tag = Tag(name=name)
            session.add(tag)
            session.flush()
        if tag not in post.tags:
            post.tags.append(tag)
''')

task("h08_duration",
     '''Implemente `parse_duration(text: str) -> int` que converte durações como "1h30m", "2d", "45s", "1d2h3m4s" em segundos (d=86400, h=3600, m=60, s=1). As unidades devem aparecer na ordem d, h, m, s, cada uma no máximo uma vez, sem espaços; ex.: "30m1h" ou "1h1h" são inválidos. Também aceita só um número inteiro sem unidade (ex.: "90") que vale segundos. Qualquer outra coisa (vazio, "abc", "-5s", "1.5h") levanta `ValueError`. Implemente também `format_duration(seconds: int) -> str` que faz o inverso usando a menor representação com d/h/m/s, omitindo unidades zeradas (ex.: 5400 -> "1h30m", 0 -> "0s"); negativo levanta `ValueError`.''',
     '''
import pytest
from solution import parse_duration, format_duration

def test_parse_ok():
    assert parse_duration("1h30m") == 5400
    assert parse_duration("2d") == 172800
    assert parse_duration("1d2h3m4s") == 93784
    assert parse_duration("45s") == 45 and parse_duration("90") == 90

@pytest.mark.parametrize("s", ["", "abc", "-5s", "1.5h", "30m1h", "1h1h", "1h 30m", "h", "5x"])
def test_parse_invalid(s):
    with pytest.raises(ValueError):
        parse_duration(s)

def test_format():
    assert format_duration(5400) == "1h30m"
    assert format_duration(0) == "0s"
    assert format_duration(93784) == "1d2h3m4s"
    assert format_duration(86400) == "1d"
    with pytest.raises(ValueError):
        format_duration(-1)

def test_roundtrip():
    for n in [1, 59, 60, 3599, 3600, 86399, 86400, 100000]:
        assert parse_duration(format_duration(n)) == n
''',
     '''
import re

_RE = re.compile(r"(?:(\\d+)d)?(?:(\\d+)h)?(?:(\\d+)m)?(?:(\\d+)s)?")

def parse_duration(text):
    if re.fullmatch(r"\\d+", text):
        return int(text)
    m = _RE.fullmatch(text)
    if not text or not m:
        raise ValueError("invalid")
    d, h, mi, s = (int(x) if x else 0 for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s

def format_duration(seconds):
    if seconds < 0:
        raise ValueError("negative")
    if seconds == 0:
        return "0s"
    out = ""
    for unit, size in (("d", 86400), ("h", 3600), ("m", 60), ("s", 1)):
        q, seconds = divmod(seconds, size)
        if q:
            out += f"{q}{unit}"
    return out
''')

task("h09_grid_path",
     '''Implemente `shortest_path(grid: list[str], start: tuple[int, int], goal: tuple[int, int]) -> int`: menor número de passos entre `start` e `goal` (linha, coluna) em uma grade onde "#" é parede e qualquer outro caractere é livre; movimentos só nas 4 direções. Devolve `-1` se não há caminho. `start == goal` devolve 0. Se `start` ou `goal` estiver fora da grade ou em uma parede, levante `ValueError`.''',
     '''
import pytest
from solution import shortest_path

G = ["..#.",
     "..#.",
     "....",
     "#..."]

def test_basic():
    assert shortest_path(G, (0, 0), (0, 3)) == 7
    assert shortest_path(G, (0, 0), (0, 0)) == 0

def test_no_path():
    assert shortest_path(["..#.", "..#."], (0, 0), (0, 3)) == -1

def test_invalid():
    with pytest.raises(ValueError):
        shortest_path(G, (0, 2), (0, 0))
    with pytest.raises(ValueError):
        shortest_path(G, (0, 0), (9, 9))
    with pytest.raises(ValueError):
        shortest_path(G, (-1, 0), (0, 0))
''',
     '''
from collections import deque

def shortest_path(grid, start, goal):
    R, C = len(grid), len(grid[0]) if grid else 0
    for r, c in (start, goal):
        if not (0 <= r < R and 0 <= c < C) or grid[r][c] == "#":
            raise ValueError("invalid")
    q = deque([(start, 0)])
    seen = {start}
    while q:
        (r, c), d = q.popleft()
        if (r, c) == goal:
            return d
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (r + dr, c + dc)
            if 0 <= n[0] < R and 0 <= n[1] < C and grid[n[0]][n[1]] != "#" and n not in seen:
                seen.add(n)
                q.append((n, d + 1))
    return -1
''')

task("h10_token_pair",
     '''Usando PyJWT, implemente `issue_pair(user_id: int, secret: str) -> dict` que devolve `{"access": str, "refresh": str}` (HS256). O access expira em 15 minutos e o refresh em 7 dias; ambos têm "sub" (string do id) e um claim `"type"` que vale "access" ou "refresh". Implemente também `refresh_access(refresh_token: str, secret: str) -> str | None`: se o refresh for válido (assinatura, expiração e `type == "refresh"`) devolve um novo access token; caso contrário (inclusive se alguém passar um access token), devolve `None` sem levantar exceção. E `verify_access(token: str, secret: str) -> int | None` que devolve o user_id só para tokens `type == "access"` válidos.''',
     '''
import datetime
import jwt
from solution import issue_pair, refresh_access, verify_access

S = "k" * 32

def test_pair_claims():
    p = issue_pair(7, S)
    a = jwt.decode(p["access"], S, algorithms=["HS256"])
    r = jwt.decode(p["refresh"], S, algorithms=["HS256"])
    assert a["type"] == "access" and r["type"] == "refresh" and a["sub"] == "7"
    da = a["exp"] - datetime.datetime.now(datetime.timezone.utc).timestamp()
    dr = r["exp"] - datetime.datetime.now(datetime.timezone.utc).timestamp()
    assert 14 * 60 < da <= 15 * 60 + 5 and 6.9 * 86400 < dr <= 7 * 86400 + 5

def test_verify_access_only():
    p = issue_pair(7, S)
    assert verify_access(p["access"], S) == 7
    assert verify_access(p["refresh"], S) is None
    assert verify_access("lixo", S) is None
    assert verify_access(p["access"], "o" * 32) is None

def test_refresh_flow():
    p = issue_pair(7, S)
    new = refresh_access(p["refresh"], S)
    assert new and verify_access(new, S) == 7
    assert refresh_access(p["access"], S) is None
    assert refresh_access("lixo", S) is None

def test_expired_refresh():
    old = jwt.encode({"sub": "7", "type": "refresh",
                      "exp": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=5)}, S, algorithm="HS256")
    assert refresh_access(old, S) is None
''',
     '''
import datetime
import jwt

def _tok(uid, secret, kind, delta):
    exp = datetime.datetime.now(datetime.timezone.utc) + delta
    return jwt.encode({"sub": str(uid), "type": kind, "exp": exp}, secret, algorithm="HS256")

def issue_pair(user_id, secret):
    return {"access": _tok(user_id, secret, "access", datetime.timedelta(minutes=15)),
            "refresh": _tok(user_id, secret, "refresh", datetime.timedelta(days=7))}

def _decode(token, secret, kind):
    try:
        p = jwt.decode(token, secret, algorithms=["HS256"])
        if p.get("type") != kind:
            return None
        return int(p["sub"])
    except Exception:
        return None

def refresh_access(refresh_token, secret):
    uid = _decode(refresh_token, secret, "refresh")
    return None if uid is None else _tok(uid, secret, "access", datetime.timedelta(minutes=15))

def verify_access(token, secret):
    return _decode(token, secret, "access")
''')
