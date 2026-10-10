# Princípio (REVISADO em 2026-10-10): qualidade alta independentemente do prompt

> **Correção do usuário:** a regra anterior ("o prompt não pode crescer") estava mal entendida. O objetivo é **aumentar absurdamente a qualidade** das IAs locais e gratuitas (um "Claude local"), de modo que o resultado seja bom **qualquer que seja o prompt**: o usuário não deve precisar de um prompt maior ou mais cuidadoso para ter qualidade. O tamanho do prompt não é uma restrição.
>
> Consequências:
> - **Todas as técnicas** do [GUIA_PERSONALIZACAO_IA_LOCAL.md](GUIA_PERSONALIZACAO_IA_LOCAL.md) valem: LoRA, RAG, loop de execução e correção, best-of-N, agente, DPO etc. O loop de correção **volta a contar como melhoria** (é parte do sistema).
> - Cada ciclo: implementar, testar na GPU, avaliar, repetir; sempre com testes automáticos.
> - Passa a medir **robustez ao prompt**: o mesmo problema escrito de formas diferentes (parafraseado, vago, com erros) deve render a mesma qualidade.
> - Restrição de implantação: roda em PC normal (CPU, ~12 GB).

---
## Histórico: versão original deste documento (substituída pela correção acima)
# Princípio: melhorar a IA, não o prompt

## A ideia
O prompt do usuário (`spec/TASK.md`) é **fixo** e entra em **uma única tentativa**. O que evolui é a IA por trás dele.
Se a resposta só melhora quando o prompt cresce (mais regras, mais exemplos, erros colados), o modelo não melhorou: melhorou o prompt.

## Regras do experimento
1. Mesmo prompt, mesmo teste (`tests/test_api.py`, 21 testes), uma geração, sem retry.
2. Cada mudança é uma versão nomeada (`v0` baseline, `v1`...), medida com pass@1 (testes que passam / 21).
3. Mudar **uma coisa por vez** e registrar no quadro de resultados abaixo.
4. O loop "rodar testes → colar erros → regenerar" **não conta como melhoria**: aumenta o prompt. Ele só serve como **gerador de dados** para treino.

## O que vale como "ajuste interno" (prompt do usuário intacto)
| Camada | Técnica | Onde fica | Status |
|---|---|---|---|
| Configuração | System prompt fixo, temperatura, top_p/top_k, repeat_penalty, num_ctx, num_predict | `Modelfile` | v1 |
| Conhecimento | RAG interno: a spec é usada para buscar trechos (docs, código de referência) injetados automaticamente | `rag/` | a fazer |
| Decodificação | Saída estruturada/gramática, best-of-N com seleção automática | harness | a fazer |
| Pesos | LoRA/QLoRA com dataset verificado pelos testes (destilação, rejection sampling) | GPU alugada | a fazer |
| Preferência | DPO com pares "passou × falhou" | GPU alugada | a fazer |
| Modelo | Modelo base maior, quantização maior (Q6/Q8), merge | — | a fazer |

Observação: system prompt e RAG também "aumentam o contexto", mas de forma **embutida na IA**, não no que o usuário digita. A prova de que o ganho é do modelo (e não de um prompt maior) vem do LoRA: quando o ajuste está nos pesos, o prompt pode voltar a ser curto.

## Quadro de resultados (mesmo prompt, 1 tentativa)
| Versão | Mudança | Testes | Obs. |
|---|---|---|---|
| v0 | qwen3:8b cru | 0/21 | FK inexistente em relationship, import circular, header 422 em vez de 401 |
| v1 | Modelfile: system prompt + parâmetros | 0/21 | Corrigiu o import circular (criou database.py), mas **esqueceu de gerar app/models.py**: todos os módulos o importam, então nada carrega. 52 min de geração. System prompt longo + tarefa multi-arquivo = mais chance de omissão entre arquivos. |

### Lições até agora
- Tarefa de 7+ arquivos em tentativa única é grande demais para um 8B na CPU: o erro migra de lugar (v0: bug em models; v1: models ausente) em vez de sumir.
- Cada medição custa 25–50 min. Para iterar de verdade é preciso uma suíte de tarefas pequenas (minutos por teste) e/ou GPU.
- Regras genéricas no system prompt não bastam; o que ensina consistência entre arquivos é treino (LoRA) ou um modelo base maior.

## Gabarito
`reference/` contém a implementação correta (21/21). Serve para validar os testes, alimentar o RAG e gerar dados de treino.
