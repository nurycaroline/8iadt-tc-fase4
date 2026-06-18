# Fase 3 — Fusão Multimodal e Integração em Nuvem

> Objetivo (o **diferencial** do desafio): combinar as saídas dos modelos num **motor de regras** e disponibilizar tudo como serviço na **nuvem**.

## Resultado esperado (Definition of Done)
- [ ] Motor de fusão retornando o **JSON de risco padronizado**.
- [ ] **Métrica do ganho da fusão** vs. modalidade única documentada.
- [ ] **Alerta em tempo real** chegando ao dashboard (WebSocket/SSE).
- [ ] **Relatório automático** gerado por caso (ver [doc dedicado](06-relatorios-automaticos.md)).
- [ ] API Python (FastAPI) com endpoint de inferência.
- [ ] API Node.js orquestrando upload, Azure Blob e chamada ao Python.
- [ ] Deploy na Azure (App Service / Functions / Container).
- [ ] Pipeline ponta-a-ponta funcionando.

---

## Tarefa 3.1 — Motor de regras clínicas (fusão)
Função em Python que avalia os modelos simultaneamente:

| Evidência | Resultado |
|-----------|-----------|
| Só vídeo detecta sangramento | **Alerta Amarelo (MÉDIO)** |
| Só sinais vitais anômalos | **Alerta Amarelo (MÉDIO)** |
| Vídeo (sangramento) **E** sinais vitais (queda de PA / FHR instável) | **Alerta Vermelho (ALTO) — intervenção imediata** |
| Áudio com risco psicológico/violência | acrescenta contexto e encaminhamento |

- Saída no formato do [contrato-api.md](contrato-api.md).
- Princípio: **a IA não decide tudo sozinha** — a regra de negócio explícita torna o alerta explicável.
- O **texto/NLP** entra como contexto adicional (ex.: laudo confirmando complicação eleva a prioridade).

## Tarefa 3.1b — Métricas da fusão (provar o valor da multimodalidade)
> Este é o diferencial avaliado. Não basta a fusão funcionar; é preciso **mostrar que ela é melhor** que usar uma modalidade só.
- Compare, sobre o mini-dataset, a detecção do evento de risco:
  - usando **só vídeo**, **só sinais vitais**, **só áudio/texto**;
  - usando a **fusão**.
- Reporte precisão, recall e **taxa de falsos positivos** de cada cenário.
- Conclusão esperada: a fusão **reduz falsos positivos** (ex.: sangue sem instabilidade não dispara alerta vermelho) e/ou **aumenta o recall** de casos críticos.
- Coloque essa tabela comparativa no relatório técnico e no vídeo.

## Tarefa 3.2 — Serviço de IA (Python / FastAPI)
- Endpoint `POST /inferencia` recebe URLs/dados, roda os modelos e retorna o JSON de risco.
- `Uvicorn` para servir; `Ultralytics`, `scikit-learn`, `pandas` como dependências.
- Ver exemplo de payload em [contrato-api.md](contrato-api.md).

## Tarefa 3.3 — Backend orquestrador (Node.js / Express)
- `POST /analisar-cirurgia`: recebe upload, envia para o **Azure Blob**, chama o serviço Python (`axios`), grava resultado no banco e dispara alerta.
- `Dotenv` para credenciais; sem segredos no Git.

## Tarefa 3.3b — Alerta em tempo real
> O PDF pede alertar a equipe "em tempo real".
- Implementar **WebSocket** (ex.: `socket.io`) ou **SSE** no backend Node para empurrar o alerta ao dashboard assim que a fusão classificar risco `MÉDIO`/`ALTO`.
- Para a **demonstração**, reproduzir o vídeo cirúrgico com os **sinais vitais rolando em sincronia**, de modo que o alerta apareça no instante exato do evento (usando o mock de sincronização da Fase 1).
- Opcional: notificação adicional (e-mail/Teams) para reforçar o fluxo "alerta à equipe".

## Tarefa 3.3c — Relatório automático
- Após a fusão, gerar o **relatório clínico estruturado** do caso e salvá-lo no Azure Blob.
- Detalhes e template em [docs/06-relatorios-automaticos.md](06-relatorios-automaticos.md).

## Tarefa 3.4 — Infraestrutura Azure
1. Criar conta/recurso no **Microsoft Azure** (tier gratuito).
2. **Azure Blob Storage** para vídeos/frames de alerta.
3. **Deploy** do serviço Python em **Azure App Service**, **Azure Functions** ou **Container Instances**.
4. (Opcional) **Azure Speech / Text Analytics** para o módulo de áudio.

> 💡 Tenha um **fallback local** funcionando para gravar o vídeo de demo, caso a Azure tenha limite/instabilidade na hora.

## Tarefa 3.5 — Teste ponta-a-ponta
- Rodar o pipeline com o mini-dataset (5/5/5).
- Verificar: upload → Blob → inferência → JSON → alerta no dashboard/log.
- Capturar evidências (prints/gravação) para o relatório e o vídeo.

---

## Detalhes de arquitetura
Veja o documento completo de [arquitetura](arquitetura.md) e o [contrato de API](contrato-api.md).
