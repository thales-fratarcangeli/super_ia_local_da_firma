# elias_ia_firma — laboratório para melhorar uma IA local de programação

Objetivo: **aumentar absurdamente a qualidade de IAs locais e gratuitas** (um "Claude local"), com qualidade alta independentemente do prompt. Todas as técnicas do guia valem (LoRA, RAG, loop de correção, best-of-N, agente, DPO).
Este arquivo é o diário/índice do projeto. Última atualização: 2026-10-09.

## 1. Ambiente
| Item | Estado |
|---|---|
| PC | Windows 10, 11,7 GB RAM, Intel Iris Xe (sem GPU dedicada): inferência só na CPU, ~2–4 tokens/s |
| Ollama | 0.21.2 instalado via winget (`%LOCALAPPDATA%\Programs\Ollama\ollama.exe`); servidor local em `localhost:11434` |
| Modelo base | `qwen3:8b` (5,2 GB) |
| VPS própria | 2 vCPU, 1,9 GB RAM, sem GPU: **não serve** para rodar o modelo (só consultada, nada instalado) |
| GPU para treino | Pod RunPod com RTX A6000 (46 GB), Ollama, `qwen2.5-coder:32b` baixado; laboratório copiado por SSH (dados de conexão ficam fora do repositório) |

## 2. Princípio
Mesmo prompt, uma tentativa, mede-se pass@1. Detalhes e regras: [IDEIA_AJUSTAR_IA_SEM_AUMENTAR_PROMPT.md](IDEIA_AJUSTAR_IA_SEM_AUMENTAR_PROMPT.md).
Catálogo de todas as formas de personalizar uma IA local: [GUIA_PERSONALIZACAO_IA_LOCAL.md](GUIA_PERSONALIZACAO_IA_LOCAL.md).


## 2b. Restrição de implantação (definida pelo usuário em 2026-10-10)
**A IA final roda em um PC normal (CPU, ~12 GB de RAM, sem GPU).** A GPU alugada (RunPod RTX A6000, 46 GB) é só ferramenta de treino e de medição rápida.
Consequências:
- O modelo entregue tem que caber e ser usável na CPU: **~3B a 8B quantizado (Q4_K_M)**. O 32B é só **professor** (gera e verifica dados de treino) e **teto de referência**, nunca o entregável.
- Os testes na GPU usam os **mesmos pesos quantizados (GGUF)** que irão para o PC, para os números transferirem. A medição final de precisão **e de tempo** é feita no PC.
- O RAG precisa ser leve: embedding pequeno (ex.: nomic-embed-text), índice local (sqlite-vec/FAISS), poucos trechos curtos. Na CPU, cada token a mais injetado custa tempo de leitura do prompt, então o contexto recuperado tem orçamento fixo.
- Sem restrição de tamanho de prompt (regra revisada em 2026-10-10): importa a qualidade final do sistema, medida também sob prompts parafraseados.

## 3. Estrutura da pasta
| Caminho | O que é |
|---|---|
| `spec/TASK.md` | Tarefa grande: API FastAPI + SQLAlchemy + JWT de gerenciamento de tarefas (o prompt fixo) |
| `tests/test_api.py` | 21 testes escondidos da tarefa grande (o modelo nunca os vê) |
| `reference/` | Implementação correta da tarefa grande (21/21): valida os testes e vira gabarito/dados |
| `suite/tasks.py` | **Suíte rápida**: 14 tarefas pequenas de 1 arquivo, cada uma com prompt, testes e solução de referência |
| `harness/lib.py` | Cliente do Ollama (streaming, thinking desligado), extração de arquivos da resposta, execução dos testes |
| `harness/run_baseline.py` | Roda a tarefa grande: `python harness/run_baseline.py <nome> [modelo]` |
| `harness/run_suite.py` | Roda a suíte rápida: `python harness/run_suite.py <nome> [modelo] [--only t01,t05] [--n 3] [--reference]` |
| `harness/run_repair.py` | Loop gerar→testar→corrigir (retomável). Só como gerador de dados, **não** conta como melhoria |
| `Modelfile.v1` | Ajuste v1: system prompt embutido + parâmetros; cria o modelo `elias-v1` |
| `runs/` | Saídas: respostas, projetos gerados, `result.json`, `summary.json`, logs |

## 4. Linha do tempo (o que foi feito)
1. Instalado o Ollama e baixado o `qwen3:8b`.
2. Consultada a VPS (somente leitura): inviável para IA.
3. Escrita a tarefa grande (`spec/TASK.md`) e os 21 testes escondidos; montado o harness.
4. **Baseline v0 (modelo cru): 0/21.** Causa: relationship sem FK quebra todos os mappers; import circular; header Bearer obrigatório dando 422 em vez de 401. Análise em `runs/baseline/ANALISE.md`.
5. Criado um loop de correção; **descartado como melhoria** (aumenta o prompt), mantido só como gerador de dados. O PC desligou no meio, então o loop ficou retomável.
6. Escrita a implementação de referência e validado: **21/21** (os testes estão certos).
7. **v1 (Modelfile com system prompt + parâmetros): 0/21.** Corrigiu o import circular, mas esqueceu de gerar `app/models.py`, então nada importa. 52 min de geração.
8. Diagnóstico: tarefa grande demais e iteração lenta demais (25–50 min por medida). Criada a **suíte rápida** (14 tarefas, minutos cada), validada **14/14** contra as referências.
9. **Em andamento:** suíte rápida em v0 (qwen3:8b cru) e depois v1 (`elias-v1`).

## 5. Quadro de resultados
| Versão | Mudança | Tarefa grande (21 testes) | Suíte rápida (14 tarefas) |
|---|---|---|---|
| v0 | qwen3:8b cru | 0/21 | em execução (`runs/s_v0.log`) |
| v1 | + system prompt + parâmetros | 0/21 | na fila (`runs/s_v1.log`) |

A suíte cobre: slugify, paginação, parser de query string, LRU, hash de senha, JWT, repositório sqlite, modelos SQLAlchemy (relationship/cascade), FastAPI com 401 em Bearer, FastAPI com paginação 422, merge de intervalos, token bucket, toposort e validação Pydantic. Alguns testes miram diretamente os erros vistos no baseline (FK/relationship, 401 vs 422).

## 5b. Resultados dos ciclos (suíte rápida, 4 amostras/tarefa, temp 0,4, na GPU do pod)
| Ciclo | Sistema | Passando | Obs. |
|---|---|---|---|
| ref | qwen2.5-coder:32b (professor, 1 amostra) | 11/14 (79%) | teto atual |
| C1-base | qwen3:8b cru | 24/56 (43%) | ponto de partida do aluno |
| C1-RAG v1 | qwen3:8b + RAG (22 chunks, k=3, ~1060 chars) | **33/56 (59%)** | +16 pts. Ganhos: t01 slugify 0→4, t06 jwt 0→4. Regressões: t12 token bucket 4→1, t08 sqlalchemy 1→0 |

Ressalvas do C1-RAG v1: (1) as notas foram escritas depois de ver os erros da suíte, então o ganho em t01/t06 pode ser "ensinar para a prova"; só uma **suíte inédita (held-out)** confirma. (2) A regressão da t12 veio de um chunk heterogêneo ("Estruturas e validação") que induziu validações e função em vez de classe: corrigido no RAG v2 (chunks de um assunto só). Custo do RAG: ~1060 caracteres de contexto por pedido.

## 6. Próximos passos (ordem)
1. Ler os resultados de v0 e v1 na suíte, classificar os erros por tipo.
2. **Modelo base maior** em GPU alugada (qwen3-coder / qwen2.5-coder:32b) como novo ponto de comparação.
3. **RAG interno** (chunking por função, embeddings, reranker) alimentado pelas referências e docs das bibliotecas.
4. **Dataset por rejection sampling** (N amostras por tarefa, fica só o que passa nos testes) e **LoRA** em GPU alugada; depois DPO com pares passou × falhou.
5. Reavaliar na suíte rápida e, no fim, na tarefa grande.

## 7. Como retomar se o PC reiniciar
1. Subir o Ollama: abrir o app Ollama, ou `ollama serve`.
2. Rodar de novo o que estava na fila (`python harness/run_suite.py s_v0 qwen3:8b`, etc.). O `run_repair.py` retoma sozinho.
3. Conferir `runs/*.log` e `runs/suite/<nome>/summary.json`.

## 8. Avisos
- Credenciais (VPS, pod, chaves SSH) nunca entram no repositório.
- Nada foi commitado ou enviado para fora; tudo é local.
