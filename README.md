# elias_ia_firma — laboratório para melhorar IAs locais de programação

**Objetivo:** aumentar muito a qualidade de IAs locais e gratuitas (um "Claude local") em programação, com qualidade alta independentemente do prompt.
Todas as técnicas do [guia](GUIA_PERSONALIZACAO_IA_LOCAL.md) valem (RAG, LoRA, loop de correção, best-of-N, agente, DPO). Cada mudança é **medida com testes automáticos** em suítes que o modelo não vê.
Última atualização: 2026-10-10. Gráfico da evolução: [evolucao.svg](evolucao.svg).

## 1. Resumo honesto do que foi conseguido
- **O que funciona e está entregue:** um agente local (`ia.bat`) que conversa no terminal e constrói coisas no PC (escreve arquivos, roda comandos, corrige erros), com **RAG** de notas de referência. Responde em 3–5 s com o modelo carregado.
- **RAG ajuda, menos do que parecia.** Na suíte em que as notas foram desenhadas o ganho foi +25 pontos (43% → 68%), mas na suíte **inédita** foi só +5 (35% → 40%). Parte do ganho inicial era "ensinar para a prova".
- **LoRA treinado imitando o professor (32B) piorou o aluno nas tarefas inéditas** (35% → 12–15%), apesar de melhorar Go e a suíte de desenvolvimento. Causa investigada: o aluno passou a escrever código menos cuidadoso (ex.: `parse_csv_line` com laço infinito). Detalhes na seção 6.
- **Padrão do `ia.bat` continua sendo o `qwen3:8b` + RAG**, porque nenhum LoRA bateu o modelo cru nas duas suítes inéditas (regra de entrega, seção 7).

## 2. Ambiente
| Item | Estado |
|---|---|
| PC de uso final | Windows 10, i5-1235U, 11,7 GB RAM, Intel Iris Xe. **Só CPU** (a GPU integrada fica mais lenta: 2,2 contra 4,8 tokens/s, testado com Vulkan). ~4–5 tokens/s |
| Ollama no PC | 0.21.2; servidor em `127.0.0.1:11434` (`127.0.0.1` evita um atraso de 2 s do IPv6 no Windows) |
| Modelo base | `qwen3:8b` (Q4_K_M, 5,2 GB) |
| GPU para treino/medição | Pod RunPod com RTX A6000 (46 GB), alugado por hora. Mesmos pesos do PC (mesmo hash do modelo), só mais rápido. Credenciais ficam fora do repositório |
| VPS própria | 2 vCPU, 1,9 GB RAM, sem GPU: não serve para rodar modelos |

**Restrição de implantação (definida pelo usuário):** a IA final roda em PC normal (CPU, ~12 GB). Por isso o entregável é um modelo de 3B a 8B quantizado. O modelo 32B (qwen2.5-coder) é só **professor** (gera e verifica dados) e **teto de comparação**.

## 3. Como usar
- **Agente no seu PC:** dois cliques em [`ia.bat`](ia.bat). Abre o terminal, liga o Ollama se precisar, pré-carrega o modelo e o RAG. Comandos: `/auto` (liga/desliga a confirmação antes de rodar comandos), `/limpar`, `/sair`. Trabalha na pasta `workspace/` (não escreve fora dela). Para trocar de modelo: `set IA_MODELO=...` no `.bat`.
- **Medir um modelo** (precisa do Ollama rodando):
  - `python harness/run_suite.py <nome> <modelo> --n 4 --temp 0.4 [--rag] [--suite heldout]` (14 tarefas Python; suíte inédita com `--suite heldout`, 10 tarefas)
  - `python harness/run_poly.py <nome> <modelo> --n 2 [--rag]` (24 desafios em Python, JS, C, Go, Java e SQL, por nível)
  - Validar que os testes estão certos: acrescente `--reference` (usa as soluções do professor Claude; hoje 14/14, 10/10 e 24/24).
- **Gráfico:** `python harness/plot_evolucao.py` (lê `evolucao.csv`).

## 4. Estrutura da pasta
| Caminho | O que é |
|---|---|
| `ia.py`, `ia.bat` | Agente local com ferramentas (listar/ler/escrever arquivo, rodar comando), streaming, RAG e pré-aquecimento |
| `rag/` | RAG leve: `kb/*.md` (notas por assunto), `rag.py` (chunks por seção, embeddings `nomic-embed-text`, busca cosseno com orçamento de contexto) |
| `suite/tasks.py` | Suíte de **desenvolvimento**: 14 tarefas Python pequenas (já usadas para desenhar o RAG) |
| `suite/heldout.py` | Suíte **inédita**: 10 tarefas novas, **nunca** usadas em RAG ou treino. É a prova que vale |
| `suite/poly.py` | Bateria **multilinguagem**: 24 desafios (Python, JS, C, Go, Java, SQL) em 3 níveis, em sequência |
| `spec/TASK.md`, `tests/test_api.py`, `reference/` | Tarefa grande (API FastAPI + SQLAlchemy + JWT): prompt, 21 testes escondidos e solução de referência (21/21) |
| `harness/` | `lib.py` (cliente Ollama), `run_suite.py`, `run_poly.py`, `run_baseline.py`, `run_repair.py`, `gen_dataset.py` e `gen_poly_dataset.py` (dataset verificado por execução com o professor), `gen_rft.py` (amostragem com rejeição do próprio aluno), `train_lora.py`, `merge_lora.py`, `pod_pipeline.sh`, `rft_v4.sh`, `plot_evolucao.py` |
| `artefatos/` | Adaptador LoRA v3 em GGUF (87 MB, só referência). O modelo `elias-v4` (5 GB, em partes) e o adaptador v4 ficam nas **Releases** do GitHub, com o script `instalar_elias_v4.bat` |
| `Modelfile.v1` | Primeiro ajuste (system prompt + parâmetros) |
| `evolucao.csv`, `evolucao.svg` | Dados e gráfico da evolução |
| `runs/pod/` | Resumos dos resultados rodados na GPU |

## 5. Resultados (mesmo prompt, 4 amostras por tarefa, temperatura 0,4, medidos na GPU do pod)
| Sistema | Dev (14) | **Inédita (10)** | Multilinguagem (24) | Obs. |
|---|---|---|---|---|
| qwen3:8b cru | 43% | **35%** | 54% | ponto de partida |
| + RAG v1 | 59% | — | — | notas escritas olhando os erros da dev |
| + RAG v2 | 68% | 40% | — | ganho real na inédita é só +5 |
| + LoRA v2 (QLoRA 4 bits, 3 épocas, imita o professor) | 48% | 12% | 52% | decorou o estilo; Go 12%→50% |
| + LoRA v2 + RAG | 55% | 28% | 50% | |
| + LoRA v3 (bf16, 2 épocas, lr 1e-4, dropout 0,1) | 54% | 15% | **58%** | Go 12%→38%, Python 50%→62% |
| + LoRA v3 + RAG | 50% | 20% | 50% | |
| **+ LoRA v4 (RFT: treina nas próprias respostas corretas)** | 45% | 30% | **58%** | empata com o cru sem o dano do v3; Go 13%→38%, JS 38%→50% |
| + LoRA v4 + RAG | 57% | 28% | 46% | RAG não ajuda o v4 na multilinguagem |
| Professor qwen2.5-coder:32b (1 amostra) | 79% | — | — | teto atual |

Multilinguagem do modelo cru por linguagem: Python 50%, JS 38%, C 63%, **Go 13%**, Java 75%, SQL 88%; por nível: fácil 75%, médio 59%, difícil 29%.

**Tarefa grande** (API completa de uma vez, 21 testes): qwen3:8b cru 0/21 (relationship sem FK, import circular), com system prompt 0/21 (esqueceu `models.py`), professor 32B 0/21 (usou `passlib`, fora da especificação). Nenhum modelo passou numa tentativa única; é onde um agente com laço de correção deve entrar.

## 6. Aprendizados
1. **Teste em dados que ninguém viu.** A suíte de desenvolvimento superestimou o RAG em 20 pontos. Por isso existe a suíte inédita.
2. **RAG:** pedaços heterogêneos fazem mal (um chunk misturando vários assuntos fez o modelo inventar validações e trocar classe por função). Um assunto por chunk.
3. **LoRA imitando um professor maior, com poucos exemplos, pode piorar o aluno.** Os exemplos eram verificados (os testes passavam), mas os testes gerados pelo próprio professor eram frouxos. O aluno aprendeu a escrever soluções "no estilo do professor" sem o mesmo cuidado com casos de borda: ex.: `parse_csv_line` com laço infinito, `guest` sem validação de não-vazio. A loss chegou a 0,08: ele decorou.
4. **O treino ajuda onde o aluno não sabia nada** (Go: 13% → 38–50%) e atrapalha onde já sabia.
5. **Ruído:** 10 tarefas com 4 amostras = um par de tarefas que vira muda 10–20 pontos. Aumentar a suíte inédita é um próximo passo.
6. **A GPU integrada do PC não ajuda** (mesma RAM, mais lenta com Vulkan).
7. **Latência do agente** vinha de recarregar o modelo a cada mudança de tamanho de contexto e de um atraso de IPv6; resolvido (3–5 s por resposta curta).
8. **Armadilhas do pod:** instalar as dependências do `llama.cpp` troca o PyTorch por uma versão sem CUDA e rebaixa o `transformers` (usar um ambiente virtual só para converter); o tokenizador salvo pelo `transformers` 5 quebra o conversor (restaurar o original); o Ollama novo não aceita adaptador LoRA (juntar o adaptador ao modelo e quantizar com `llama.cpp`); o disco de 31 GB enche com o cache do modelo base.

## 7. Regra de entrega
O modelo treinado só vira padrão do `ia.bat` se bater o `qwen3:8b` cru **nas duas suítes que não viram** (inédita > 35% e multilinguagem > 54%) sem piorar a dev. Se não bater, o padrão continua `qwen3:8b` com RAG. O `elias-v4` é distribuído como **experimental** (melhor LoRA: empata na inédita e melhora Go/JS). O v3 e o v2 não são recomendados (pioram a inédita).

## 8. Ciclo v4: amostragem com rejeição do próprio aluno (RFT)
Em vez de imitar o professor, o `qwen3:8b` gerou 8 soluções para cada uma das 281 tarefas verificadas, os testes filtraram, e ele treinou só nas próprias respostas corretas (1 exemplo onde acerta sempre, até 2 onde acerta só às vezes). Resultado da geração: das 281 tarefas, o aluno **nunca acertou 167**, acertou sempre 52 e acertou às vezes 62, o que rendeu **156 exemplos**. Treino: 2 épocas em bf16, loss 0,03, 3 minutos.
**Resultado:** não repetiu o dano do v3. Empata com o modelo cru na suíte inédita (30% contra 35%, diferença de 2 amostras em 40) e melhora a multilinguagem em 4 pontos (58% contra 54%), com ganhos em Go e JS. Pela regra de entrega (seção 7) **não vira o padrão** do `ia.bat`, porque o ganho não é claro o bastante; é distribuído como opção experimental `elias-v4`.
**Limite:** 156 exemplos e 10 tarefas inéditas dão resultados ruidosos; para afirmar um ganho real é preciso mais dados de treino e uma suíte inédita maior.

## 9. Próximos passos
1. Resultado do v4; se bater a regra de entrega, trocar o padrão do `ia.bat` e publicar.
2. Ampliar a suíte inédita (mais tarefas, outras áreas) para reduzir o ruído.
3. **Agente com laço de correção** para projetos completos (plataforma/app): planejar arquivos, escrever, rodar testes, corrigir. É o que separa um modelo de um "Claude local".
4. Dados melhores: testes mais rígidos (consenso entre soluções independentes), DPO com pares passou × falhou.
5. Modelo base diferente (ex.: Qwen3.6-27B quantizado em máquina com mais RAM) como comparação.

## 10. Como retomar se o PC reiniciar
1. Abrir o Ollama (ou `ollama serve`).
2. Rodar de novo o que estava na fila (comandos da seção 3). Os scripts do pod são retomáveis: `pod_pipeline.sh` pula o merge se o modelo mesclado já existe.
3. Conferir `runs/*.log` e `runs/suite/<nome>/summary.json`.

## 11. Avisos
- Credenciais (VPS, pod, chaves SSH) nunca entram no repositório.
- O pod RunPod cobra por hora enquanto ligado; desligar (Stop) apaga o disco dele, então copie os artefatos antes.
