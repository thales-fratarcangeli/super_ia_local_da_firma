"""Gera dataset de treino com o professor (32B): tarefa + testes + solução, verificados por execução.
Cada exemplo mantido: os testes gerados PASSAM na solução gerada e FALHAM numa solução vazia (testes não triviais).
Não usa nenhuma das tarefas da suíte de avaliação (filtro por nomes e por similaridade).
Uso: python harness/gen_dataset.py <saida.jsonl> [--n 300] [--workers 4] [--model qwen2.5-coder:32b]"""
import argparse
import json
import random
import re
import subprocess
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "suite"))
import lib  # noqa: E402
from tasks import TASKS  # noqa: E402

FORMAT = "\n\nResponda SOMENTE com o código completo do arquivo `solution.py` em um único bloco ```python, sem explicações e sem testes."

TOPICS = [
    "função pura de texto (normalização, parsing, formatação)", "função pura de listas/dicionários (agrupar, achatar, deduplicar, ordenar)",
    "classe de estrutura de dados (fila, pilha, heap, trie, cache, contador)", "algoritmo clássico (busca, ordenação, grafo, programação dinâmica)",
    "validação de dados com Pydantic v2", "repositório com sqlite3 (CRUD parametrizado)", "modelos SQLAlchemy 2.0 com relationship, FK e cascade",
    "FastAPI: rota com autenticação por token Bearer e erros 401/403", "FastAPI: CRUD em memória com 201/204/404/422", "FastAPI: paginação e filtros com Query validada",
    "JWT com PyJWT (criar, validar, expiração, claims)", "hash de senha (bcrypt ou PBKDF2) e verificação segura", "parser/serializador (CSV simples, query string, ini, duração '1h30m')",
    "datas e tempo com datetime (intervalos, janelas, fusos UTC)", "rate limiter, retry com backoff ou circuit breaker com relógio injetado", "máquina de estados ou workflow com transições válidas",
    "expressões e tokenização (calculadora, parser de expressão simples)", "manipulação de arquivos/paths com pathlib em diretório temporário", "decorators e context managers (cache, timer, retry)",
    "dataclasses e enums com validação", "permissões e papéis (RBAC) com regras 404/403", "processamento de eventos/logs (agregação, janelas, top-N)",
]
TOPICS += [t for t in TOPICS if any(w in t for w in ("FastAPI", "SQLAlchemy", "JWT", "hash de senha", "Pydantic", "sqlite3", "permissões"))] * 2  # mais peso para web/db/auth
TWISTS = ["com casos de borda (vazio, None, limites)", "com validação e ValueError em entradas inválidas", "com ordenação determinística e desempate", "sem alterar a entrada (sem efeitos colaterais)",
          "com tratamento de erro que devolve None/False em vez de levantar", "com duas funções que cooperam entre si", "usando uma classe com estado", "com parâmetros opcionais com valor padrão"]

META = """Você cria exercícios de programação Python 3.12 para treinar um modelo. Tema: {topic}. Particularidade: {twist}. Semente de variação: {seed}.
Crie UM exercício NOVO e original (não use slugify, paginate, LRU, JWT básico, token bucket, toposort, merge de intervalos).
Responda exatamente com 3 blocos, nesta ordem, sem texto fora deles:

### PROMPT
(enunciado em português, preciso: nomes exatos de funções/classes com assinatura completa e valores padrão, erros que devem ser levantados (tipo da exceção), formato exato do retorno e **pelo menos um exemplo concreto de entrada e saída**; 3 a 7 frases; o código vai em um único arquivo `solution.py`)
### TEST
```python
(testes pytest que fazem `from solution import ...`; 3 a 8 testes cobrindo caso normal, bordas e erros descritos no enunciado)
```
### SOLUTION
```python
(implementação correta e completa de solution.py)
```"""

BLOCK = re.compile(r"### PROMPT\s*\n(.*?)### TEST\s*\n```(?:python|py)?\n(.*?)```\s*### SOLUTION\s*\n```(?:python|py)?\n(.*?)```", re.S)
lock = threading.Lock()
import ast  # noqa: E402

eval_names = set()  # nomes de funções/classes públicas das soluções de referência da suíte de avaliação
for t in TASKS:
    for node in ast.walk(ast.parse(t["ref"])):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and not node.name.startswith("_") and node.name not in ("Base", "User", "Project", "Task", "get", "put", "add", "list", "delete", "allow", "me", "health", "items", "auth", "check_username", "set_done"):
            eval_names.add(node.name)
eval_prompts = [t["prompt"] for t in TASKS]


def run_pytest(code, test):
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "solution.py").write_text(code, encoding="utf-8")
        (d / "test_solution.py").write_text(test, encoding="utf-8")
        try:
            p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-W", "ignore", "--tb=no"],
                               cwd=d, capture_output=True, text=True, timeout=60)
        except subprocess.TimeoutExpired:
            return 0, 1
        m, f = re.search(r"(\d+) passed", p.stdout), re.search(r"(\d+) (failed|error)", p.stdout)
        return (int(m.group(1)) if m else 0), (int(f.group(1)) if f else 0)


def one(i, args, kept_prompts, out_path, stats):
    rnd = random.Random(i)
    topic, twist = rnd.choice(TOPICS), rnd.choice(TWISTS)
    try:
        text, _ = lib.chat([{"role": "user", "content": META.format(topic=topic, twist=twist, seed=i)}], model=args.model,
                           temperature=0.8, num_ctx=6144, num_predict=2500)
    except Exception as e:  # noqa: BLE001
        stats["erro_api"] += 1
        return
    m = BLOCK.search(text)
    if not m:
        stats["sem_formato"] += 1
        return
    prompt, test, sol = m.group(1).strip(), m.group(2), m.group(3)
    names = set(re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)", prompt))
    if names & eval_names or any(SequenceMatcher(None, prompt, e).ratio() > 0.6 for e in eval_prompts):
        stats["parece_avaliacao"] += 1
        return
    passed, failed = run_pytest(sol, test)
    if failed or passed < 3:
        stats["testes_nao_passam"] += 1
        return
    p_stub, _ = run_pytest("", test)  # solução vazia não pode passar nos testes
    if p_stub:
        stats["teste_trivial"] += 1
        return
    with lock:
        if any(SequenceMatcher(None, prompt, k).ratio() > 0.8 for k in kept_prompts):
            stats["duplicado"] += 1
            return
        kept_prompts.append(prompt)
        with open(out_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"prompt": prompt + FORMAT, "completion": f"```python\n{sol.strip()}\n```", "test": test,
                                "topic": topic, "tests_passed": passed}, ensure_ascii=False) + "\n")
        stats["mantidos"] += 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--model", default="qwen2.5-coder:32b")
    ap.add_argument("--start", type=int, default=0)
    args = ap.parse_args()
    out = Path(args.out)
    kept = [json.loads(l)["prompt"] for l in out.read_text(encoding="utf-8").splitlines()] if out.exists() else []
    stats = {k: 0 for k in ["mantidos", "erro_api", "sem_formato", "parece_avaliacao", "testes_nao_passam", "teste_trivial", "duplicado"]}
    stats["mantidos"] = 0
    done = [0]

    def wrapped(i):
        one(i, args, kept, out, stats)
        done[0] += 1
        if done[0] % 10 == 0:
            print(f"[{done[0]}/{args.n}] {stats}", flush=True)

    with ThreadPoolExecutor(args.workers) as ex:
        list(ex.map(wrapped, range(args.start, args.start + args.n)))
    print("FIM", stats, flush=True)
