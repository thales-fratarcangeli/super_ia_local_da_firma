"""Bateria multilinguagem em sequência (por nível de dificuldade). Uso:
  python harness/run_poly.py <nome> [modelo] [--reference] [--lang c,go] [--level 1,2] [--only go2] [--n 1] [--temp 0.4]
Linguagens: python, js (node), c (gcc), go, java (javac 17), sql (SQLite). Cada desafio: 1 arquivo entregue pela IA, testes escondidos."""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "suite"))
import lib  # noqa: E402
from poly import CH  # noqa: E402

ORDEM_LANG = ["python", "js", "c", "go", "java", "sql"]
CODE_RE = re.compile(r"```[A-Za-z0-9+#_-]*[ \t]*\n(.*?)```", re.S)
OPEN_RE = re.compile(r"```[A-Za-z0-9+#_-]*[ \t]*\n(.*)\Z", re.S)
WIN = os.name == "nt"

ap = argparse.ArgumentParser()
ap.add_argument("name")
ap.add_argument("model", nargs="?", default="qwen3:8b")
ap.add_argument("--reference", action="store_true")
ap.add_argument("--lang", default="")
ap.add_argument("--level", default="")
ap.add_argument("--only", default="")
ap.add_argument("--n", type=int, default=1)
ap.add_argument("--temp", type=float, default=0.4)
ap.add_argument("--rag", action="store_true")
ap.add_argument("--k", type=int, default=3)
ap.add_argument("--budget", type=int, default=1400)
args = ap.parse_args()

run = lib.ROOT / "runs" / "poly" / args.name
retriever = None
if args.rag:
    sys.path.insert(0, str(lib.ROOT / "rag"))
    from rag import Retriever  # noqa: E402
    retriever = Retriever(k=args.k, budget_chars=args.budget)


def extract(text):
    m = CODE_RE.search(text) or OPEN_RE.search(text)
    return m.group(1) if m else text


def sh(cmd, cwd, timeout=240, env=None):
    e = dict(os.environ, **(env or {}))
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=e, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout + p.stderr)[-600:]


def run_tests(c, d):
    lang = c["lang"]
    try:
        if lang == "python":
            return sh([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-W", "ignore", "--tb=line", "--rootdir", str(d), "test_solution.py"], d)
        if lang == "js":
            return sh(["node", "test.js"], d)
        if lang == "sql":
            return sh([sys.executable, "test.py"], d)
        if lang == "c":
            exe = "t.exe" if WIN else "t"
            rc, out = sh(["gcc", "-std=c11", "-O0", "-o", exe, "test.c", "-lm"], d)
            if rc != 0:
                return rc, "COMPILAÇÃO: " + out
            return sh([str(d / exe)], d, timeout=60)
        if lang == "go":
            return sh(["go", "test", "./..."], d, timeout=300, env={"GOTOOLCHAIN": "local", "GOFLAGS": "-mod=mod"})
        if lang == "java":
            files = [os.path.basename(f) for f in glob.glob(str(d / "*.java"))]
            rc, out = sh(["javac", "-encoding", "UTF-8"] + files, d)
            if rc != 0:
                return rc, "COMPILAÇÃO: " + out
            return sh(["java", "-cp", str(d), "Test"], d, timeout=120)
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT"
    except FileNotFoundError as e:
        return 127, f"ferramenta ausente: {e}"
    return 1, "linguagem desconhecida"


sel = [c for c in CH if (not args.lang or c["lang"] in args.lang.split(",")) and (not args.level or str(c["level"]) in args.level.split(","))
       and (not args.only or any(c["id"].startswith(o) for o in args.only.split(",")))]
sel.sort(key=lambda c: (c["level"], ORDEM_LANG.index(c["lang"]), c["id"]))
results = []
for c in sel:
    for k in range(args.n):
        d = run / c["id"] / f"s{k}"
        d.mkdir(parents=True, exist_ok=True)
        for fname, content in c["test"].items():
            (d / fname).write_text(content, encoding="utf-8")
        t0 = time.time()
        gen = 0
        if args.reference:
            code = c["ref"]
        else:
            prompt = c["prompt"] + f"\n\nResponda SOMENTE com o código completo do arquivo `{c['file']}` em um único bloco de código, sem explicações e sem testes."
            msgs = [{"role": "user", "content": prompt}]
            if retriever:
                sysmsg, hits = retriever.system_message(c["prompt"])
                if sysmsg:
                    msgs.insert(0, {"role": "system", "content": sysmsg})
            text, meta = lib.chat(msgs, model=args.model, temperature=args.temp, num_ctx=6144, num_predict=3000)
            (d / "response.txt").write_text(text, encoding="utf-8")
            code, gen = extract(text), meta["seconds"]
        (d / c["file"]).write_text(code, encoding="utf-8")
        rc, out = run_tests(c, d)
        ok = rc == 0
        results.append({"id": c["id"], "lang": c["lang"], "area": c["area"], "level": c["level"], "sample": k, "ok": ok,
                        "gen_seconds": gen, "tail": "" if ok else out[-500:]})
        print(f"[N{c['level']}] {c['id']:<16} {c['lang']:<7} {c['area']:<22} s{k}: {'OK  ' if ok else 'FALHA'} gen={gen}s", flush=True)


def taxa(items):
    return round(sum(r["ok"] for r in items) / max(1, len(items)), 3)


por_lang = {l: taxa([r for r in results if r["lang"] == l]) for l in ORDEM_LANG if any(r["lang"] == l for r in results)}
por_nivel = {str(n): taxa([r for r in results if r["level"] == n]) for n in (1, 2, 3) if any(r["level"] == n for r in results)}
summary = {"name": args.name, "model": args.model, "rag": args.rag, "pass_rate": taxa(results), "total": len(results),
           "por_linguagem": por_lang, "por_nivel": por_nivel, "results": results}
run.mkdir(parents=True, exist_ok=True)
(run / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"== {args.name} [{args.model}{' +RAG' if args.rag else ''}]: {sum(r['ok'] for r in results)}/{len(results)} ({summary['pass_rate']:.0%}) | por linguagem {por_lang} | por nível {por_nivel}")
