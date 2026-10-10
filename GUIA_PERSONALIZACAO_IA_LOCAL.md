# Guia: tudo que dá para mexer numa IA local de programação

Objetivo: ter a IA local mais forte possível para programar. Este guia lista as alavancas, o custo de cada uma e a ordem recomendada.

> Os nomes de modelos mudam rápido. Confira o que existe na biblioteca do Ollama (ollama.com/library) e no Hugging Face antes de baixar.

---

## 1. Escolher o modelo base (maior alavanca)

Nenhuma técnica abaixo compensa um modelo base fraco. O ganho principal vem de rodar o maior modelo de código que o hardware aguenta.

| Faixa de memória | Modelos de código a considerar |
|---|---|
| ~8 GB (CPU, seu PC hoje) | qwen3:4b/8b, qwen2.5-coder:7b, deepseek-coder:6.7b |
| 16–24 GB (GPU 4090/3090) | qwen3:14b/30b-a3b, qwen2.5-coder:14b/32b (quantizado), devstral, gpt-oss:20b |
| 48–96 GB (2 GPUs, Mac Studio, A100) | qwen3-coder (30B/480B), qwen2.5-coder:32b em Q8, deepseek-coder-v2, gpt-oss:120b |

Regra: **MoE** (ex.: qwen3:30b-a3b) roda mais rápido que um denso do mesmo tamanho, porque ativa só parte dos pesos por token.

---

## 2. Sem mexer nos pesos (grátis, rápido de testar)

| Técnica | O que faz | Esforço |
|---|---|---|
| **Modelfile do Ollama** | System prompt fixo, temperatura, contexto, template | Minutos |
| **Engenharia de prompt** | Instruções claras, exemplos (few-shot), formato de saída, passos "planeje, depois escreva" | Minutos |
| **Parâmetros de amostragem** | temperature baixa (0–0.2) para código, top_p, repeat_penalty, seed fixa | Minutos |
| **Contexto maior (num_ctx)** | Mais código cabe na conversa. Custa RAM | Minutos |
| **Thinking/raciocínio** | Modelos como qwen3 pensam antes de responder: mais certo, mais lento | Minutos |
| **Saída estruturada** | Força JSON/gramática (GBNF) e elimina erro de formato | Horas |
| **Loop de execução e correção** | Gera, roda testes, devolve o erro ao modelo, repete. Maior ganho por esforço | Horas |
| **Best-of-N** | Gera N soluções e fica com a que passa nos testes | Horas |
| **Self-consistency / revisão** | Um segundo passo revisa o código do primeiro | Horas |
| **Agentes com ferramentas** | Ler arquivos, rodar comandos, buscar na doc (tool calling) | Dias |
| **Decomposição de tarefa** | Planejador quebra o problema, o executor faz arquivo por arquivo | Dias |
| **Pipeline multi-modelo** | Modelo grande planeja, o rápido escreve, um terceiro revisa | Dias |
| **Speculative decoding** | Modelo pequeno "adivinha" tokens e o grande confirma: mais velocidade | Horas |

---

## 3. Conhecimento externo (RAG)

Dá ao modelo informação que ele não tem, sem treinar.

- **Chunking:** quebrar código e docs em pedaços. Para código, melhor por função/classe (tree-sitter) do que por tamanho fixo.
- **Embeddings:** modelos como nomic-embed-text, bge-m3 ou qwen3-embedding (via Ollama).
- **Banco vetorial:** Chroma, Qdrant, FAISS ou sqlite-vec.
- **Busca híbrida:** vetorial + palavra-chave (BM25) + **reranker** (bge-reranker): melhora muito a precisão.
- **Contexto do repositório:** índice do seu código (nomes de funções, mapa de dependências).
- **Documentação das bibliotecas** (FastAPI, SQLAlchemy etc.) na versão que você usa.
- **Memória de erros:** guardar "erro → correção que funcionou" e recuperar em casos parecidos.

---

## 4. Mexendo nos pesos (treino)

Precisa de GPU (aluguel por hora: RunPod, Vast.ai, Lambda, Colab).

| Técnica | O que faz | VRAM aprox. (modelo 8B) |
|---|---|---|
| **SFT com LoRA/QLoRA** | Ensina estilo, formato e padrões do seu projeto | 12–24 GB |
| **Fine-tuning completo** | Altera todos os pesos | 80+ GB |
| **Destilação** | Um modelo forte (ex.: Claude) gera exemplos e o local aprende | Igual ao SFT |
| **Rejection sampling (RFT)** | Gera N respostas, **mantém só as que passam nos testes**, treina nelas | Igual ao SFT |
| **DPO / ORPO / KTO** | Treina com pares "resposta boa × ruim" (código que passa × que falha) | 24+ GB |
| **RL com recompensa de testes (GRPO)** | O modelo treina rodando testes e ganha recompensa por passar. Mais poderoso, mais difícil | 40+ GB |
| **Continued pretraining** | Mais texto bruto (seu código, docs) | Alto |

Ferramentas: Unsloth (mais fácil e rápido), Axolotl, LLaMA-Factory, TRL (Hugging Face), torchtune.

Depois de treinar: converter o adaptador para GGUF, juntar ao modelo base e importar no Ollama com `ollama create`.

**Cuidados:** poucos dados bons valem mais que muitos ruins (comece com 500–2000 exemplos verificados). Separe um conjunto de avaliação que o treino nunca vê. Fine-tuning demais causa esquecimento e overfitting.

---

## 5. Mexendo no modelo em si

| Técnica | O que faz |
|---|---|
| **Quantização** (Q4_K_M, Q5, Q6, Q8, AWQ, GPTQ) | Menor e mais rápido, perde um pouco de qualidade. Q4_K_M é o equilíbrio padrão; para código, prefira Q6/Q8 se couber |
| **Merge de modelos** (mergekit: SLERP, TIES, DARE) | Combina pesos de modelos diferentes, por exemplo um de código com um de instrução |
| **Merge de LoRA** | Junta o adaptador ao modelo base |
| **Extensão de contexto** (RoPE/YaRN) | Aumenta o tamanho de contexto suportado |
| **Poda e destilação para modelo menor** | Reduz o tamanho mantendo parte da capacidade |
| **Cache de KV quantizado** | Menos RAM para contextos longos |

---

## 6. Olhar dentro do modelo (pesquisa)

Não é "decompilar": o modelo são matrizes de números, sem código-fonte.

- **Interpretabilidade:** TransformerLens, nnsight, sparse autoencoders: ver quais neurônios e cabeças de atenção ativam.
- **Activation steering / representation engineering:** empurrar o comportamento ao somar vetores nas ativações (mais cuidadoso, mais conciso etc.).
- **Abliteration:** remove a direção de "recusa" nos pesos.
- **Análise de logits:** ver as probabilidades de cada token para achar onde ele hesita.

Para melhorar programação, rende muito menos que as seções 2 a 4.

---

## 7. Infraestrutura e velocidade

- **Motor:** Ollama (simples), llama.cpp (controle total), vLLM / SGLang (GPU, alta vazão), MLX (Mac).
- **Hardware:** o que manda é **VRAM** (ou memória unificada) e a banda de memória. CPU pura é de 3 a 5 tokens/s num 8B.
- **Flash attention, batching, cache de prompt:** ganhos de velocidade.
- **Interfaces:** Continue.dev, Aider, Cline, OpenHands, Open WebUI: usam o modelo local como assistente dentro do editor.

---

## 8. Avaliação (sem isso você não sabe se melhorou)

- Conjunto fixo de tarefas com **testes automáticos** (nosso `tests/test_api.py`).
- Métrica: **pass@1** (acerta de primeira) e **pass@k**.
- Benchmarks públicos: HumanEval+, MBPP+, LiveCodeBench, SWE-bench Verified, Aider polyglot.
- Mude **uma coisa por vez** e registre o resultado antes e depois.

---

## Ordem recomendada neste projeto

1. **Baseline** do qwen3:8b cru (em andamento): mede o ponto de partida.
2. **Modelfile + prompt + temperatura baixa:** ganho barato.
3. **Loop de execução e correção + best-of-N:** maior salto por esforço.
4. **RAG** (docs das libs + memória de erros), com chunking por função, embeddings, reranker.
5. **Modelo base maior**, em GPU alugada: qwen3-coder / qwen2.5-coder:32b / gpt-oss.
6. **Dataset por rejection sampling** com os acertos do próprio loop, e depois **LoRA** em GPU de aluguel.
7. **DPO** com os pares certo × errado que o loop já gerou.
8. **GRPO** (RL com testes) só se os passos anteriores estagnarem.

## Realidade do hardware atual

PC: 11,7 GB RAM, sem GPU dedicada: roda 7–8B quantizado, lento. VPS atual: 1,9 GB RAM, sem GPU: só serve para hospedar coisas leves. O teto de qualidade local depende de ter uma GPU com 24 GB ou mais (própria ou alugada).
