"""Baseline: modelo cru, só com a especificação. Salva resposta, projeto gerado e resultado dos testes."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import lib  # noqa: E402

name = sys.argv[1] if len(sys.argv) > 1 else "baseline"
model = sys.argv[2] if len(sys.argv) > 2 else "qwen3:8b"
run = lib.ROOT / "runs" / name
run.mkdir(parents=True, exist_ok=True)
spec = (lib.ROOT / "spec" / "TASK.md").read_text(encoding="utf-8")

with open(run / "response.txt", "w", encoding="utf-8") as log:
    text, meta = lib.chat([{"role": "user", "content": spec}], model=model, temperature=0.1 if model != "qwen3:8b" else 0.2,
                              num_predict=8000 if model != "qwen3:8b" else 6000, log=log)

files = lib.parse_files(text)
lib.write_project(files, run / "project")
result = lib.run_tests(run / "project") if files else {"passed": 0, "total": 0, "failures": [{"test": "<parse>", "message": "nenhum arquivo extraído"}]}
result.update({"files": sorted(files), "gen": meta})
(run / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"{name}: {result['passed']}/{result.get('total', 0)} testes | arquivos={sorted(files)} | {meta['seconds']}s")
