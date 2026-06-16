# Plano de Desenvolvimento — Tech Challenge Fase 4 (8IADT)

> Solução de **IA Multimodal para Saúde da Mulher**: análise de **vídeo cirúrgico**, **áudio de consultas** e **sinais vitais**, com **fusão multimodal** para gerar alertas clínicos em tempo real, hospedada em **nuvem (Azure)**.

Este documento é o **índice mestre** do plano. Ele resume o escopo, as decisões de projeto e como o trabalho está dividido em partes. Cada parte tem um documento próprio dentro de [`docs/`](docs/).

---

## 1. Como usar este plano

1. Leia esta página inteira (visão geral + decisões de escopo).
2. Siga as fases na ordem. Cada fase tem um arquivo próprio com tarefas, entregáveis e critérios de "pronto".
3. Use o [checklist de entrega](docs/05-checklist-entrega.md) para garantir que nada do que vale nota fica de fora.

### Mapa dos documentos

| Parte | Documento | O que cobre |
|------|-----------|-------------|
| Visão geral | [`docs/00-visao-geral-e-escopo.md`](docs/00-visao-geral-e-escopo.md) | Problema, escopo escolhido, decisões e riscos |
| Fase 1 | [`docs/01-fase1-dados.md`](docs/01-fase1-dados.md) | Aquisição e preparação de dados |
| Fase 2 | [`docs/02-fase2-modelos.md`](docs/02-fase2-modelos.md) | Modelos individuais (vídeo, áudio, sinais vitais) |
| Fase 3 | [`docs/03-fase3-fusao-e-nuvem.md`](docs/03-fase3-fusao-e-nuvem.md) | Fusão multimodal + deploy na nuvem |
| Fase 4 | [`docs/04-fase4-entregaveis.md`](docs/04-fase4-entregaveis.md) | Repositório, relatório técnico e vídeo |
| Componente | [`docs/06-relatorios-automaticos.md`](docs/06-relatorios-automaticos.md) | Relatórios clínicos automáticos (requisito do PDF) |
| Componente | [`docs/07-privacidade-e-seguranca.md`](docs/07-privacidade-e-seguranca.md) | Privacidade, segurança e LGPD |
| Apoio | [`docs/arquitetura.md`](docs/arquitetura.md) | Arquitetura de software (Node + Python + Azure) |
| Apoio | [`docs/frontend.md`](docs/frontend.md) | Dashboard de monitoramento (front-end) |
| Apoio | [`docs/contrato-api.md`](docs/contrato-api.md) | Contrato de API entre serviços |
| Apoio | [`docs/datasets.md`](docs/datasets.md) | Datasets recomendados e como obtê-los |
| Apoio | [`docs/qualidade-testes-ci.md`](docs/qualidade-testes-ci.md) | Docker, testes automatizados e CI |
| Apoio | [`docs/cronograma-dependencias.md`](docs/cronograma-dependencias.md) | Caminho crítico e o que paralelizar |
| Apoio | [`docs/glossario.md`](docs/glossario.md) | Glossário clínico e técnico |
| Apoio | [`docs/05-checklist-entrega.md`](docs/05-checklist-entrega.md) | Checklist final de avaliação |

---

## 2. O que o desafio exige (resumo do PDF)

O Tech Challenge pede uma solução de IA que monitore pacientes por **dados multimodais (áudio, vídeo e texto)** para identificar sinais precoces de risco em saúde da mulher.

- **Funcionalidades** — escolher **pelo menos 2**.
- **Objetivos** — escolher **pelo menos 3**.
- **Entregas técnicas obrigatórias** — o PDF lista, em "Requisitos obrigatórios":
  1. **Análise de Vídeo Especializada** (YOLOv8 customizado + relatórios automáticos).
  2. **Análise de Áudio Especializada** (consultas, pré-natal, pós-parto, vítimas de violência).
- **Entregáveis da fase**: repositório Git completo, relatório técnico e vídeo de até 15 min.

> ⚠️ **Atenção (gap identificado):** as anotações iniciais focavam em **Vídeo + Sinais Vitais** e **não incluíam Áudio**. Como o PDF lista **Áudio** entre as entregas técnicas obrigatórias, este plano **inclui um módulo de áudio** (mesmo que enxuto) para reduzir risco de perda de nota. Veja a decisão em [`docs/00-visao-geral-e-escopo.md`](docs/00-visao-geral-e-escopo.md).

---

## 3. Escopo escolhido (decisão de projeto)

Para manter o projeto realista e com forte "fusão multimodal" (que é o diferencial avaliado), o escopo recomendado é:

**Cenário clínico central:** *Hemorragia / complicação em cirurgia ginecológica-obstétrica, com paciente sob vigilância de sinais vitais e histórico de consulta.*

**4 modalidades implementadas (áudio, vídeo, sinais vitais e texto):**
1. **Vídeo** — YOLOv8 detecta sangramento/anatomia/instrumentos em vídeo cirúrgico.
2. **Sinais vitais** — modelo clássico (Random Forest / Isolation Forest) detecta anomalia (queda de PA, FHR fora da faixa).
3. **Áudio** — transcrição + classificação de sinais de risco psicológico/violência em áudio de consulta.
4. **Texto/NLP** — análise de laudos, prescrições hormonais e evolução clínica (fecha a tríade "áudio, vídeo e texto" do enunciado).

**Fusão multimodal (o "pulo do gato"):** um motor de regras combina os sinais e classifica o risco em `BAIXO / MÉDIO / ALTO`, disparando **alerta em tempo real** (WebSocket/SSE) para a equipe e gerando um **relatório automático**.

**Mapeamento de requisitos:** ver tabela completa em [`docs/00-visao-geral-e-escopo.md`](docs/00-visao-geral-e-escopo.md).

---

## 4. Arquitetura em uma frase

**Node.js** (orquestrador: upload, API, banco, dashboard, Azure Blob) **+** **Python/FastAPI** (motor de IA: YOLO, sinais vitais, áudio) **+** **Azure** (Blob Storage + hospedagem). Detalhes em [`docs/arquitetura.md`](docs/arquitetura.md).

```
Usuário → API Node.js → Azure Blob (armazena) → chama Serviço Python (FastAPI)
                                                      ↓
                    YOLO + Sinais Vitais + Áudio + Texto → Fusão → JSON + Relatório
                                                      ↓
              Node grava no banco → Dashboard (alerta em tempo real via WebSocket)
```

---

## 5. Fases em ordem (visão macro)

| Fase | Objetivo | Resultado "pronto" |
|------|----------|--------------------|
| **1 — Dados** | Obter e preparar mini-datasets de vídeo, sinais vitais e áudio | Dados limpos e anotados para começar a treinar |
| **2 — Modelos** | Treinar/validar cada IA isoladamente | 3 modelos funcionando individualmente com métricas |
| **3 — Fusão + Nuvem** | Motor de regras + API + deploy Azure | Pipeline ponta-a-ponta rodando na nuvem |
| **4 — Entregáveis** | Repo, relatório e vídeo | Tudo pronto para submissão |

> **Princípio guia:** comece com um **mini-dataset** (5 vídeos, 5 planilhas, 5 áudios) e faça o pipeline rodar ponta-a-ponta. "Se rodar com 5, roda com 500." Só depois escale.

---

## 6. Estrutura de repositório recomendada

```
.
├── README.md                  # Como rodar a solução
├── PLANO_DE_DESENVOLVIMENTO.md
├── docker-compose.yml         # Sobe Node + Python com um comando
├── .github/workflows/ci.yml   # Lint + testes a cada push
├── docs/                      # Este plano (por partes) + relatório técnico
├── ai-service/                # Python / FastAPI (YOLO, vitais, áudio, texto, fusão)
│   ├── app/
│   ├── models/                # Pesos treinados (.pt / .onnx) — usar Git LFS
│   ├── notebooks/             # Treino e EDA
│   ├── tests/                 # pytest (foco no motor de fusão)
│   ├── Dockerfile
│   └── requirements.txt
├── backend/                   # Node.js / Express (orquestrador + Azure)
│   ├── src/
│   ├── tests/                 # jest
│   ├── Dockerfile
│   └── package.json
├── frontend/                  # Dashboard React (tempo real) — ver docs/frontend.md
│   ├── src/
│   └── package.json
├── data/                      # Mini-dataset (NÃO versionar dados grandes/sensíveis)
└── scripts/                   # Geração de dados sintéticos, conversões
```

> ⚖️ **Privacidade:** dados médicos são sensíveis. Não versione dados reais de pacientes. Use `.gitignore` para `data/` e variáveis de ambiente (`.env`) para credenciais da Azure.

---

## 7. Próximo passo imediato

1. Ler [`docs/00-visao-geral-e-escopo.md`](docs/00-visao-geral-e-escopo.md) e confirmar o escopo com o grupo.
2. Dividir as fases entre os integrantes (sugestão de divisão no doc da Fase 4).
3. Começar a Fase 1 pelo **mini-dataset** — ver [`docs/01-fase1-dados.md`](docs/01-fase1-dados.md).
