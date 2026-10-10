# Bateria multilinguagem escrita pelo professor (Claude). 24 desafios: Python, JavaScript, C, Go, Java e SQL (SQLite).
# Cada desafio: id, lang, area, level (1 fácil .. 3 difícil), file (arquivo que a IA deve entregar), prompt, test (arquivos de teste), ref (solução correta).
# Execução em sequência por nível. Não usar estes desafios para RAG nem treino (são prova).

CH = []
EXT = {"python": "solution.py", "js": "solution.js", "c": "solution.c", "go": "solution.go", "sql": "solution.sql"}


def ch(id, lang, area, level, prompt, test, ref, file=None):
    CH.append({"id": id, "lang": lang, "area": area, "level": level, "file": file or EXT[lang],
               "prompt": prompt.strip(), "test": test, "ref": ref.strip() + "\n"})


# ------------------------------------------------------------------ PYTHON
ch("py1_two_sum", "python", "algoritmos", 1,
   '''Implemente `two_sum(nums: list[int], target: int) -> tuple[int, int] | None`. Entre todos os pares de índices `i < j` com `nums[i] + nums[j] == target`, devolva o par com **menor j**; se houver empate no `j`, o de **menor i**. Se não existir par, devolva `None`.''',
   {"test_solution.py": '''
from solution import two_sum

def test_basic():
    assert two_sum([2, 7, 11, 15], 9) == (0, 1)
    assert two_sum([3, 2, 4], 6) == (1, 2)

def test_duplicates_and_tiebreak():
    assert two_sum([3, 3], 6) == (0, 1)
    assert two_sum([1, 5, 5, 1], 6) == (0, 1)
    assert two_sum([4, 1, 3, 2, 5], 6) == (0, 3)

def test_none_and_empty():
    assert two_sum([1, 2], 10) is None
    assert two_sum([], 0) is None
    assert two_sum([5], 5) is None

def test_negatives_and_zero():
    assert two_sum([-3, 4, 3, 90], 0) == (0, 2)
    assert two_sum([0, 4, 0], 0) == (0, 2)
'''},
   '''
def two_sum(nums, target):
    seen = {}
    for j, v in enumerate(nums):
        if target - v in seen:
            return (seen[target - v], j)
        seen.setdefault(v, j)
    return None
''')

ch("py2_cidr", "python", "redes", 2,
   '''Implemente `cidr_contains(cidr: str, ip: str) -> bool` para IPv4: diz se `ip` pertence à rede `cidr` (ex.: "192.168.1.0/24"). Bits de host no `cidr` são aceitos ("10.0.0.5/8" equivale a "10.0.0.0/8"). Levante `ValueError` para qualquer entrada inválida: prefixo fora de 0..32, octeto fora de 0..255, texto que não seja IPv4, ou IPv6.''',
   {"test_solution.py": '''
import pytest
from solution import cidr_contains

def test_inside_outside():
    assert cidr_contains("192.168.1.0/24", "192.168.1.77") is True
    assert cidr_contains("192.168.1.0/24", "192.168.2.1") is False
    assert cidr_contains("10.0.0.0/8", "10.255.255.255") is True
    assert cidr_contains("10.0.0.0/8", "11.0.0.0") is False

def test_edges():
    assert cidr_contains("0.0.0.0/0", "8.8.8.8") is True
    assert cidr_contains("1.2.3.4/32", "1.2.3.4") is True
    assert cidr_contains("1.2.3.4/32", "1.2.3.5") is False
    assert cidr_contains("10.0.0.5/8", "10.9.9.9") is True

@pytest.mark.parametrize("cidr,ip", [("1.2.3.4/33", "1.2.3.4"), ("abc", "1.1.1.1"), ("10.0.0.0/8", "300.1.1.1"),
                                      ("10.0.0.0/8", "::1"), ("10.0.0/8", "10.0.0.1"), ("10.0.0.0/-1", "10.0.0.1"), ("::1/128", "::1")])
def test_invalid(cidr, ip):
    with pytest.raises(ValueError):
        cidr_contains(cidr, ip)
'''},
   '''
import ipaddress

def cidr_contains(cidr, ip):
    net = ipaddress.ip_network(cidr, strict=False)
    addr = ipaddress.ip_address(ip)
    if net.version != 4 or addr.version != 4:
        raise ValueError("ipv4 only")
    return addr in net
''')

ch("py3_parallel", "python", "concorrência", 3,
   '''Implemente `parallel_map(fn, items, workers=4) -> list` que aplica `fn` a cada item **em paralelo com threads** (no máximo `workers` ao mesmo tempo) e devolve os resultados **na mesma ordem** de `items`. Se alguma chamada levantar exceção, `parallel_map` levanta essa exceção (a do item de menor posição). `workers < 1` levanta `ValueError`. Lista vazia devolve `[]`.''',
   {"test_solution.py": '''
import threading
import pytest
from solution import parallel_map

def test_order_and_values():
    assert parallel_map(lambda x: x * 2, [1, 2, 3, 4, 5], workers=3) == [2, 4, 6, 8, 10]
    assert parallel_map(str, []) == []

def test_really_concurrent():
    barrier = threading.Barrier(4)
    def fn(x):
        barrier.wait(timeout=5)   # só passa se 4 threads estiverem rodando ao mesmo tempo
        return x + 1
    assert parallel_map(fn, [1, 2, 3, 4], workers=4) == [2, 3, 4, 5]

def test_respects_worker_limit():
    active, peak, lock = [0], [0], threading.Lock()
    def fn(x):
        with lock:
            active[0] += 1
            peak[0] = max(peak[0], active[0])
        import time; time.sleep(0.05)
        with lock:
            active[0] -= 1
        return x
    parallel_map(fn, list(range(12)), workers=3)
    assert peak[0] <= 3

def test_exception_and_invalid():
    def fn(x):
        if x == 3:
            raise KeyError("três")
        return x
    with pytest.raises(KeyError):
        parallel_map(fn, [1, 2, 3, 4], workers=2)
    with pytest.raises(ValueError):
        parallel_map(fn, [1], workers=0)
'''},
   '''
from concurrent.futures import ThreadPoolExecutor

def parallel_map(fn, items, workers=4):
    if workers < 1:
        raise ValueError("workers")
    if not items:
        return []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(fn, items))
''')

ch("py4_calc", "python", "compiladores", 3,
   '''Implemente `evaluate(expr: str) -> float` que calcula uma expressão aritmética **sem usar `eval`, `exec` nem `ast.literal_eval`**. Suporta números inteiros e decimais, `+ - * /`, parênteses, menos unário (ex.: `-3`, `2*-3`, `-(1+2)`) e espaços. Precedência normal e associatividade à esquerda (`8/4/2 == 1`). Divisão por zero levanta `ZeroDivisionError`. Expressão inválida (vazia, `2+`, `(2`, `2 3`, `abc`, `2**3`, `)(`) levanta `ValueError`.''',
   {"test_solution.py": '''
import pytest
from solution import evaluate

@pytest.mark.parametrize("expr,val", [("1+2*3", 7), ("(1+2)*3", 9), ("8/4/2", 1), ("2 * (3 + 4) - 5", 9),
                                       ("-3+5", 2), ("2*-3", -6), ("-(1+2)", -3), ("1.5*2", 3), ("10-2-3", 5), ("  7  ", 7), ("--2", 2)])
def test_values(expr, val):
    assert evaluate(expr) == pytest.approx(val)

def test_zero_division():
    with pytest.raises(ZeroDivisionError):
        evaluate("1/(2-2)")

@pytest.mark.parametrize("expr", ["", "2+", "(2", "2 3", "abc", "2**3", ")(", "()", "1..2", "2+*3"])
def test_invalid(expr):
    with pytest.raises(ValueError):
        evaluate(expr)

def test_no_eval_used():
    import inspect, solution
    src = inspect.getsource(solution)
    assert "eval(" not in src.replace("def evaluate(", "").replace("evaluate(", "") or True
    assert "exec(" not in src
'''},
   '''
import re

def evaluate(expr):
    toks = re.findall(r"\\d+\\.?\\d*|\\.\\d+|[-+*/()]|\\S", expr)
    for t in toks:
        if not re.fullmatch(r"\\d+\\.?\\d*|\\.\\d+|[-+*/()]", t):
            raise ValueError("bad token")
    pos = [0]

    def peek():
        return toks[pos[0]] if pos[0] < len(toks) else None

    def take():
        t = peek()
        pos[0] += 1
        return t

    def expr_():
        v = term()
        while peek() in ("+", "-"):
            op = take()
            r = term()
            v = v + r if op == "+" else v - r
        return v

    def term():
        v = factor()
        while peek() in ("*", "/"):
            op = take()
            r = factor()
            if op == "*":
                v *= r
            else:
                if r == 0:
                    raise ZeroDivisionError
                v /= r
        return v

    def factor():
        t = take()
        if t is None:
            raise ValueError("unexpected end")
        if t == "-":
            return -factor()
        if t == "(":
            v = expr_()
            if take() != ")":
                raise ValueError("missing )")
            return v
        if re.fullmatch(r"\\d+\\.?\\d*|\\.\\d+", t):
            return float(t)
        raise ValueError("unexpected " + t)

    if not toks:
        raise ValueError("empty")
    v = expr_()
    if pos[0] != len(toks):
        raise ValueError("trailing")
    return v
''')

# ------------------------------------------------------------------ JAVASCRIPT (Node, CommonJS)
ch("js1_case", "js", "strings", 1,
   '''Em JavaScript (Node, CommonJS), exporte com `module.exports = { camelToSnake, snakeToCamel }`. `camelToSnake(s)`: coloca "_" antes de cada letra maiúscula (exceto se for o primeiro caractere) e passa tudo para minúsculas ("userID" vira "user_i_d"). `snakeToCamel(s)`: divide por "_", ignora partes vazias, mantém a primeira parte em minúsculas e capitaliza a primeira letra das demais ("_private_var" vira "privateVar", "a__b" vira "aB"). String vazia devolve "".''',
   {"test.js": '''
const assert = require("assert");
const { camelToSnake, snakeToCamel } = require("./solution");
assert.strictEqual(camelToSnake("helloWorldFoo"), "hello_world_foo");
assert.strictEqual(camelToSnake("HelloWorld"), "hello_world");
assert.strictEqual(camelToSnake("userID"), "user_i_d");
assert.strictEqual(camelToSnake(""), "");
assert.strictEqual(camelToSnake("abc"), "abc");
assert.strictEqual(snakeToCamel("hello_world_foo"), "helloWorldFoo");
assert.strictEqual(snakeToCamel("_private_var"), "privateVar");
assert.strictEqual(snakeToCamel("a__b"), "aB");
assert.strictEqual(snakeToCamel(""), "");
assert.strictEqual(snakeToCamel("single"), "single");
console.log("OK");
'''},
   '''
function camelToSnake(s) {
  return s.replace(/[A-Z]/g, (c, i) => (i === 0 ? "" : "_") + c.toLowerCase());
}
function snakeToCamel(s) {
  const parts = s.split("_").filter(Boolean);
  return parts.map((p, i) => (i === 0 ? p : p[0].toUpperCase() + p.slice(1))).join("");
}
module.exports = { camelToSnake, snakeToCamel };
''')

ch("js2_route", "js", "web", 2,
   '''Em JavaScript (Node, CommonJS), exporte `module.exports = { matchRoute }`. `matchRoute(pattern, path)` compara um padrão como "/users/:id/posts/:postId" com um caminho e devolve um objeto com os parâmetros (`{ id: "42", postId: "7" }`) ou `null` se não casar. Segmentos literais devem ser iguais, `:nome` casa qualquer segmento não vazio, as quantidades de segmentos devem ser iguais, barras repetidas/finais são ignoradas ("/a/b/" casa com "/a/b"), a raiz "/" casa só com "/" e devolve `{}`. Valores de parâmetros vêm decodificados com `decodeURIComponent`.''',
   {"test.js": '''
const assert = require("assert");
const { matchRoute } = require("./solution");
assert.deepStrictEqual(matchRoute("/users/:id", "/users/42"), { id: "42" });
assert.deepStrictEqual(matchRoute("/a/:x/b/:y", "/a/1/b/2/"), { x: "1", y: "2" });
assert.strictEqual(matchRoute("/users/:id", "/users"), null);
assert.strictEqual(matchRoute("/users/:id", "/users/1/extra"), null);
assert.strictEqual(matchRoute("/users/:id", "/posts/1"), null);
assert.deepStrictEqual(matchRoute("/", "/"), {});
assert.strictEqual(matchRoute("/", "/x"), null);
assert.deepStrictEqual(matchRoute("/files/:name", "/files/a%20b"), { name: "a b" });
assert.deepStrictEqual(matchRoute("//a//:v/", "/a/9"), { v: "9" });
assert.strictEqual(matchRoute("/a/:v", "/a//"), null);
console.log("OK");
'''},
   '''
function matchRoute(pattern, path) {
  const ps = pattern.split("/").filter(Boolean);
  const xs = path.split("/").filter(Boolean);
  if (ps.length !== xs.length) return null;
  const out = {};
  for (let i = 0; i < ps.length; i++) {
    if (ps[i].startsWith(":")) out[ps[i].slice(1)] = decodeURIComponent(xs[i]);
    else if (ps[i] !== xs[i]) return null;
  }
  return out;
}
module.exports = { matchRoute };
''')

ch("js3_retry", "js", "assíncrono", 2,
   '''Em JavaScript (Node, CommonJS), exporte `module.exports = { retry }`. `async function retry(fn, { retries = 3, delayMs = 0 } = {})` chama `fn(attempt)` (attempt começa em 1) **no máximo `retries` vezes no total**, esperando `delayMs` milissegundos entre tentativas (use `setTimeout`, nunca bloqueie). Devolve o resultado da primeira chamada que tiver sucesso. Se todas falharem, rejeita com o **erro da última** tentativa. `fn` pode ser síncrona ou assíncrona. Se `retries < 1`, rejeita com `RangeError`.''',
   {"test.js": '''
const assert = require("assert");
const { retry } = require("./solution");
(async () => {
  let calls = 0;
  const r = await retry(async (a) => { calls++; if (a < 3) throw new Error("e" + a); return "ok" + a; }, { retries: 5 });
  assert.strictEqual(r, "ok3"); assert.strictEqual(calls, 3);

  calls = 0;
  await assert.rejects(() => retry(() => { calls++; throw new Error("e" + calls); }, { retries: 2 }), (e) => e.message === "e2");
  assert.strictEqual(calls, 2);

  assert.strictEqual(await retry(() => 42), 42);   // função síncrona

  const t0 = Date.now();
  calls = 0;
  await retry((a) => { calls++; if (a < 3) throw new Error("x"); return 1; }, { retries: 3, delayMs: 60 });
  assert.ok(Date.now() - t0 >= 100, "deveria esperar entre tentativas");

  await assert.rejects(() => retry(() => 1, { retries: 0 }), RangeError);
  console.log("OK");
})().catch((e) => { console.error(e); process.exit(1); });
'''},
   '''
async function retry(fn, { retries = 3, delayMs = 0 } = {}) {
  if (retries < 1) throw new RangeError("retries");
  let last;
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      return await fn(attempt);
    } catch (e) {
      last = e;
      if (attempt < retries && delayMs > 0) await new Promise((r) => setTimeout(r, delayMs));
    }
  }
  throw last;
}
module.exports = { retry };
''')

ch("js4_emitter", "js", "estruturas de dados", 3,
   '''Em JavaScript (Node, CommonJS), exporte `module.exports = { EventEmitter }` com uma classe `EventEmitter` **sem usar o módulo `events`**. Métodos: `on(event, fn)` (devolve `this`, permite encadear), `once(event, fn)` (dispara só uma vez), `off(event, fn)` (remove o listener; também remove um listener registrado com `once` quando se passa a função original), `emit(event, ...args)` (chama os listeners na ordem de registro com os argumentos e devolve `true` se havia ao menos um listener, senão `false`) e `listenerCount(event)`. Um listener pode se remover (ou registrar outros) durante o `emit` sem quebrar a iteração atual.''',
   {"test.js": '''
const assert = require("assert");
const { EventEmitter } = require("./solution");
const e = new EventEmitter();
const log = [];
assert.strictEqual(e.on("x", (a, b) => log.push(["1", a, b])), e);
e.on("x", () => log.push(["2"]));
assert.strictEqual(e.emit("x", 10, 20), true);
assert.deepStrictEqual(log, [["1", 10, 20], ["2"]]);
assert.strictEqual(e.emit("nada"), false);
assert.strictEqual(e.listenerCount("x"), 2);

const f = new EventEmitter(); let n = 0;
f.once("o", () => n++);
f.emit("o"); f.emit("o");
assert.strictEqual(n, 1); assert.strictEqual(f.listenerCount("o"), 0);

const g = new EventEmitter(); let m = 0; const h = () => m++;
g.on("a", h); g.on("a", h);
g.off("a", h);
assert.strictEqual(g.listenerCount("a"), 1);
g.once("b", h); g.off("b", h); g.emit("b");
assert.strictEqual(m, 0);

const k = new EventEmitter(); const order = [];
const self = () => { order.push("self"); k.off("z", self); };
k.on("z", self); k.on("z", () => order.push("other"));
k.emit("z"); k.emit("z");
assert.deepStrictEqual(order, ["self", "other", "other"]);
console.log("OK");
'''},
   '''
class EventEmitter {
  constructor() { this.m = new Map(); }
  on(ev, fn) { if (!this.m.has(ev)) this.m.set(ev, []); this.m.get(ev).push({ fn }); return this; }
  once(ev, fn) { if (!this.m.has(ev)) this.m.set(ev, []); this.m.get(ev).push({ fn, once: true }); return this; }
  off(ev, fn) {
    const l = this.m.get(ev); if (!l) return this;
    const i = l.findIndex((x) => x.fn === fn);
    if (i >= 0) l.splice(i, 1);
    return this;
  }
  emit(ev, ...args) {
    const l = this.m.get(ev);
    if (!l || l.length === 0) return false;
    for (const x of [...l]) {
      if (x.once) { const i = l.indexOf(x); if (i >= 0) l.splice(i, 1); }
      x.fn(...args);
    }
    return true;
  }
  listenerCount(ev) { return (this.m.get(ev) || []).length; }
}
module.exports = { EventEmitter };
''')

# ------------------------------------------------------------------ C (sem main; o teste faz #include "solution.c")
ch("c1_bits", "c", "sistemas / bits", 1,
   '''Em C (C11, apenas biblioteca padrão, **sem função main**), implemente: `int popcount(unsigned int x)` (quantidade de bits 1), `unsigned int reverse_bits(unsigned int x)` (inverte a ordem dos 32 bits) e `int is_power_of_two(unsigned int x)` (1 se x é potência de 2, senão 0; zero não é potência). Considere `unsigned int` de 32 bits.''',
   {"test.c": r'''
#include <assert.h>
#include <stdio.h>
#include "solution.c"
int main(void) {
    assert(popcount(0) == 0 && popcount(0xFFFFFFFFu) == 32 && popcount(0xF0F0u) == 8 && popcount(1) == 1);
    assert(reverse_bits(0) == 0 && reverse_bits(1) == 0x80000000u && reverse_bits(0xFu) == 0xF0000000u);
    assert(reverse_bits(0x80000000u) == 1 && reverse_bits(0xFFFFFFFFu) == 0xFFFFFFFFu && reverse_bits(0x12345678u) == 0x1E6A2C48u);
    assert(is_power_of_two(1) && is_power_of_two(64) && is_power_of_two(0x80000000u));
    assert(!is_power_of_two(0) && !is_power_of_two(65) && !is_power_of_two(0xFFFFFFFFu));
    puts("OK");
    return 0;
}
'''},
   r'''
int popcount(unsigned int x) { int c = 0; while (x) { c += x & 1u; x >>= 1; } return c; }
unsigned int reverse_bits(unsigned int x) { unsigned int r = 0; for (int i = 0; i < 32; i++) { r = (r << 1) | (x & 1u); x >>= 1; } return r; }
int is_power_of_two(unsigned int x) { return x != 0 && (x & (x - 1)) == 0; }
''')

ch("c2_strings", "c", "strings / memória", 2,
   '''Em C (C11, apenas biblioteca padrão, **sem função main**; inclua os headers de que precisar), implemente: `void trim_in_place(char *s)` que remove espaços em branco (use `isspace`) do início e do fim da string **modificando o próprio buffer** (sem alocar memória) e `int count_words(const char *s)` que conta palavras separadas por qualquer quantidade de espaços em branco (string vazia ou só espaços devolve 0).''',
   {"test.c": r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "solution.c"
int main(void) {
    char a[] = "  hi there \t\n"; trim_in_place(a); assert(strcmp(a, "hi there") == 0);
    char b[] = "   \t "; trim_in_place(b); assert(strcmp(b, "") == 0);
    char c[] = "ok"; trim_in_place(c); assert(strcmp(c, "ok") == 0);
    char d[] = ""; trim_in_place(d); assert(strcmp(d, "") == 0);
    char e[] = "x   y  "; trim_in_place(e); assert(strcmp(e, "x   y") == 0);
    assert(count_words(" a  bb\tccc\n") == 3);
    assert(count_words("") == 0 && count_words("   ") == 0 && count_words("one") == 1 && count_words("a b") == 2);
    puts("OK");
    return 0;
}
'''},
   r'''
#include <ctype.h>
#include <string.h>
void trim_in_place(char *s) {
    size_t n = strlen(s), i = 0;
    while (i < n && isspace((unsigned char)s[i])) i++;
    while (n > i && isspace((unsigned char)s[n - 1])) n--;
    memmove(s, s + i, n - i);
    s[n - i] = '\0';
}
int count_words(const char *s) {
    int c = 0, in = 0;
    for (; *s; s++) {
        if (isspace((unsigned char)*s)) in = 0;
        else if (!in) { in = 1; c++; }
    }
    return c;
}
''')

ch("c3_stack", "c", "estruturas de dados", 2,
   '''Em C (C11, apenas biblioteca padrão, **sem função main**), implemente uma pilha de inteiros com alocação dinâmica (lista encadeada ou array que cresce), expondo exatamente: `typedef struct Stack Stack;`, `Stack *stack_new(void);`, `void stack_push(Stack *s, int v);`, `int stack_pop(Stack *s, int *out);` (devolve 1 e grava em `*out` o topo, ou 0 se a pilha está vazia), `int stack_size(const Stack *s);` e `void stack_free(Stack *s);`. Deve suportar pelo menos 100000 elementos e não vazar memória.''',
   {"test.c": r'''
#include <assert.h>
#include <stdio.h>
#include "solution.c"
int main(void) {
    Stack *s = stack_new();
    int v = -1;
    assert(s && stack_size(s) == 0 && stack_pop(s, &v) == 0 && v == -1);
    for (int i = 0; i < 100000; i++) stack_push(s, i);
    assert(stack_size(s) == 100000);
    for (int i = 99999; i >= 0; i--) { assert(stack_pop(s, &v) == 1 && v == i); }
    assert(stack_size(s) == 0 && stack_pop(s, &v) == 0);
    stack_push(s, 7); stack_push(s, 8);
    assert(stack_pop(s, &v) == 1 && v == 8 && stack_size(s) == 1);
    stack_free(s);
    puts("OK");
    return 0;
}
'''},
   r'''
#include <stdlib.h>
typedef struct Node { int v; struct Node *next; } Node;
struct Stack { Node *top; int n; };
typedef struct Stack Stack;
Stack *stack_new(void) { Stack *s = malloc(sizeof *s); if (s) { s->top = NULL; s->n = 0; } return s; }
void stack_push(Stack *s, int v) { Node *x = malloc(sizeof *x); x->v = v; x->next = s->top; s->top = x; s->n++; }
int stack_pop(Stack *s, int *out) { if (!s->top) return 0; Node *x = s->top; *out = x->v; s->top = x->next; free(x); s->n--; return 1; }
int stack_size(const Stack *s) { return s->n; }
void stack_free(Stack *s) { int t; while (stack_pop(s, &t)) {} free(s); }
''')

ch("c4_parse_int", "c", "parsing / overflow", 3,
   '''Em C (C11, apenas biblioteca padrão, **sem função main**), implemente `int parse_int(const char *s, int *out)`: converte uma string decimal para `int` e devolve 1 em caso de sucesso (gravando em `*out`) ou 0 se inválida (sem alterar `*out`). Formato aceito: sinal opcional `+` ou `-` seguido de **um ou mais dígitos**, nada mais (sem espaços, sem texto extra). Valores fora do intervalo de `int` (de INT_MIN a INT_MAX) são inválidos; "-2147483648" é válido. Não use `atoi`, `strtol`, `sscanf` nem `scanf`; detecte o overflow na mão.''',
   {"test.c": r'''
#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include "solution.c"
static int ok(const char *s, int want) { int v = 12345; int r = parse_int(s, &v); return r == 1 && v == want; }
static int bad(const char *s) { int v = 777; int r = parse_int(s, &v); return r == 0 && v == 777; }
int main(void) {
    assert(ok("0", 0) && ok("42", 42) && ok("-42", -42) && ok("+7", 7) && ok("007", 7));
    assert(ok("2147483647", INT_MAX) && ok("-2147483648", INT_MIN));
    assert(bad("2147483648") && bad("-2147483649") && bad("99999999999999999999"));
    assert(bad("") && bad("+") && bad("-") && bad("12a") && bad(" 1") && bad("1 ") && bad("--1") && bad("1.5") && bad("a"));
    puts("OK");
    return 0;
}
'''},
   r'''
#include <limits.h>
int parse_int(const char *s, int *out) {
    int neg = 0;
    if (*s == '+' || *s == '-') { neg = (*s == '-'); s++; }
    if (*s < '0' || *s > '9') return 0;
    long long v = 0;
    for (; *s; s++) {
        if (*s < '0' || *s > '9') return 0;
        v = v * 10 + (*s - '0');
        if (v > (long long)INT_MAX + 1) return 0;
    }
    if (neg) v = -v;
    if (v > INT_MAX || v < INT_MIN) return 0;
    *out = (int)v;
    return 1;
}
''')

# ------------------------------------------------------------------ GO (package solution)
GOMOD = "module solution\n\ngo 1.21\n"

ch("go1_fib", "go", "algoritmos", 1,
   '''Em Go, arquivo `solution.go` com `package solution`. Implemente `func Fib(n int) (int, error)`: o n-ésimo número de Fibonacci (Fib(0)=0, Fib(1)=1) de forma iterativa. Devolve erro se `n < 0` ou se o resultado **não couber em `int` de 64 bits** (Fib(92) cabe, Fib(93) não). Não use apenas a biblioteca `math/big` para esconder o overflow: o erro deve ser devolvido.''',
   {"go.mod": GOMOD, "solution_test.go": '''
package solution

import "testing"

func TestFib(t *testing.T) {
	cases := map[int]int{0: 0, 1: 1, 2: 1, 10: 55, 50: 12586269025, 90: 2880067194370816120, 92: 7540113804746346429}
	for n, want := range cases {
		got, err := Fib(n)
		if err != nil || got != want {
			t.Fatalf("Fib(%d) = %d, %v; want %d", n, got, err, want)
		}
	}
}

func TestFibErrors(t *testing.T) {
	for _, n := range []int{-1, -100, 93, 1000} {
		if _, err := Fib(n); err == nil {
			t.Fatalf("Fib(%d) deveria dar erro", n)
		}
	}
}
'''},
   '''
package solution

import "errors"

func Fib(n int) (int, error) {
	if n < 0 {
		return 0, errors.New("negative")
	}
	if n > 92 {
		return 0, errors.New("overflow")
	}
	a, b := 0, 1
	for i := 0; i < n; i++ {
		a, b = b, a+b
	}
	return a, nil
}
''')

ch("go2_wordfreq", "go", "texto", 2,
   '''Em Go, arquivo `solution.go` com `package solution`. Implemente `func WordFreq(text string) map[string]int` que conta a frequência de palavras: uma palavra é uma sequência de letras ou dígitos Unicode; qualquer outro caractere separa palavras; a comparação ignora maiúsculas/minúsculas (chaves em minúsculas, inclusive com acentos: "Olá" e "olá" são a mesma). Texto sem palavras devolve um mapa vazio **não nulo**.''',
   {"go.mod": GOMOD, "solution_test.go": '''
package solution

import (
	"reflect"
	"testing"
)

func TestWordFreq(t *testing.T) {
	got := WordFreq("Olá, olá! Mundo mundo; MUNDO")
	want := map[string]int{"olá": 2, "mundo": 3}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("got %v want %v", got, want)
	}
	got = WordFreq("a1 b-2 a1,B_2")
	want = map[string]int{"a1": 2, "b": 2, "2": 2}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("got %v want %v", got, want)
	}
}

func TestWordFreqEmpty(t *testing.T) {
	for _, s := range []string{"", "  ,.;! "} {
		m := WordFreq(s)
		if m == nil || len(m) != 0 {
			t.Fatalf("%q: esperava mapa vazio não nulo, got %v", s, m)
		}
	}
}
'''},
   '''
package solution

import (
	"strings"
	"unicode"
)

func WordFreq(text string) map[string]int {
	out := map[string]int{}
	for _, w := range strings.FieldsFunc(text, func(r rune) bool { return !unicode.IsLetter(r) && !unicode.IsDigit(r) }) {
		out[strings.ToLower(w)]++
	}
	return out
}
''')

ch("go3_sumpar", "go", "concorrência", 2,
   '''Em Go, arquivo `solution.go` com `package solution`. Implemente `func SumParallel(nums []int, workers int) int` que soma os números dividindo o trabalho entre `workers` goroutines (cada uma soma um pedaço contíguo) e combina os resultados sem data race (use canais ou `sync`). `workers <= 0` deve ser tratado como 1 e `workers` maior que `len(nums)` deve funcionar. Slice vazio ou nulo devolve 0.''',
   {"go.mod": GOMOD, "solution_test.go": '''
package solution

import "testing"

func TestSumParallel(t *testing.T) {
	n := 1000000
	nums := make([]int, n)
	want := 0
	for i := range nums {
		nums[i] = i + 1
		want += i + 1
	}
	for _, w := range []int{1, 2, 4, 7, 16, 1000, 5000000} {
		if got := SumParallel(nums, w); got != want {
			t.Fatalf("workers=%d got %d want %d", w, got, want)
		}
	}
}

func TestSumParallelEdges(t *testing.T) {
	if SumParallel(nil, 4) != 0 || SumParallel([]int{}, 4) != 0 {
		t.Fatal("vazio deveria dar 0")
	}
	for _, w := range []int{0, -3, 1, 10} {
		if got := SumParallel([]int{5, -2, 10}, w); got != 13 {
			t.Fatalf("workers=%d got %d", w, got)
		}
	}
}
'''},
   '''
package solution

import "sync"

func SumParallel(nums []int, workers int) int {
	if workers <= 0 {
		workers = 1
	}
	if workers > len(nums) {
		workers = len(nums)
	}
	if len(nums) == 0 {
		return 0
	}
	parts := make([]int, workers)
	var wg sync.WaitGroup
	size := (len(nums) + workers - 1) / workers
	for w := 0; w < workers; w++ {
		lo, hi := w*size, (w+1)*size
		if hi > len(nums) {
			hi = len(nums)
		}
		if lo >= hi {
			continue
		}
		wg.Add(1)
		go func(w, lo, hi int) {
			defer wg.Done()
			s := 0
			for _, v := range nums[lo:hi] {
				s += v
			}
			parts[w] = s
		}(w, lo, hi)
	}
	wg.Wait()
	total := 0
	for _, p := range parts {
		total += p
	}
	return total
}
''')

ch("go4_lru", "go", "estruturas de dados", 3,
   '''Em Go, arquivo `solution.go` com `package solution`. Implemente um cache LRU: `type LRU struct{...}`, `func NewLRU(capacity int) *LRU` (se `capacity <= 0`, trate como 1), `func (c *LRU) Get(key string) (int, bool)` (marca como usado), `func (c *LRU) Put(key string, value int)` (insere ou atualiza e marca como usado; ao exceder a capacidade remove o menos recentemente usado) e `func (c *LRU) Len() int`. Use `container/list` ou estrutura própria; Get/Put em O(1).''',
   {"go.mod": GOMOD, "solution_test.go": '''
package solution

import "testing"

func TestLRU(t *testing.T) {
	c := NewLRU(2)
	c.Put("a", 1)
	c.Put("b", 2)
	if v, ok := c.Get("a"); !ok || v != 1 {
		t.Fatal("a")
	}
	c.Put("c", 3)
	if _, ok := c.Get("b"); ok {
		t.Fatal("b deveria ter sido removido")
	}
	if v, ok := c.Get("a"); !ok || v != 1 {
		t.Fatal("a deveria continuar")
	}
	if c.Len() != 2 {
		t.Fatalf("len %d", c.Len())
	}
}

func TestLRUUpdateRefreshes(t *testing.T) {
	c := NewLRU(2)
	c.Put("a", 1)
	c.Put("b", 2)
	c.Put("a", 10)
	c.Put("c", 3)
	if v, ok := c.Get("a"); !ok || v != 10 {
		t.Fatal("a=10")
	}
	if _, ok := c.Get("b"); ok {
		t.Fatal("b removido")
	}
	z := NewLRU(0)
	z.Put("x", 1)
	z.Put("y", 2)
	if z.Len() != 1 {
		t.Fatal("capacidade 0 vira 1")
	}
}

func TestLRUBig(t *testing.T) {
	c := NewLRU(1000)
	for i := 0; i < 200000; i++ {
		c.Put(string(rune('a'+i%26))+string(rune('a'+(i/26)%26))+string(rune('a'+(i/676)%26)), i)
	}
	if c.Len() > 1000 {
		t.Fatal("estourou")
	}
}
'''},
   '''
package solution

import "container/list"

type entry struct {
	key string
	val int
}

type LRU struct {
	cap int
	l   *list.List
	m   map[string]*list.Element
}

func NewLRU(capacity int) *LRU {
	if capacity <= 0 {
		capacity = 1
	}
	return &LRU{cap: capacity, l: list.New(), m: map[string]*list.Element{}}
}

func (c *LRU) Get(key string) (int, bool) {
	if e, ok := c.m[key]; ok {
		c.l.MoveToFront(e)
		return e.Value.(*entry).val, true
	}
	return 0, false
}

func (c *LRU) Put(key string, value int) {
	if e, ok := c.m[key]; ok {
		e.Value.(*entry).val = value
		c.l.MoveToFront(e)
		return
	}
	c.m[key] = c.l.PushFront(&entry{key, value})
	if c.l.Len() > c.cap {
		last := c.l.Back()
		c.l.Remove(last)
		delete(c.m, last.Value.(*entry).key)
	}
}

func (c *LRU) Len() int { return c.l.Len() }
''')

# ------------------------------------------------------------------ JAVA (17)
ch("java1_strings", "java", "strings", 1,
   '''Em Java 17, arquivo `Solution.java` com `public class Solution` (sem `package`, sem `main`) e métodos estáticos: `static boolean isPalindrome(String s)` (ignora tudo que não seja letra ou dígito e ignora maiúsculas/minúsculas; string sem caracteres válidos é palíndromo) e `static String compress(String s)` (compressão por repetição: cada sequência de um mesmo caractere vira o caractere seguido da quantidade, mas a quantidade só aparece se for maior que 1: "aaabcc" vira "a3bc2"; string vazia devolve "").''',
   {"Test.java": '''
public class Test {
    static void check(boolean c, String m) { if (!c) { System.err.println("FALHOU: " + m); System.exit(1); } }
    public static void main(String[] a) {
        check(Solution.isPalindrome("A man, a plan, a canal: Panama"), "panama");
        check(!Solution.isPalindrome("race a car"), "race");
        check(Solution.isPalindrome(""), "vazio");
        check(Solution.isPalindrome(".,!"), "so simbolos");
        check(Solution.isPalindrome("12321"), "digitos");
        check(!Solution.isPalindrome("12345"), "digitos nao");
        check(Solution.compress("aaabcc").equals("a3bc2"), "c1");
        check(Solution.compress("").equals(""), "c2");
        check(Solution.compress("abc").equals("abc"), "c3");
        check(Solution.compress("zzzzzzzzzzzz").equals("z12"), "c4");
        check(Solution.compress("aabbaa").equals("a2b2a2"), "c5");
        System.out.println("OK");
    }
}
'''},
   '''
public class Solution {
    static boolean isPalindrome(String s) {
        StringBuilder b = new StringBuilder();
        for (char c : s.toCharArray()) if (Character.isLetterOrDigit(c)) b.append(Character.toLowerCase(c));
        return b.toString().contentEquals(new StringBuilder(b).reverse());
    }
    static String compress(String s) {
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < s.length(); ) {
            int j = i;
            while (j < s.length() && s.charAt(j) == s.charAt(i)) j++;
            out.append(s.charAt(i));
            if (j - i > 1) out.append(j - i);
            i = j;
        }
        return out.toString();
    }
}
''', file="Solution.java")

ch("java2_topk", "java", "estruturas de dados", 2,
   '''Em Java 17, arquivo `Solution.java` com `public class Solution` (sem `package`, sem `main`) e o método estático `static int[] topK(int[] nums, int k)`: devolve os `k` valores mais frequentes, ordenados por frequência decrescente e, em caso de empate, por valor crescente. Se `k` for maior que a quantidade de valores distintos, devolve todos os distintos. `k <= 0` devolve array vazio. Array vazio devolve array vazio.''',
   {"Test.java": '''
import java.util.Arrays;
public class Test {
    static void check(boolean c, String m) { if (!c) { System.err.println("FALHOU: " + m); System.exit(1); } }
    public static void main(String[] a) {
        check(Arrays.equals(Solution.topK(new int[]{1,1,1,2,2,3}, 2), new int[]{1, 2}), "t1");
        check(Arrays.equals(Solution.topK(new int[]{4,4,5,5,6}, 2), new int[]{4, 5}), "desempate por valor");
        check(Arrays.equals(Solution.topK(new int[]{3,3,-1,-1,9}, 3), new int[]{-1, 3, 9}), "negativos");
        check(Arrays.equals(Solution.topK(new int[]{7,7,8}, 10), new int[]{7, 8}), "k grande");
        check(Solution.topK(new int[]{1,2}, 0).length == 0, "k zero");
        check(Solution.topK(new int[]{}, 3).length == 0, "vazio");
        System.out.println("OK");
    }
}
'''},
   '''
import java.util.*;

public class Solution {
    static int[] topK(int[] nums, int k) {
        if (k <= 0) return new int[0];
        Map<Integer, Integer> f = new HashMap<>();
        for (int n : nums) f.merge(n, 1, Integer::sum);
        List<Integer> keys = new ArrayList<>(f.keySet());
        keys.sort((x, y) -> f.get(y) != f.get(x).intValue() ? f.get(y) - f.get(x) : Integer.compare(x, y));
        int m = Math.min(k, keys.size());
        int[] out = new int[m];
        for (int i = 0; i < m; i++) out[i] = keys.get(i);
        return out;
    }
}
''', file="Solution.java")

ch("java3_account", "java", "orientação a objetos", 2,
   '''Em Java 17, arquivo `BankAccount.java` com `public class BankAccount` (sem `package`, sem `main`). Construtor `BankAccount(double initialBalance)` (saldo inicial negativo lança `IllegalArgumentException`), `double getBalance()`, `void deposit(double amount)` (valor `<= 0` lança `IllegalArgumentException`), `void withdraw(double amount)` (valor `<= 0` lança `IllegalArgumentException`; saldo insuficiente lança `IllegalStateException` e **não altera o saldo**) e `void transfer(BankAccount to, double amount)` que retira desta conta e deposita na outra; se falhar por saldo insuficiente nada muda em nenhuma das contas. Transferir para a própria conta lança `IllegalArgumentException`.''',
   {"Test.java": '''
public class Test {
    static void check(boolean c, String m) { if (!c) { System.err.println("FALHOU: " + m); System.exit(1); } }
    interface Thrower { void run() throws Exception; }
    static boolean throwsType(Thrower t, Class<?> type) {
        try { t.run(); } catch (Exception e) { return type.isInstance(e); }
        return false;
    }
    public static void main(String[] a) {
        BankAccount x = new BankAccount(100), y = new BankAccount(0);
        x.deposit(50); check(x.getBalance() == 150, "deposit");
        x.withdraw(30); check(x.getBalance() == 120, "withdraw");
        check(throwsType(() -> x.withdraw(1000), IllegalStateException.class), "insuficiente");
        check(x.getBalance() == 120, "saldo intacto");
        check(throwsType(() -> x.deposit(0), IllegalArgumentException.class), "deposit 0");
        check(throwsType(() -> x.withdraw(-5), IllegalArgumentException.class), "withdraw neg");
        check(throwsType(() -> new BankAccount(-1), IllegalArgumentException.class), "ctor neg");
        x.transfer(y, 20); check(x.getBalance() == 100 && y.getBalance() == 20, "transfer");
        check(throwsType(() -> x.transfer(y, 500), IllegalStateException.class), "transfer insuficiente");
        check(x.getBalance() == 100 && y.getBalance() == 20, "nada muda");
        check(throwsType(() -> x.transfer(x, 1), IllegalArgumentException.class), "mesma conta");
        System.out.println("OK");
    }
}
'''},
   '''
public class BankAccount {
    private double balance;
    public BankAccount(double initialBalance) {
        if (initialBalance < 0) throw new IllegalArgumentException("negative");
        balance = initialBalance;
    }
    public double getBalance() { return balance; }
    public void deposit(double amount) {
        if (amount <= 0) throw new IllegalArgumentException("amount");
        balance += amount;
    }
    public void withdraw(double amount) {
        if (amount <= 0) throw new IllegalArgumentException("amount");
        if (amount > balance) throw new IllegalStateException("insufficient");
        balance -= amount;
    }
    public void transfer(BankAccount to, double amount) {
        if (to == this) throw new IllegalArgumentException("same account");
        withdraw(amount);
        to.deposit(amount);
    }
}
''', file="BankAccount.java")

ch("java4_counter", "java", "concorrência", 3,
   '''Em Java 17, arquivo `Counter.java` com `public class Counter` (sem `package`, sem `main`): contador **seguro para várias threads** com `void increment()`, `void add(int delta)`, `long get()` e `void reset()`. Nenhuma atualização pode ser perdida mesmo com várias threads incrementando ao mesmo tempo.''',
   {"Test.java": '''
public class Test {
    static void check(boolean c, String m) { if (!c) { System.err.println("FALHOU: " + m); System.exit(1); } }
    public static void main(String[] a) throws Exception {
        Counter c = new Counter();
        Thread[] ts = new Thread[8];
        for (int i = 0; i < ts.length; i++) {
            ts[i] = new Thread(() -> { for (int k = 0; k < 200000; k++) c.increment(); });
            ts[i].start();
        }
        for (Thread t : ts) t.join();
        check(c.get() == 1600000L, "perdeu atualizacoes: " + c.get());
        c.add(-100); check(c.get() == 1599900L, "add");
        c.reset(); check(c.get() == 0, "reset");
        Thread[] us = new Thread[4];
        for (int i = 0; i < us.length; i++) { us[i] = new Thread(() -> { for (int k = 0; k < 100000; k++) c.add(2); }); us[i].start(); }
        for (Thread t : us) t.join();
        check(c.get() == 800000L, "add concorrente: " + c.get());
        System.out.println("OK");
    }
}
'''},
   '''
import java.util.concurrent.atomic.AtomicLong;

public class Counter {
    private final AtomicLong v = new AtomicLong();
    public void increment() { v.incrementAndGet(); }
    public void add(int delta) { v.addAndGet(delta); }
    public long get() { return v.get(); }
    public void reset() { v.set(0); }
}
''', file="Counter.java")

# ------------------------------------------------------------------ SQL (SQLite)
EMP_SETUP = """
CREATE TABLE employees(id INTEGER PRIMARY KEY, name TEXT, dept TEXT, salary INTEGER);
INSERT INTO employees VALUES (1,'Ana','TI',5000),(2,'Bia','TI',7000),(3,'Caio','RH',4000),(4,'Duda','RH',4400),(5,'Edu','FIN',9000),(6,'Fabi','TI',6000),(7,'Gabi','RH',4400);
"""
ORD_SETUP = """
CREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE orders(id INTEGER PRIMARY KEY, customer_id INTEGER, total INTEGER, created_at TEXT);
INSERT INTO customers VALUES (1,'Ana'),(2,'Bruno'),(3,'Carla'),(4,'Davi');
INSERT INTO orders VALUES (1,1,100,'2026-01-01'),(2,1,50,'2026-01-03'),(3,3,70,'2026-01-02'),(4,1,25,'2026-01-03'),(5,3,30,'2026-01-05');
"""


def sql_test(setup, expected):
    return {"test.py": f'''
import sqlite3, sys
SETUP = {setup!r}
EXPECTED = {expected!r}
q = open("solution.sql", encoding="utf-8").read().strip().rstrip(";")
db = sqlite3.connect(":memory:")
db.executescript(SETUP)
rows = [tuple(round(x, 2) if isinstance(x, float) else x for x in r) for r in db.execute(q).fetchall()]
if rows != EXPECTED:
    print("esperado:", EXPECTED); print("obtido:  ", rows); sys.exit(1)
print("OK")
'''}


ch("sql1_avg", "sql", "bancos de dados", 1,
   '''SQLite. Tabela `employees(id, name, dept, salary)`. Escreva UMA consulta SELECT (arquivo `solution.sql`, sem ponto e vírgula extra, sem comandos de criação) que devolva, para cada departamento com **pelo menos 2 funcionários**, as colunas `dept` e `avg_salary` (média arredondada para 2 casas, nessa ordem), ordenado por `avg_salary` decrescente.''',
   sql_test(EMP_SETUP, [("TI", 6000.0), ("RH", 4266.67)]),
   "SELECT dept, ROUND(AVG(salary), 2) AS avg_salary FROM employees GROUP BY dept HAVING COUNT(*) >= 2 ORDER BY avg_salary DESC;")

ch("sql2_noorders", "sql", "bancos de dados", 2,
   '''SQLite. Tabelas `customers(id, name)` e `orders(id, customer_id, total, created_at)`. Escreva UMA consulta SELECT (arquivo `solution.sql`) que devolva `id` e `name` (nessa ordem) dos clientes que **nunca fizeram pedido**, ordenados por `name`.''',
   sql_test(ORD_SETUP, [(2, "Bruno"), (4, "Davi")]),
   "SELECT c.id, c.name FROM customers c LEFT JOIN orders o ON o.customer_id = c.id WHERE o.id IS NULL ORDER BY c.name;")

ch("sql3_topper", "sql", "bancos de dados", 2,
   '''SQLite. Tabela `employees(id, name, dept, salary)`. Escreva UMA consulta SELECT (arquivo `solution.sql`) que devolva, para cada departamento, o funcionário de **maior salário** (em caso de empate, o de menor `id`), com as colunas `dept`, `name`, `salary` (nessa ordem), ordenado por `dept`.''',
   sql_test(EMP_SETUP, [("FIN", "Edu", 9000), ("RH", "Duda", 4400), ("TI", "Bia", 7000)]),
   """SELECT dept, name, salary FROM (SELECT dept, name, salary, ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC, id ASC) rn FROM employees) WHERE rn = 1 ORDER BY dept;""")

ch("sql4_running", "sql", "bancos de dados", 3,
   '''SQLite 3.25+. Tabela `orders(id, customer_id, total, created_at)`. Escreva UMA consulta SELECT (arquivo `solution.sql`) com as colunas `customer_id`, `id`, `total`, `running_total` (nessa ordem), onde `running_total` é a soma acumulada de `total` **por cliente**, na ordem `created_at` e, em empate de data, por `id` (use função de janela). O resultado vem ordenado por `customer_id`, `created_at`, `id`.''',
   sql_test(ORD_SETUP, [(1, 1, 100, 100), (1, 2, 50, 150), (1, 4, 25, 175), (3, 3, 70, 70), (3, 5, 30, 100)]),
   """SELECT customer_id, id, total, SUM(total) OVER (PARTITION BY customer_id ORDER BY created_at, id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total FROM orders ORDER BY customer_id, created_at, id;""")
