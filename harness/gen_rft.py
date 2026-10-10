"""Amostragem com rejeição (RFT) "on-policy": o ALUNO gera K soluções por tarefa; os testes verificados filtram; só as que passam viram dados de treino.
Não muda o estilo do aluno (ao contrário de imitar o professor), só reforça o que ele já sabe fazer certo.
Uso: python3 gen_rft.py <saida.jsonl> <entrada1.jsonl> [entrada2.jsonl ...] [--k 8] [--model qwen3:8b] [--workers 6]
As entradas são os datasets do gerador (campos prompt, test, lang; sem 'lang' = python)."""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import lib  # noqa: E402
from gen_poly_dataset import LANGS, run_case  # noqa: E402

CODE_RE = re.compile(r"```[A-Za-z0-9+#_-]*[ \t]*\n(.*?)```", re.S)


def run_python(code, test, timeout=60):
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "solution.py").write_text(code, encoding="utf-8")
        (d / "test_solution.py").write_text(test, encoding="utf-8")
        try:
            return subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-W", "ignore", "--tb=no"],
                                  cwd=d, capture_output=True, timeout=timeout).returncode == 0
        except subprocess.TimeoutExpired:
            return False


def passes(lang, code, test):
    return run_python(code, test) if lang == "python" else run_case(lang, code, test)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--model", default="qwen3:8b")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    tasks = []
    for f in a.inputs:
        for line in open(f, encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                tasks.append({"prompt": r["prompt"], "test": r["test"], "lang": r.get("lang", "python")})
    print(len(tasks), "tarefas x", a.k, "amostras", flush=True)
    jobs = [(i, k) for i in range(len(tasks)) for k in range(a.k)]
    res = defaultdict(list)

    def work(job):
        i, k = job
        t = tasks[i]
        try:
            text, _ = lib.chat([{"role": "user", "content": t["prompt"]}], model=a.model, temperature=0.8, num_ctx=4096, num_predict=2000)
        except Exception:  # noqa: BLE001
            return
        m = CODE_RE.search(text)
        if not m:
            res[i].append((None, False))
            return
        code = m.group(1)
        res[i].append((code, passes(t["lang"], code, t["test"])))
        if len(res) % 20 == 0 and k == 0:
            print(f"  ... {len(res)} tarefas com amostras", flush=True)

    with ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(work, jobs))
    kept, stats = [], defaultdict(int)
    for i, t in enumerate(tasks):
        rs = res.get(i, [])
        ok = [c for c, p in rs if p]
        rate = len(ok) / max(1, len(rs))
        stats["tarefas"] += 1
        if rate == 0:
            stats["nenhuma_passa"] += 1
            continue
        stats["facil_100%" if rate == 1 else "medias"] += 1
        want = 1 if rate == 1 else 2        # mais exemplos onde o aluno ainda erra às vezes
        seen = []
        for c in ok:
            if c.strip() in seen:
                continue
            seen.append(c.strip())
            if len(seen) >= want:
                break
        fence = LANGS[t["lang"]]["fence"] if t["lang"] in LANGS else "python"
        for c in seen:
            kept.append({"prompt": t["prompt"], "completion": f"```{fence}\n{c.strip()}\n```", "lang": t["lang"], "pass_rate": round(rate, 2)})
    Path(a.out).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in kept), encoding="utf-8")
    print("FIM", dict(stats), "exemplos mantidos:", len(kept), flush=True)


if __name__ == "__main__":
    main()
