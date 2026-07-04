# Fase 3 — Fusão Multimodal e Integração em Nuvem

> Objetivo (o **diferencial** do desafio): combinar as saídas dos modelos num **motor de regras** e disponibilizar tudo como serviço na **nuvem**.

## Resultado esperado (Definition of Done)
- [x] Motor de fusão retornando o **JSON de risco padronizado** (`ai-service/app/fusao.py` + `pipeline.py`).
- [x] **Métrica do ganho da fusão** vs. modalidade única documentada (`models/metricas_fusao.json`).
- [x] **Alerta em tempo real** chegando ao cliente (socket.io — `backend/src/realtime/alertas.js`).
- [x] **Relatório automático** gerado por caso (`ai-service/app/relatorio.py`; ver [doc dedicado](06-relatorios-automaticos.md)).
- [x] API Python (FastAPI) com endpoint de inferência (`POST /inferencia` + `/health`).
- [x] API Node.js orquestrando upload, Azure Blob/local e chamada ao Python (`POST /analisar`).
- [~] Deploy na Azure (App Service / Functions / Container) — documentado em [deploy-azure.md](deploy-azure.md); **fallback local** garante a demo.
- [x] Pipeline ponta-a-ponta funcionando (`scripts/e2e_demo.py` + `docker compose up`).

---

## Tarefa 3.1 — Motor de regras clínicas (fusão)
Função em Python que avalia os modelos simultaneamente, **para a mesma paciente**:

| Evidência | Resultado |
|-----------|-----------|
| Só cicatriz com sinal de infecção (vídeo) | **Alerta Amarelo (MÉDIO)** |
| Só sinais vitais de risco (PA alta / classe high risk) | **Alerta Amarelo (MÉDIO)** |
| Cicatriz com infecção **E** sinais vitais/relato de febre/dor | **Alerta Vermelho (ALTO) — risco de infecção puerperal** |
| Sinais vitais de risco **E** áudio/texto com cefaleia/proteinúria | **Alerta Vermelho (ALTO) — risco de pré-eclâmpsia** |
| Áudio com depressão pós-parto persistente | **Amarelo (MÉDIO) — encaminhamento psicológico** |
| Áudio/texto com indício de violência | **Vermelho (ALTO) — protocolo de proteção** |

- Saída no formato do [contrato-api.md](contrato-api.md).
- Princípio: **a IA não decide tudo sozinha** — a regra de negócio explícita torna o alerta explicável.
- O **texto/NLP** entra como contexto adicional (ex.: laudo confirmando proteinúria eleva a prioridade da pré-eclâmpsia).

## Tarefa 3.1b — Métricas da fusão (provar o valor da multimodalidade)
> Este é o diferencial avaliado. Não basta a fusão funcionar; é preciso **mostrar que ela é melhor** que usar uma modalidade só.
- Compare, sobre o mini-dataset / casos de exemplo:
  - usando **só vídeo**, **só sinais vitais**, **só áudio/texto**;
  - usando a **fusão**.
- Reporte precisão, recall e **taxa de falsos positivos** de cada cenário.
- Conclusão esperada: a fusão **reduz falsos positivos** (ex.: vermelhidão leve na cicatriz, sem febre nem PA alta, não dispara alerta vermelho) e/ou **aumenta o recall** de casos críticos.
- Coloque essa tabela comparativa no relatório técnico e no vídeo.

## Tarefa 3.2 — Serviço de IA (Python / FastAPI)
- Endpoint `POST /inferencia` recebe URLs/dados, roda os modelos e retorna o JSON de risco.
- `Uvicorn` para servir; `Ultralytics`, `scikit-learn`, `pandas` como dependências.
- Ver exemplo de payload em [contrato-api.md](contrato-api.md).

## Tarefa 3.3 — Backend orquestrador (Node.js / Express)
- `POST /analisar`: recebe upload, envia para o **Azure Blob**, chama o serviço Python (`axios`), grava resultado no banco e dispara alerta.
- `Dotenv` para credenciais; sem segredos no Git.

## Tarefa 3.3b — Alerta em tempo real
> O PDF pede alertar a equipe "em tempo real".
- Implementar **WebSocket** (ex.: `socket.io`) ou **SSE** no backend Node para empurrar o alerta ao dashboard assim que a fusão classificar risco `MÉDIO`/`ALTO`.
- Para a **demonstração**, processar o **caso de exemplo** de uma paciente e mostrar o alerta surgindo no dashboard no momento em que a fusão fecha o risco.
- Opcional: notificação adicional (e-mail/Teams) para reforçar o fluxo "alerta à equipe".

## Tarefa 3.3c — Relatório automático
- Após a fusão, gerar o **relatório clínico estruturado** do caso e salvá-lo no Azure Blob.
- Detalhes e template em [docs/06-relatorios-automaticos.md](06-relatorios-automaticos.md).

## Tarefa 3.4 — Infraestrutura Azure
1. Criar conta/recurso no **Microsoft Azure** (tier gratuito).
2. **Azure Blob Storage** para vídeos/imagens/relatórios.
3. **Deploy** do serviço Python em **Azure App Service**, **Azure Functions** ou **Container Instances**.
4. (Opcional) **Azure Speech / Text Analytics** para os módulos de áudio e texto.

> 💡 Tenha um **fallback local** funcionando para gravar o vídeo de demo, caso a Azure tenha limite/instabilidade na hora.

## Tarefa 3.5 — Teste ponta-a-ponta
- Rodar o pipeline com o mini-dataset / caso de exemplo.
- Verificar: upload → Blob → inferência → JSON → alerta no dashboard/log.
- Capturar evidências (prints/gravação) para o relatório e o vídeo.

---

## Detalhes de arquitetura
Veja o documento completo de [arquitetura](arquitetura.md) e o [contrato de API](contrato-api.md).
