"""Agente de programação local: conversa no terminal e constrói coisas no seu PC usando o modelo do Ollama.
Ferramentas do agente: listar pasta, ler arquivo, escrever arquivo, rodar comando.
Segurança: arquivos só dentro da pasta de trabalho; comandos pedem confirmação (a menos que use /auto).
Uso: python ia.py [--pasta CAMINHO] [--modelo NOME] [--auto] [--uma "pedido"]"""
import argparse
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import requests

OLLAMA = os.environ.get("OLLAMA_HOST_URL", "http://127.0.0.1:11434")
AQUI = Path(__file__).resolve().parent

SISTEMA = """Você é um engenheiro de software sênior no computador do usuário (Windows), numa pasta de trabalho. Responda em português.
Para construir algo: planeje em 1-2 frases, escreva cada arquivo COMPLETO com escrever_arquivo, rode com rodar_comando, leia a saída e corrija os erros até funcionar.
Use só caminhos relativos. Prefira a biblioteca padrão. Nada destrutivo. No fim, diga em poucas linhas o que foi criado e como executar."""

SISTEMA_CHAT = "Você é um assistente de programação simpático e direto. Responda em português, de forma curta."

PALAVRAS_TAREFA = ("crie", "criar", "faça", "faca", "fazer", "escreva", "escrever", "gere", "gerar", "construa", "monte", "implemente",
                   "programa", "script", "site", "app", "aplicativo", "api", "arquivo", "pasta", "rode", "rodar", "execute", "corrija",
                   "conserte", "teste", "código", "codigo", "função", "funcao", "classe", "jogo", "bot", "leia", "liste", "instale")


def parece_tarefa(txt):
    t = txt.lower()
    return len(t) > 60 or any(p in t for p in PALAVRAS_TAREFA)


TOOLS = [
    {"type": "function", "function": {"name": "listar_pasta", "description": "Lista arquivos de uma pasta ('.' = raiz).",
        "parameters": {"type": "object", "properties": {"caminho": {"type": "string"}}, "required": ["caminho"]}}},
    {"type": "function", "function": {"name": "ler_arquivo", "description": "Lê um arquivo de texto.",
        "parameters": {"type": "object", "properties": {"caminho": {"type": "string"}}, "required": ["caminho"]}}},
    {"type": "function", "function": {"name": "escrever_arquivo", "description": "Cria/sobrescreve um arquivo com o conteúdo COMPLETO.",
        "parameters": {"type": "object", "properties": {"caminho": {"type": "string"}, "conteudo": {"type": "string"}}, "required": ["caminho", "conteudo"]}}},
    {"type": "function", "function": {"name": "rodar_comando", "description": "Executa um comando na pasta de trabalho e devolve a saída.",
        "parameters": {"type": "object", "properties": {"comando": {"type": "string"}}, "required": ["comando"]}}},
]


class Agente:
    def __init__(self, pasta, modelo, auto):
        self.pasta = Path(pasta).resolve()
        self.pasta.mkdir(parents=True, exist_ok=True)
        self.modelo, self.auto = modelo, auto
        self.rag = None
        self.msgs = [{"role": "system", "content": SISTEMA + f"\nPasta de trabalho: {self.pasta}"}]

    def _seguro(self, caminho):
        p = (self.pasta / caminho).resolve()
        if self.pasta != p and self.pasta not in p.parents:
            raise PermissionError(f"caminho fora da pasta de trabalho: {caminho}")
        return p

    def tarefa_ativa(self):
        """Continua em modo ferramentas se a conversa já usou ferramentas (ex.: 'agora adicione X')."""
        return any(m.get("role") == "tool" for m in self.msgs)

    def executar(self, nome, a):
        try:
            if nome == "listar_pasta":
                p = self._seguro(a.get("caminho", "."))
                itens = sorted(p.iterdir(), key=lambda x: (x.is_file(), x.name))
                return "\n".join(("[pasta] " if i.is_dir() else "") + i.name for i in itens) or "(vazia)"
            if nome == "ler_arquivo":
                return self._seguro(a["caminho"]).read_text(encoding="utf-8", errors="replace")[:6000]
            if nome == "escrever_arquivo":
                p = self._seguro(a["caminho"])
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(a["conteudo"], encoding="utf-8")
                print(f"   [escreveu] {p.relative_to(self.pasta)} ({len(a['conteudo'])} caracteres)")
                return f"ok: {a['caminho']} salvo"
            if nome == "rodar_comando":
                cmd = a["comando"]
                print(f"   [comando] {cmd}")
                if not self.auto:
                    r = input("   executar? [s/N/a=sempre] ").strip().lower()
                    if r == "a":
                        self.auto = True
                    elif r not in ("s", "sim", "y"):
                        return "usuário recusou executar este comando"
                p = subprocess.run(cmd, shell=True, cwd=self.pasta, capture_output=True, text=True, timeout=120,
                                   encoding="utf-8", errors="replace")
                out = (p.stdout + p.stderr)[-3000:]
                return f"código de saída {p.returncode}\n{out}"
            return f"ferramenta desconhecida: {nome}"
        except subprocess.TimeoutExpired:
            return "erro: comando passou de 120 s"
        except Exception as e:  # noqa: BLE001
            return f"erro: {type(e).__name__}: {e}"

    def chamar(self, com_ferramentas=True):
        msgs = self.msgs if com_ferramentas else [{"role": "system", "content": SISTEMA_CHAT}] + self.msgs[1:]
        corpo = {"model": self.modelo, "messages": msgs, "stream": True, "think": False, "keep_alive": "60m",
                 "options": {"temperature": 0.2, "num_ctx": 8192, "num_predict": 4000 if com_ferramentas else 600}}
        if com_ferramentas:
            corpo["tools"] = TOOLS
        texto, calls, primeiro = [], [], True
        with requests.post(f"{OLLAMA}/api/chat", json=corpo, stream=True, timeout=3600) as r:
            r.raise_for_status()
            for linha in r.iter_lines():
                if not linha:
                    continue
                d = json.loads(linha)
                m = d.get("message", {})
                if m.get("content"):
                    if primeiro:
                        print("\nIA: ", end="", flush=True)
                        primeiro = False
                    print(m["content"], end="", flush=True)
                    texto.append(m["content"])
                calls += m.get("tool_calls") or []
                if d.get("done"):
                    break
        if not primeiro:
            print("\n")
        msg = {"role": "assistant", "content": "".join(texto)}
        if calls:
            msg["tool_calls"] = calls
        return msg

    def turno(self, texto):
        self.msgs.append({"role": "user", "content": texto})
        self.tarefa = parece_tarefa(texto) or self.tarefa_ativa()
        if self.tarefa and self.rag:
            try:
                nota, _ = self.rag.system_message(texto)
            except Exception:  # noqa: BLE001
                nota = None
            self.msgs = [m for m in self.msgs if not (m["role"] == "system" and m["content"].startswith("Notas de referência"))]
            if nota:
                self.msgs.insert(1, {"role": "system", "content": nota})
        for _ in range(25):  # limite de passos por pedido
            t0 = time.time()
            print("   ... pensando", end="\r", flush=True)
            m = self.chamar()
            self.msgs.append(m)
            if m.get("content"):
                print(f"\nIA: {m['content'].strip()}\n")
            calls = m.get("tool_calls") or []
            if not calls:
                return
            for c in calls:
                f = c["function"]
                args = f.get("arguments") or {}
                if isinstance(args, str):
                    args = json.loads(args or "{}")
                saida = self.executar(f["name"], args)
                self.msgs.append({"role": "tool", "tool_name": f["name"], "content": saida})
            print(f"   (passo em {time.time() - t0:.0f}s)")
        print("IA: parei após 25 passos; peça para continuar se precisar.\n")


def carregar_rag():
    """RAG leve: notas de referência (rag/kb) buscadas por embeddings. Desliga sozinho se algo faltar (numpy, nomic-embed-text...)."""
    try:
        sys.path.insert(0, str(AQUI / "rag"))
        import rag as _rag
        if not _rag.INDEX.exists():
            print("   (montando o índice do RAG, só na primeira vez...)")
            _rag.build()
        return _rag.Retriever(k=3, budget_chars=1400)
    except Exception as e:  # noqa: BLE001
        print(f"   (RAG desligado: {type(e).__name__}: {e})")
        return None


def preaquecer(modelo):
    """Carrega o modelo na memória enquanto o usuário digita (a 1a resposta deixa de pagar o carregamento)."""
    try:
        requests.post(f"{OLLAMA}/api/generate", json={"model": modelo, "prompt": "", "keep_alive": "60m", "options": {"num_ctx": 8192}}, timeout=600)
    except Exception:  # noqa: BLE001
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pasta", default=str(AQUI / "workspace"))
    ap.add_argument("--modelo", default=os.environ.get("IA_MODELO", "qwen3:8b"))
    ap.add_argument("--auto", action="store_true", help="roda comandos sem pedir confirmação")
    ap.add_argument("--sem-rag", action="store_true", help="não consulta as notas de referência")
    ap.add_argument("--uma", default="", help="executa um único pedido e sai")
    a = ap.parse_args()
    ag = Agente(a.pasta, a.modelo, a.auto)
    if not a.sem_rag:
        ag.rag = carregar_rag()
    if not a.uma:  # no modo interativo carrega o modelo enquanto o usuário digita
        threading.Thread(target=preaquecer, args=(a.modelo,), daemon=True).start()
    print(f"== IA local | modelo: {a.modelo} | pasta: {ag.pasta}\n   comandos: /auto (liga/desliga confirmação) /limpar (nova conversa) /sair\n")
    if a.uma:
        ag.turno(a.uma)
        return
    while True:
        try:
            txt = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not txt:
            continue
        if txt in ("/sair", "/exit", "sair"):
            break
        if txt == "/auto":
            ag.auto = not ag.auto
            print(f"   confirmação de comandos: {'DESLIGADA' if ag.auto else 'ligada'}\n")
            continue
        if txt == "/limpar":
            ag.msgs = ag.msgs[:1]
            print("   conversa limpa\n")
            continue
        try:
            ag.turno(txt)
        except requests.exceptions.ConnectionError:
            print("   Ollama não está respondendo. Abra o Ollama e tente de novo.\n")
        except Exception as e:  # noqa: BLE001
            print(f"   erro: {type(e).__name__}: {e}\n")


if __name__ == "__main__":
    main()
