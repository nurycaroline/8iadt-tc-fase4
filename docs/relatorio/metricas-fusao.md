# Métrica do ganho da fusão — tabela legível

> Versão legível de [`ai-service/models/metricas_fusao.json`](../../ai-service/models/metricas_fusao.json)
> (gerado por [`ai-service/app/metricas_fusao.py`](../../ai-service/app/metricas_fusao.py)). **Os números
> abaixo reproduzem exatamente** o arquivo de origem — nenhum valor foi alterado (princípio "nunca
> inventar", `AGENTS.md`).

## Cenário de avaliação

Conjunto sintético rotulado de **6 casos** (`crítico` = exige alerta vermelho), definido em
`app.metricas_fusao.casos_avaliacao()`. Inclui 3 casos críticos que **exigem corroboração multimodal**
(infecção puerperal, pré-eclâmpsia, violência) e 3 "quase-alertas"/normais isolados (vermelhidão leve
isolada, ansiedade isolada, tudo normal) que **não** devem disparar o vermelho.

- **Modalidade única** prediz "crítico" quando a fusão **restrita àquela modalidade** sai do `BAIXO`
  (qualquer sinal de risco isolado) — comportamento conservador que gera falsos positivos.
- **Fusão** prediz "crítico" apenas quando o risco combinado é `ALTO` (há corroboração entre modalidades).

## Comparativo (n = 6)

| Cenário                | Precisão | Recall  | Taxa de FP | TP | FP | FN | TN |
| ---------------------- | -------- | ------- | ---------- | -- | -- | -- | -- |
| Só vídeo               | 0,50     | 0,3333  | 0,3333     | 1  | 1  | 2  | 2  |
| Só sinais vitais       | 1,00     | 0,6667  | 0,00       | 2  | 0  | 1  | 3  |
| Só áudio/texto         | 0,6667   | 0,6667  | 0,3333     | 2  | 1  | 1  | 2  |
| **Fusão multimodal**   | **1,00** | **1,00**| **0,00**   | 3  | 0  | 0  | 3  |

## Conclusão

A **fusão** atinge **recall 1,0** (não perde nenhum dos 3 casos críticos) com **taxa de falsos positivos
0,0** — superando todas as modalidades isoladas, que ou perdem casos (recall ≤ 0,67) ou geram falsos
positivos (FP até 0,33). O ganho vem de **exigir corroboração** entre modalidades antes do alerta
vermelho, em vez de reagir a qualquer sinal isolado. É a evidência direta do **diferencial da fusão**
(requisito do PDF: "métrica do ganho da fusão vs. modalidade única").
