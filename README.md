# Tech Challenge Fase 4 — IA Multimodal para Saúde da Mulher (8IADT)

Solução de IA que faz o **acompanhamento contínuo da mulher no pós-parto** (e gestação avançada): a paciente envia, de casa, **áudio** (relato/consulta), **vídeo** (cicatriz da cesárea e exercícios de fisioterapia), **sinais vitais** (pressão, batimentos, glicemia) e **texto** (laudos/exames). O sistema faz a **fusão multimodal** desses dados para detectar **sinais precoces de risco** e gerar **alertas clínicos em tempo real**, com integração à **nuvem (Azure)**.

> Projeto **implementado de ponta a ponta** (Fases 1–4): dados → modelos → fusão → API → alerta em tempo real → relatório automático, com Docker, testes e CI. Para rodar do zero, vá direto para **[Como rodar a stack](#como-rodar-a-stack)**. O histórico de planejamento por fases está em **[`PLANO_DE_DESENVOLVIMENTO.md`](PLANO_DE_DESENVOLVIMENTO.md)** e em [`.specs/`](.specs/).

> ⚠️ **Disclaimer ético.** Esta é uma solução **acadêmica de apoio à decisão clínica**. **Não realiza diagnóstico** nem substitui a avaliação de profissionais de saúde, e **não deve ser usada em ambiente real** sem validação clínica e regulatória adequada. Dados de saúde são **sensíveis** pela LGPD — o repositório usa **apenas dados sintéticos** e os controles de privacidade/segurança estão descritos em [privacidade e segurança (LGPD)](docs/07-privacidade-e-seguranca.md).

## Estrutura do repositório

```
ai-service/   # Motor de IA (Python/FastAPI): modelos por modalidade, fusão, relatório, métricas
backend/      # Orquestrador (Node/Express): upload, storage, persistência, alerta em tempo real
frontend/     # Dashboard de produção (React+Vite+TS): monitoramento + alerta em tempo real (Fase 5)
docs/         # Documentação: arquitetura, contrato de API, relatório técnico, roteiro do vídeo
scripts/      # Preparação de dados (Fase 1), demo E2E e utilitários
data/         # Estrutura de dados (conteúdo ignorado pelo Git — LGPD); só metadados leves versionados
```

Dependências com **versões fixadas** em [`ai-service/requirements.txt`](ai-service/requirements.txt) (Python) e
[`backend/package.json`](backend/package.json) (Node). Pesos de modelo **não são versionados** (reprodutíveis
pelo treino); só **métricas** e gráficos entram no Git — ver [`.gitignore`](.gitignore) e
[privacidade/LGPD](docs/07-privacidade-e-seguranca.md).

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
- [Fase 5 — Produção, Escala e Robustez](docs/08-fase5-producao-e-escala.md) _(dashboard, reforço de vitais, hardening)_
- **[Relatório técnico](docs/relatorio-tecnico.md)** (6 seções) · **[Roteiro do vídeo](docs/roteiro-video.md)** (≤15 min) · [Evidências consolidadas](docs/relatorio/)
- [Fase 6 — Relatórios Automáticos](docs/09-fase6-relatorios-automaticos.md) · [Fase 7 — Privacidade e Segurança (LGPD)](docs/10-fase7-privacidade-e-seguranca.md) _(auth, TLS, auditoria, retenção, hardening)_
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

## Como rodar a stack

A stack tem **dois serviços**: o motor de IA (Python/FastAPI) e o orquestrador (Node/Express), que
expõe o cliente mínimo de demonstração do alerta em tempo real.

### Com Docker (um comando)

```bash
cp .env.example .env          # ajuste se for usar Azure; o padrão é storage local
docker compose up --build     # sobe ai-service (8000) e backend (3000)
```

Com `docker compose up` o **dashboard** (Fase 5) sobe em `http://localhost:8080/`; o backend também
expõe o cliente mínimo de fallback em `http://localhost:3000/`. Envie um caso em `POST /analisar` (ou pela
tela "Enviar caso") e veja o alerta surgir quando a fusão fecha o risco `MEDIO`/`ALTO`.

### Sem Docker (local)

```bash
# 1) Serviço de IA (Python 3.12+)
python -m venv .venv && source .venv/bin/activate
pip install -r ai-service/requirements.txt
(cd ai-service && uvicorn app.api.main:app --port 8000)

# 2) Backend (Node 20+), em outro terminal
cd backend && npm install && npm start

# 3) Dashboard (React), em outro terminal — proxy automático para o backend
cd frontend && npm install && npm run dev   # http://localhost:5173
```

> **Dashboard (Fase 5):** painel de monitoramento com lista/entrada de pacientes, upload do caso,
> **detalhe do caso** (painéis por modalidade + fusão) e **alerta em tempo real**. Em produção, o backend
> serve o build de `frontend/dist`; detalhes em [`frontend/README.md`](frontend/README.md).

### Demo ponta-a-ponta (em processo, sem subir a stack)

```bash
python -m scripts.e2e_demo    # upload local → inferência → JSON de risco → alerta (log)
```

> **Fallback local:** com `STORAGE_BACKEND=local` (padrão) tudo roda sem a Azure — garante a demo.
> O deploy real na Azure está em [docs/deploy-azure.md](docs/deploy-azure.md).

### Privacidade e segurança (Fase 7 — LGPD)

Os controles de privacidade/segurança ([`docs/07`](docs/07-privacidade-e-seguranca.md)) são **opt-in por
variável de ambiente**, preservando a demo local sem credenciais:

- **Autenticação (F7-01):** defina `API_KEY` para exigir o header `x-api-key` nas rotas de dados, e
  `AI_SERVICE_API_KEY` para proteger o `ai-service`. Sem essas variáveis, a demo segue aberta (`/health` e
  `/ready` são sempre públicos).
- **TLS na borda (F7-02):** `./scripts/gerar-cert-dev.sh` e
  `docker compose -f docker-compose.yml -f docker-compose.tls.yml up` (HTTPS em `:8443`, HSTS).
- **Auditoria (F7-03):** acessos a casos/relatórios e análises ficam na tabela `auditoria` (quem/quando/qual
  caso). Identidade do chamador via header `x-user-id`.
- **Retenção (F7-04):** defina `RETENTION_DAYS` e rode `npm run retencao` (no `backend/`) — remove casos e
  artefatos expirados; `0` (padrão) desabilita.
- **Segredos (F7-07):** defina `AZURE_KEY_VAULT_URL` para carregar segredos do Azure Key Vault (fallback
  `.env`).

Todas as variáveis estão documentadas em [`.env.example`](.env.example).

## Entregáveis da fase (Fase 4)
- **Repositório Git** com código completo (este repo) — estrutura, deps fixadas, Docker, testes e CI.
- **Relatório técnico:** [`docs/relatorio-tecnico.md`](docs/relatorio-tecnico.md) (6 seções) — exportável
  para PDF/HTML via `python -m scripts.exportar_relatorio` (fallback HTML quando faltam libs de PDF).
- **Vídeo de demonstração (≤ 15 min):** roteiro pronto em [`docs/roteiro-video.md`](docs/roteiro-video.md).
  - 🎬 **Link do vídeo:** _[a publicar — YouTube/Vimeo "Não listado"; substituir este placeholder pelo link]_

## Créditos / Integrantes

> Preencha os integrantes do grupo antes de submeter (não invente nomes).

| Nome | RM | GitHub |
| ---- | -- | ------ |
| _\<preencher\>_ | _\<preencher\>_ | _\<preencher\>_ |
| _\<preencher\>_ | _\<preencher\>_ | _\<preencher\>_ |
| _\<preencher\>_ | _\<preencher\>_ | _\<preencher\>_ |

Curso: Pós-Tech IA para Devs (8IADT) — Tech Challenge Fase 4.

> ⚠️ Solução acadêmica de **apoio à decisão clínica** — não substitui avaliação médica. Ver [privacidade e segurança](docs/07-privacidade-e-seguranca.md).
