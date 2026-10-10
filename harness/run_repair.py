"""Loop de correção: roda os testes, devolve erros + código ao modelo, repete. Uso: run_repair.py <origem> <destino> [rodadas]"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import lib  # noqa: E402

src, name = sys.argv[1], sys.argv[2]
rounds = int(sys.argv[3]) if len(sys.argv) > 3 else 4
run = lib.ROOT / "runs" / name
proj = run / "project"
spec = (lib.ROOT / "spec" / "TASK.md").read_text(encoding="utf-8")
hist_file = run / "history.json"
# retoma se já houve rodadas (PC desligou etc.): continua do estado atual do projeto destino
resume = hist_file.exists() and json.loads(hist_file.read_text(encoding="utf-8")) and (proj / "app").exists()
base = proj if resume else lib.ROOT / "runs" / src / "project"
files = {str(p.relative_to(base)).replace("\\", "/"): p.read_text(encoding="utf-8") for p in base.rglob("*.py")
         if "__pycache__" not in p.parts}
if not resume:
    lib.write_project(files, proj)
history = json.loads(hist_file.read_text(encoding="utf-8")) if resume else []
start = len(history) and history[-1]["round"]


def summarize(res):
    seen, lines = set(), []
    for f in res["failures"]:
        key = f["message"][:120]
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"- {f['test']}: {f['message']}")
    return "\n".join(lines[:12])


for r in range(start, rounds + 1):
    res = lib.run_tests(proj)
    history = [h for h in history if h["round"] != r]
    history.append({"round": r, "passed": res["passed"], "total": res["total"]})
    print(f"rodada {r}: {res['passed']}/{res['total']}", flush=True)
    (run / "history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")
    if res["passed"] == res["total"] and res["total"] > 0 or r == rounds:
        break
    code = "\n\n".join(f"### FILE: {k}\n```python\n{v}```" for k, v in files.items())
    prompt = (f"{spec}\n\n---\nAbaixo está sua implementação atual e os erros dos testes automáticos. "
              f"Corrija os bugs. Responda SOMENTE com os arquivos que mudaram, completos, no formato '### FILE:'.\n\n"
              f"## CÓDIGO ATUAL\n{code}\n\n## ERROS DOS TESTES ({res['passed']}/{res['total']} passando)\n{summarize(res)}\n")
    with open(run / f"round{r + 1}_response.txt", "w", encoding="utf-8") as log:
        text, meta = lib.chat([{"role": "user", "content": prompt}], num_ctx=16384, num_predict=6000, log=log)
    new = lib.parse_files(text)
    files.update(new)
    lib.write_project(new, proj)
    print(f"  corrigiu {sorted(new)} em {meta['seconds']}s", flush=True)
