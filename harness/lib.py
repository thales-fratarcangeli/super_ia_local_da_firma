"""Utilitários: chamar o Ollama, extrair arquivos da resposta, rodar os testes e medir."""
import json
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
OLLAMA = "http://localhost:11434"
TAIL_RE = re.compile(r"###\s*FILE:\s*(\S+)\s*\n```[a-zA-Z]*\n((?:(?!```).)*)\Z", re.S)
FILE_RE = re.compile(r"###\s*FILE:\s*(\S+)\s*\n```[a-zA-Z]*\n(.*?)```", re.S)


def chat(messages, model="qwen3:8b", temperature=0.2, num_ctx=8192, num_predict=6000, log=None):
    """Chama /api/chat com streaming (thinking desligado, senão fica lento demais na CPU)."""
    body = {
        "model": model, "messages": messages, "stream": True, "think": False,
        "options": {"temperature": temperature, "num_ctx": num_ctx, "num_predict": num_predict},
    }
    out, t0, n = [], time.time(), 0
    with requests.post(f"{OLLAMA}/api/chat", json=body, stream=True, timeout=None) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if not line:
                continue
            d = json.loads(line)
            piece = d.get("message", {}).get("content", "")
            out.append(piece)
            n += 1
            if log and piece:
                log.write(piece)
                log.flush()
            if d.get("done"):
                break
    text = "".join(out)
    return text, {"seconds": round(time.time() - t0, 1), "chunks": n}


def parse_files(text):
    files = {m.group(1).strip().lstrip("./"): m.group(2) for m in FILE_RE.finditer(text)}
    # último bloco sem fence de fechamento (resposta cortada pelo limite de tokens): marca como truncado
    tail = re.search(TAIL_RE, text)
    if tail and tail.group(1).strip().lstrip("./") not in files:
        files[tail.group(1).strip().lstrip("./")] = tail.group(2)
    return files


def write_project(files, dest: Path):
    dest.mkdir(parents=True, exist_ok=True)
    for rel, code in files.items():
        p = dest / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(code, encoding="utf-8")
    # garante que app/ é pacote mesmo que o modelo esqueça
    if (dest / "app").is_dir() and not (dest / "app" / "__init__.py").exists():
        (dest / "app" / "__init__.py").write_text("", encoding="utf-8")


def run_tests(project: Path, timeout=300):
    """Roda os testes escondidos contra o projeto gerado. Retorna dict com métricas."""
    xml = project / "junit.xml"
    if xml.exists():
        xml.unlink()
    p = subprocess.run(
        [sys.executable, "-m", "pytest", str(ROOT / "tests" / "test_api.py"), "-q", "-x" if False else "-q",
         f"--junitxml={xml}", "-p", "no:cacheprovider", "--rootdir", str(project)],
        cwd=project, capture_output=True, text=True, timeout=timeout)
    res = {"passed": 0, "failed": 0, "errors": 0, "total": 0, "failures": [], "stdout_tail": p.stdout[-3000:]}
    if xml.exists():
        suite = ET.parse(xml).getroot()
        for case in suite.iter("testcase"):
            res["total"] += 1
            bad = case.find("failure") if case.find("failure") is not None else case.find("error")
            if bad is None:
                res["passed"] += 1
            else:
                res["failed" if case.find("failure") is not None else "errors"] += 1
                res["failures"].append({"test": case.get("name"), "message": (bad.get("message") or "")[:300]})
    else:  # nem coletou (erro de import etc.)
        res["errors"] = 1
        res["failures"].append({"test": "<collection>", "message": p.stdout[-800:] + p.stderr[-800:]})
    return res
