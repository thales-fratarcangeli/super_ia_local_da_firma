"""RAG leve: chunking por seção, embeddings (Ollama nomic-embed-text), busca cosseno com orçamento de contexto.
O prompt do usuário NÃO muda: os trechos vão numa mensagem de sistema, limitada por `budget_chars`.
Uso: python rag/rag.py build            -> gera rag/index.json a partir de rag/kb/*.md
     python rag/rag.py query "texto"    -> mostra o que seria recuperado"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import requests

HERE = Path(__file__).parent
KB = HERE / "kb"
INDEX = HERE / "index.json"
OLLAMA = "http://127.0.0.1:11434"
EMBED_MODEL = "nomic-embed-text"


def embed(texts, prefix):
    r = requests.post(f"{OLLAMA}/api/embed", json={"model": EMBED_MODEL, "input": [prefix + t for t in texts]}, timeout=300)
    r.raise_for_status()
    v = np.array(r.json()["embeddings"], dtype=np.float32)
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def chunk_kb():
    chunks = []
    for f in sorted(KB.glob("*.md")):
        for part in re.split(r"(?m)^## ", f.read_text(encoding="utf-8")):
            part = part.strip()
            if not part:
                continue
            title, _, body = part.partition("\n")
            chunks.append({"source": f.name, "title": title.strip(), "text": f"{title.strip()}: {body.strip()}"})
    return chunks


def build():
    chunks = chunk_kb()
    vecs = embed([c["text"] for c in chunks], "search_document: ")
    INDEX.write_text(json.dumps({"chunks": chunks, "vectors": vecs.tolist()}), encoding="utf-8")
    print(f"{len(chunks)} chunks indexados em {INDEX}")


class Retriever:
    def __init__(self, k=3, budget_chars=1400, min_score=0.0):
        data = json.loads(INDEX.read_text(encoding="utf-8"))
        self.chunks, self.vecs = data["chunks"], np.array(data["vectors"], dtype=np.float32)
        self.k, self.budget, self.min_score = k, budget_chars, min_score

    def retrieve(self, query):
        q = embed([query[:2000]], "search_query: ")[0]
        scores = self.vecs @ q
        out, used = [], 0
        for i in np.argsort(-scores)[: self.k]:
            if scores[i] < self.min_score:
                break
            text = self.chunks[i]["text"]
            if used + len(text) > self.budget:
                text = text[: max(0, self.budget - used)].rsplit(" ", 1)[0]
                if len(text) < 80:
                    break
            out.append({"title": self.chunks[i]["title"], "score": float(scores[i]), "text": text})
            used += len(text)
        return out

    def system_message(self, query):
        hits = self.retrieve(query)
        if not hits:
            return None, []
        body = "\n\n".join(f"- {h['text']}" for h in hits)
        return "Notas de referência (use apenas se forem relevantes para a tarefa):\n" + body, hits


if __name__ == "__main__":
    if sys.argv[1] == "build":
        build()
    else:
        msg, hits = Retriever().system_message(" ".join(sys.argv[2:]))
        print(msg)
