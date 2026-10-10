"""Gera evolucao.svg a partir de evolucao.csv (sem dependências). Uso: python harness/plot_evolucao.py
CSV: ciclo,rotulo,suite,pct,tipo   (tipo = aluno | teto ; suite = dev | heldout)
Linha sólida = qualidade do aluno por ciclo na suíte dev; linha laranja = suíte inédita (heldout); tracejada = professor."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rows = list(csv.DictReader(open(ROOT / "evolucao.csv", encoding="utf-8")))
alunos = [r for r in rows if r["tipo"] == "aluno"]
tetos = [r for r in rows if r["tipo"] == "teto"]
rotulos = []
for r in alunos:
    if r["rotulo"] not in rotulos:
        rotulos.append(r["rotulo"])

W, H, L, R, T, B = 860, 460, 70, 30, 60, 110
pw, ph = W - L - R, H - T - B


def x(i):
    return L + (pw * i / max(1, len(rotulos) - 1) if len(rotulos) > 1 else pw / 2)


def y(p):
    return T + ph * (1 - p / 100)


svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Segoe UI,Arial,sans-serif">',
       f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
       f'<text x="{L}" y="30" font-size="20" font-weight="600" fill="#1f2937">Evolução da qualidade da IA local (tarefas passando nos testes)</text>',
       f'<text x="{L}" y="48" font-size="12" fill="#6b7280">Aluno que roda no seu PC · quanto maior, melhor</text>']
for g in range(0, 101, 20):
    svg.append(f'<line x1="{L}" y1="{y(g)}" x2="{W - R}" y2="{y(g)}" stroke="#e5e7eb"/>')
    svg.append(f'<text x="{L - 8}" y="{y(g) + 4}" font-size="11" text-anchor="end" fill="#6b7280">{g}%</text>')
for r in tetos:
    p = float(r["pct"])
    svg.append(f'<line x1="{L}" y1="{y(p)}" x2="{W - R}" y2="{y(p)}" stroke="#9ca3af" stroke-dasharray="6 4"/>')
    svg.append(f'<text x="{W - R}" y="{y(p) - 6}" font-size="11" text-anchor="end" fill="#6b7280">{r["rotulo"]}: {p:.0f}%</text>')

series = [("dev", "#2563eb", "suíte de desenvolvimento"), ("heldout", "#ea580c", "suíte inédita (heldout)")]
for suite, cor, nome in series:
    pts = [(rotulos.index(r["rotulo"]), float(r["pct"])) for r in alunos if r["suite"] == suite]
    if not pts:
        continue
    pts.sort()
    if len(pts) > 1:
        svg.append(f'<polyline fill="none" stroke="{cor}" stroke-width="3" points="{" ".join(f"{x(i):.1f},{y(p):.1f}" for i, p in pts)}"/>')
    for i, p in pts:
        svg.append(f'<circle cx="{x(i):.1f}" cy="{y(p):.1f}" r="5" fill="{cor}"/>')
        svg.append(f'<text x="{x(i):.1f}" y="{y(p) - 11:.1f}" font-size="13" font-weight="600" text-anchor="middle" fill="{cor}">{p:.0f}%</text>')
for i, rot in enumerate(rotulos):
    svg.append(f'<text x="{x(i):.1f}" y="{H - B + 22}" font-size="12" text-anchor="middle" fill="#374151">{rot}</text>')
ly = H - 22
for k, (suite, cor, nome) in enumerate(series):
    if any(r["suite"] == suite for r in alunos):
        svg.append(f'<rect x="{L + k * 250}" y="{ly - 9}" width="14" height="4" fill="{cor}"/>')
        svg.append(f'<text x="{L + k * 250 + 20}" y="{ly - 3}" font-size="12" fill="#374151">{nome}</text>')
svg.append("</svg>")
(ROOT / "evolucao.svg").write_text("\n".join(svg), encoding="utf-8")
print("evolucao.svg gerado com", len(alunos), "pontos")
