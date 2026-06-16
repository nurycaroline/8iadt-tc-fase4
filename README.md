# Tech Challenge Fase 4 — IA Multimodal para Saúde da Mulher (8IADT)

Solução de IA que analisa **vídeo cirúrgico**, **áudio de consultas** e **sinais vitais**, e faz a **fusão multimodal** desses dados para gerar **alertas clínicos em tempo real**, com integração à **nuvem (Azure)**.

> Este repositório começa pela fase de **planejamento**. O plano completo de desenvolvimento, organizado em partes, está em **[`PLANO_DE_DESENVOLVIMENTO.md`](PLANO_DE_DESENVOLVIMENTO.md)**.

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
- [Arquitetura](docs/arquitetura.md) · [Contrato de API](docs/contrato-api.md) · [Datasets](docs/datasets.md) · [Checklist](docs/05-checklist-entrega.md)

## Stack prevista
- **Backend/orquestrador:** Node.js + Express
- **Motor de IA:** Python + FastAPI (YOLOv8, scikit-learn, Whisper/Azure Speech)
- **Nuvem:** Azure Blob Storage + App Service/Functions

## Entregáveis da fase
- Repositório Git com código completo
- Relatório técnico
- Vídeo de demonstração (até 15 min)
