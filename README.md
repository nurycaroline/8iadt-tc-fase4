# Tech Challenge Fase 4 — IA Multimodal para Saúde da Mulher (8IADT)

Solução de IA que faz o **acompanhamento contínuo da mulher no pós-parto** (e gestação avançada): a paciente envia, de casa, **áudio** (relato/consulta), **vídeo** (cicatriz da cesárea e exercícios de fisioterapia), **sinais vitais** (pressão, batimentos, glicemia) e **texto** (laudos/exames). O sistema faz a **fusão multimodal** desses dados para detectar **sinais precoces de risco** e gerar **alertas clínicos em tempo real**, com integração à **nuvem (Azure)**.

> Este repositório começa pela fase de **planejamento**. O plano completo de desenvolvimento, organizado em partes, está em **[`PLANO_DE_DESENVOLVIMENTO.md`](PLANO_DE_DESENVOLVIMENTO.md)**.

## A dor que a solução resolve
No pós-parto a mãe vai para casa e o acompanhamento enfraquece. Sinais de risco (infecção da cicatriz, pré-eclâmpsia, depressão pós-parto, violência) aparecem aos poucos e ficam **espalhados** em sistemas e pessoas diferentes. Quando alguém cruza tudo, a complicação já aconteceu. Esta solução é o "cérebro" que **junta as modalidades da mesma paciente** e **alerta cedo** a equipe.

## Por onde começar
1. Leia o [plano mestre](PLANO_DE_DESENVOLVIMENTO.md).
2. Confirme o escopo em [`docs/00-visao-geral-e-escopo.md`](docs/00-visao-geral-e-escopo.md).
3. Comece a Fase 1 pelo mini-dataset: [`docs/01-fase1-dados.md`](docs/01-fase1-dados.md).

## Documentação
- [Plano de desenvolvimento (índice)](PLANO_DE_DESENVOLVIMENTO.md)
- [Visão geral e escopo](docs/00-visao-geral-e-escopo.md)
- [Fase 1 — Dados](docs/01-fase1-dados.md)
- [Fase 2 — Modelos](docs/02-fase2-modelos.md)
- [Fase 3 — Fusão e Nuvem](docs/03-fase3-fusao-e-nuvem.md)
- [Fase 4 — Entregáveis](docs/04-fase4-entregaveis.md)
- [Casos de uso](docs/casos-de-uso.md) · [Relatórios automáticos](docs/06-relatorios-automaticos.md) · [Privacidade e Segurança (LGPD)](docs/07-privacidade-e-seguranca.md)
- [Motor de IA (`ai-service/`)](ai-service/README.md) — modelos (Fase 2) + fusão/API/relatório (Fase 3)
- [Backend orquestrador (`backend/`)](backend/README.md) — Node/Express, upload, storage, alerta em tempo real
- [Arquitetura](docs/arquitetura.md) · [Front-end (dashboard)](docs/frontend.md) · [Contrato de API](docs/contrato-api.md) · [Datasets](docs/datasets.md)
- [Deploy na Azure](docs/deploy-azure.md) · [Qualidade: Docker, testes e CI](docs/qualidade-testes-ci.md) · [Cronograma por dependências](docs/cronograma-dependencias.md) · [Glossário](docs/glossario.md) · [Checklist](docs/05-checklist-entrega.md)

## Stack prevista
- **Backend/orquestrador:** Node.js + Express (alerta em tempo real via WebSocket/SSE)
- **Motor de IA:** Python + FastAPI (YOLOv8 + YOLOv8-pose, scikit-learn, Whisper/Azure Speech, NLP de texto)
- **Nuvem:** Azure Blob Storage + App Service/Functions
- **Infra/qualidade:** Docker + docker-compose, testes (pytest/jest), CI (GitHub Actions)

## Como rodar a stack (Fase 3)

A stack tem **dois serviços**: o motor de IA (Python/FastAPI) e o orquestrador (Node/Express), que
expõe o cliente mínimo de demonstração do alerta em tempo real.

### Com Docker (um comando)

```bash
cp .env.example .env          # ajuste se for usar Azure; o padrão é storage local
docker compose up --build     # sobe ai-service (8000) e backend (3000)
```

Abra `http://localhost:3000/` (cliente do alerta). Envie um caso em `POST /analisar` e veja o alerta
surgir quando a fusão fecha o risco `MEDIO`/`ALTO`.

### Sem Docker (local)

```bash
# 1) Serviço de IA (Python 3.12+)
python -m venv .venv && source .venv/bin/activate
pip install -r ai-service/requirements.txt
(cd ai-service && uvicorn app.api.main:app --port 8000)

# 2) Backend (Node 20+), em outro terminal
cd backend && npm install && npm start
```

### Demo ponta-a-ponta (em processo, sem subir a stack)

```bash
python -m scripts.e2e_demo    # upload local → inferência → JSON de risco → alerta (log)
```

> **Fallback local:** com `STORAGE_BACKEND=local` (padrão) tudo roda sem a Azure — garante a demo.
> O deploy real na Azure está em [docs/deploy-azure.md](docs/deploy-azure.md).

## Entregáveis da fase
- Repositório Git com código completo
- Relatório técnico
- Vídeo de demonstração (até 15 min)

> ⚠️ Solução acadêmica de **apoio à decisão clínica** — não substitui avaliação médica. Ver [privacidade e segurança](docs/07-privacidade-e-seguranca.md).
