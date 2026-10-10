"""Dataset multilinguagem verificado por execução (professor: 32B). Linguagens: js, go, c, java, sql.
Cada exemplo mantido: os testes gerados PASSAM na solução gerada e FALHAM numa solução vazia; não se parece com a bateria de avaliação.
Uso: python3 gen_poly_dataset.py <lang> <saida.jsonl> [--n 150] [--workers 3] [--model qwen2.5-coder:32b] [--start 0]"""
import argparse
import json
import os
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
from poly import CH  # noqa: E402

GOMOD = "module solution\n\ngo 1.21\n"
LANGS = {
    "js": dict(file="solution.js", test="test.js", fence="javascript", run="node test.js",
               guide="JavaScript (Node, CommonJS, `module.exports = {...}`)",
               testfmt="`test.js` usa `require('./solution')` e o módulo `assert`; termina com `console.log('OK')`; qualquer falha deve fazer o processo sair com código diferente de 0",
               topics=["manipulação de strings", "arrays e objetos (agrupar, achatar, deduplicar)", "funções assíncronas com Promises e async/await", "classe com estado (fila, pilha, cache)",
                       "parsing de formatos simples (CSV, query string, duração)", "datas e formatação", "validação de dados", "algoritmos clássicos (busca, ordenação, grafos)",
                       "funções de ordem superior (debounce, memoize, compose, pipe)", "regex e templates", "estruturas de dados (heap, trie, lista ligada)", "utilitários de URL e caminhos"]),
    "go": dict(file="solution.go", test="solution_test.go", fence="go", run="go test ./...",
               guide="Go (arquivo `solution.go` com `package solution`)",
               testfmt="`solution_test.go` com `package solution` usando o pacote `testing` (funções `TestXxx`); use `t.Fatalf` para falhar",
               topics=["strings e runas (Unicode)", "slices e maps (agrupar, ordenar, deduplicar)", "erros idiomáticos (error, errors.New, fmt.Errorf)", "goroutines, canais e sync.WaitGroup/Mutex",
                       "estruturas de dados (pilha, fila, LRU, heap com container/heap)", "parsing de texto simples", "interfaces e structs com métodos", "algoritmos clássicos",
                       "matemática e overflow de inteiros", "worker pool e pipelines", "datas com time", "validação de entrada"]),
    "c": dict(file="solution.c", test="test.c", fence="c", run="gcc test.c && ./t",
              guide="C (C11, apenas biblioteca padrão, **sem função main**)",
              testfmt="`test.c` começa com os includes necessários e `#include \"solution.c\"`, tem a função `main` com `assert` (assert.h), imprime `OK` e devolve 0",
              topics=["manipulação de bits", "strings in-place (trim, reverse, split manual)", "estruturas de dados com malloc/free (pilha, fila, lista ligada)", "parsing de números com detecção de overflow",
                      "arrays e ordenação (qsort, busca binária)", "buffers e memória (memcpy, memmove)", "matemática inteira (gcd, primos, potência modular)", "máquina de estados simples",
                      "codificação (base64, hex, run-length)", "hash simples (djb2, FNV) e checksums", "matrizes", "tabela hash simples com encadeamento"]),
    "java": dict(file="Solution.java", test="Test.java", fence="java", run="javac *.java && java Test",
                 guide="Java 17 (arquivo `Solution.java` com `public class Solution`, sem `package`, sem `main`, métodos `static`)",
                 testfmt="`Test.java` com `public class Test` e `main` que chama `Solution` e verifica os resultados; em qualquer falha chama `System.exit(1)`; no fim imprime `OK`",
                 topics=["strings e StringBuilder", "coleções (List, Map, Set, Deque)", "streams e lambdas", "algoritmos clássicos", "exceções (IllegalArgumentException, IllegalStateException)",
                         "datas com java.time", "recursão e programação dinâmica", "ordenação com Comparator", "parsing simples", "matrizes e grades", "validação de entradas", "BigInteger/BigDecimal"]),
    "sql": dict(file="solution.sql", test="test.py", fence="sql", run="python test.py",
                guide="SQLite (arquivo `solution.sql` com UMA consulta SELECT, sem comandos de criação)",
                testfmt="`test.py` (Python) define `SETUP` (script com CREATE TABLE e INSERT), `EXPECTED` (lista de tuplas), lê `solution.sql`, executa a consulta com `sqlite3` em memória e compara as linhas; imprime `OK` ou sai com código 1",
                topics=["agregações com GROUP BY e HAVING", "JOINs (INNER, LEFT) e anti-join", "subconsultas e EXISTS", "funções de janela (ROW_NUMBER, RANK, SUM OVER)", "datas e strings no SQLite",
                        "ranking e top-N por grupo", "pivot com CASE WHEN", "CTEs (WITH) e recursão", "deduplicação", "médias móveis e acumulados", "contagens condicionais", "auto-junção"]),
}
TWISTS = ["com casos de borda (vazio, nulo, limites)", "com validação de entradas inválidas", "com desempate determinístico", "sem efeitos colaterais na entrada",
          "com duas funções que cooperam", "com valores padrão e parâmetros opcionais", "exigindo eficiência razoável", "com tratamento explícito de erros"]

META = """Você cria desafios de programação para treinar um modelo. Linguagem: {guide}. Tema: {topic}. Particularidade: {twist}. Semente: {seed}.
Crie UM desafio NOVO e original. Responda exatamente com 3 blocos, nesta ordem, sem nenhum texto fora deles:
### PROMPT
(enunciado em português, preciso: nomes exatos, assinaturas completas, tipos, erros/exceções esperados, formato exato do retorno e pelo menos um exemplo concreto de entrada e saída; 3 a 7 frases; deve dizer qual arquivo entregar)
### TEST
```{fence}
(arquivo de testes: {testfmt}; 4 a 10 verificações cobrindo caso normal, bordas e erros descritos)
```
### SOLUTION
```{fence}
(implementação correta e completa do arquivo `{file}`)
```"""
BLOCK = re.compile(r"### PROMPT\s*\n(.*?)### TEST\s*\n```[A-Za-z0-9+#]*\n(.*?)```\s*### SOLUTION\s*\n```[A-Za-z0-9+#]*\n(.*?)```", re.S)
SUFFIX = "\n\nResponda SOMENTE com o código completo do arquivo `{file}` em um único bloco de código, sem explicações e sem testes."
lock = threading.Lock()
WIN = os.name == "nt"

GENERIC = {"main", "Test", "Solution", "String", "List", "Map", "int", "get", "put", "add", "set", "run", "OK", "assert", "require", "solution", "package"}
eval_idents = set()
for c in CH:
    eval_idents |= set(re.findall(r"\b([A-Za-z_][A-Za-z0-9_]{3,})\s*\(", c["ref"]))
eval_idents -= GENERIC
eval_prompts = [c["prompt"] for c in CH]


def run_case(lang, solution_code, test_code, timeout=120):
    """Roda os testes numa pasta temporária. Devolve True se passou (código de saída 0)."""
    L = LANGS[lang]
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / L["file"]).write_text(solution_code, encoding="utf-8")
        (d / L["test"]).write_text(test_code, encoding="utf-8")
        try:
            if lang == "js":
                return subprocess.run(["node", "test.js"], cwd=d, capture_output=True, timeout=timeout).returncode == 0
            if lang == "sql":
                return subprocess.run([sys.executable, "test.py"], cwd=d, capture_output=True, timeout=timeout).returncode == 0
            if lang == "c":
                if subprocess.run(["gcc", "-std=c11", "-O0", "-o", "t", "test.c", "-lm"], cwd=d, capture_output=True, timeout=timeout).returncode != 0:
                    return False
                return subprocess.run([str(d / ("t.exe" if WIN else "t"))], cwd=d, capture_output=True, timeout=30).returncode == 0
            if lang == "go":
                (d / "go.mod").write_text(GOMOD, encoding="utf-8")
                return subprocess.run(["go", "test", "./..."], cwd=d, capture_output=True, timeout=300,
                                      env=dict(os.environ, GOTOOLCHAIN="local", GOFLAGS="-mod=mod")).returncode == 0
            if lang == "java":
                if subprocess.run(["javac", "-encoding", "UTF-8", L["file"], L["test"]], cwd=d, capture_output=True, timeout=timeout).returncode != 0:
                    return False
                return subprocess.run(["java", "-cp", str(d), "Test"], cwd=d, capture_output=True, timeout=60).returncode == 0
        except subprocess.TimeoutExpired:
            return False
    return False


def one(i, args, kept, out, stats):
    L = LANGS[args.lang]
    rnd = random.Random(f"{args.lang}{i}")
    try:
        text, _ = lib.chat([{"role": "user", "content": META.format(guide=L["guide"], topic=rnd.choice(L["topics"]), twist=rnd.choice(TWISTS), seed=i,
                                                                   fence=L["fence"], testfmt=L["testfmt"], file=L["file"])}],
                           model=args.model, temperature=0.8, num_ctx=6144, num_predict=3000)
    except Exception:  # noqa: BLE001
        stats["erro_api"] += 1
        return
    m = BLOCK.search(text)
    if not m:
        stats["sem_formato"] += 1
        return
    prompt, test, sol = m.group(1).strip(), m.group(2), m.group(3)
    idents = set(re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)", prompt))
    if idents & eval_idents or any(SequenceMatcher(None, prompt, e).ratio() > 0.55 for e in eval_prompts):
        stats["parece_avaliacao"] += 1
        return
    if not run_case(args.lang, sol, test):
        stats["testes_nao_passam"] += 1
        return
    if run_case(args.lang, "", test):
        stats["teste_trivial"] += 1
        return
    with lock:
        if any(SequenceMatcher(None, prompt, k).ratio() > 0.8 for k in kept):
            stats["duplicado"] += 1
            return
        kept.append(prompt)
        with open(out, "a", encoding="utf-8") as f:
            f.write(json.dumps({"prompt": prompt + SUFFIX.format(file=L["file"]), "completion": f"```{L['fence']}\n{sol.strip()}\n```",
                                "lang": args.lang, "test": test}, ensure_ascii=False) + "\n")
        stats["mantidos"] += 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("lang", choices=list(LANGS))
    ap.add_argument("out")
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--model", default="qwen2.5-coder:32b")
    ap.add_argument("--start", type=int, default=0)
    args = ap.parse_args()
    out = Path(args.out)
    kept = [json.loads(l)["prompt"] for l in out.read_text(encoding="utf-8").splitlines()] if out.exists() else []
    stats = {k: 0 for k in ["mantidos", "erro_api", "sem_formato", "parece_avaliacao", "testes_nao_passam", "teste_trivial", "duplicado"]}
    done = [0]

    def wrapped(i):
        one(i, args, kept, out, stats)
        done[0] += 1
        if done[0] % 10 == 0:
            print(f"[{args.lang} {done[0]}/{args.n}] {stats}", flush=True)

    with ThreadPoolExecutor(args.workers) as ex:
        list(ex.map(wrapped, range(args.start, args.start + args.n)))
    print("FIM", args.lang, stats, flush=True)
