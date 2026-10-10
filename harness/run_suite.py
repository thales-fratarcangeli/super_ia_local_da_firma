"""Suíte rápida. Uso:
  python harness/run_suite.py <nome_da_execução> [modelo|--reference] [--only t01,t05] [--n 1]
Cada tarefa: 1 geração (mesmo prompt de sempre + só a instrução de formato), 1 arquivo solution.py, testes escondidos.
--reference valida os testes contra as soluções de referência (tem que dar tudo verde)."""
import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "suite"))
import lib  # noqa: E402
import os  # noqa: E402
if "--suite" in sys.argv and sys.argv[sys.argv.index("--suite") + 1] == "heldout":
    from heldout import TASKS  # noqa: E402
else:
    from tasks import TASKS  # noqa: E402

FORMAT = "\n\nResponda SOMENTE com o código completo do arquivo `solution.py` em um único bloco ```python, sem explicações e sem testes."
CODE_RE = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.S)

ap = argparse.ArgumentParser()
ap.add_argument("name")
ap.add_argument("model", nargs="?", default="qwen3:8b")
ap.add_argument("--only", default="")
ap.add_argument("--suite", default="dev", help="dev | heldout")
ap.add_argument("--reference", action="store_true")
ap.add_argument("--rag", action="store_true", help="injeta notas do RAG numa mensagem de sistema (o prompt do usuário não muda)")
ap.add_argument("--temp", type=float, default=0.1)
ap.add_argument("--k", type=int, default=3)
ap.add_argument("--budget", type=int, default=1400)
ap.add_argument("--n", type=int, default=1, help="amostras por tarefa (pass@1 médio)")
args = ap.parse_args()
if args.reference:
    args.model = "--reference"

run = lib.ROOT / "runs" / "suite" / args.name
(run / "tests").mkdir(parents=True, exist_ok=True)
only = set(args.only.split(",")) if args.only else None
results = []
retriever = None
if args.rag:
    sys.path.insert(0, str(lib.ROOT / "rag"))
    from rag import Retriever  # noqa: E402
    retriever = Retriever(k=args.k, budget_chars=args.budget)


def extract(text):
    m = CODE_RE.search(text)
    if m:
        return m.group(1)
    m = re.search(r"```(?:python|py)?\s*\n(.*)\Z", text, re.S)  # bloco sem fechamento (cortado)
    return m.group(1) if m else text


for t in TASKS:
    if only and not any(t["id"].startswith(o) for o in only):
        continue
    test_file = run / "tests" / f"test_{t['id']}.py"
    test_file.write_text(t["test"], encoding="utf-8")
    for k in range(args.n):
        d = run / t["id"] / f"s{k}"
        d.mkdir(parents=True, exist_ok=True)
        t0 = time.time()
        if args.model == "--reference":
            code, gen = t["ref"], 0
        else:
            msgs = [{"role": "user", "content": t["prompt"] + FORMAT}]
            rag_chars = 0
            if retriever:
                sysmsg, hits = retriever.system_message(t["prompt"])
                if sysmsg:
                    msgs.insert(0, {"role": "system", "content": sysmsg})
                    rag_chars = len(sysmsg)
                    (d / "rag_hits.json").write_text(json.dumps(hits, ensure_ascii=False, indent=1), encoding="utf-8")
            text, meta = lib.chat(msgs, model=args.model,
                                  temperature=args.temp, num_ctx=4096, num_predict=2500)
            (d / "response.txt").write_text(text, encoding="utf-8")
            code, gen = extract(text), meta["seconds"]
        (d / "solution.py").write_text(code, encoding="utf-8")
        try:
            p = subprocess.run([sys.executable, "-m", "pytest", str(test_file), "-q", "-p", "no:cacheprovider",
                                "--rootdir", str(d), "--tb=line", "-W", "ignore"],
                               cwd=d, capture_output=True, text=True, timeout=120)
            out = p.stdout
        except subprocess.TimeoutExpired:
            out = "TIMEOUT"
        m = re.search(r"(\d+) passed", out)
        f = re.search(r"(\d+) failed", out)
        e = re.search(r"(\d+) error", out)
        passed, failed = int(m.group(1)) if m else 0, int(f.group(1)) if f else 0
        ok = bool(m) and not f and not e
        results.append({"task": t["id"], "sample": k, "ok": ok, "passed": passed, "failed": failed,
                        "gen_seconds": gen, "rag_chars": rag_chars if args.model != "--reference" else 0, "tail": "" if ok else out[-400:]})
        print(f"{t['id']} s{k}: {'OK ' if ok else 'FAIL'} ({passed} ok, {failed} falhou) gen={gen}s", flush=True)

n_ok = sum(r["ok"] for r in results)
summary = {"name": args.name, "model": args.model, "tasks_ok": n_ok, "total": len(results),
           "pass_rate": round(n_ok / max(1, len(results)), 3), "results": results}
(run / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"== {args.name} [{args.model}]: {n_ok}/{len(results)} tarefas passando ({summary['pass_rate']:.0%})")
