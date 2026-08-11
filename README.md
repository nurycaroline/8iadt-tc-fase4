# IA Multimodal para Saúde da Mulher (8IADT)

Solução de IA que faz o **acompanhamento contínuo da mulher no pós-parto** (e gestação avançada): a paciente envia, de casa, **áudio** (relato/consulta), **vídeo** (cicatriz da cesárea), **sinais vitais** (pressão, batimentos, glicemia) e **texto** (laudos/exames). O sistema faz a **fusão multimodal** desses dados para detectar **sinais precoces de risco** e gerar **alertas clínicos em tempo real**.

> ⚠️ **Disclaimer ético.** Esta é uma solução **acadêmica de apoio à decisão clínica**. **Não realiza diagnóstico** nem substitui a avaliação de profissionais de saúde, e **não deve ser usada em ambiente real** sem validação clínica e regulatória adequada. Dados de saúde são **sensíveis** pela LGPD — o repositório usa **apenas dados sintéticos** e os controles de privacidade/segurança estão descritos em [privacidade e segurança (LGPD)](docs/07-privacidade-e-seguranca.md).

## A dor que a solução resolve

No pós-parto a mãe vai para casa e o acompanhamento enfraquece. Sinais de risco (infecção da cicatriz, pré-eclâmpsia, depressão pós-parto, violência) aparecem aos poucos e ficam **espalhados** em sistemas e pessoas diferentes. Quando alguém cruza tudo, a complicação já aconteceu. Esta solução é o "cérebro" que **junta as modalidades da mesma paciente** e **alerta cedo** a equipe.

## O que a solução faz

- **Análise por modalidade:** visão computacional da cicatriz da cesárea (YOLOv8), transcrição e análise de áudio (Whisper + NLP), leitura de sinais vitais e interpretação de texto clínico (laudos/exames).
- **Fusão multimodal:** combina os sinais de todas as modalidades da mesma paciente em um **escore de risco** único (`BAIXO`/`MEDIO`/`ALTO`).
- **Alerta em tempo real:** quando a fusão fecha risco `MEDIO`/`ALTO`, dispara um alerta para a equipe (WebSocket/SSE) e o exibe no dashboard.
- **Dashboard de monitoramento:** lista/entrada de pacientes, envio de caso, detalhe por modalidade e visão da fusão, com alerta ao vivo.
- **Relatórios automáticos:** gera um resumo clínico do caso, exportável para PDF/HTML.
- **Privacidade e segurança (LGPD):** autenticação por chave, TLS na borda, auditoria de acesso, retenção configurável e gestão de segredos fora do código — tudo opt-in, preservando a demo local.

## Como funciona

Três serviços trabalham juntos:

```
frontend/    # Dashboard (React + Vite + TS): monitoramento e alerta em tempo real
backend/     # Orquestrador (Node/Express): upload, storage, persistência, alertas
ai-service/  # Motor de IA (Python/FastAPI): modelos por modalidade, fusão, relatório, métricas
```

O fluxo típico: a paciente/equipe envia um caso pelo **dashboard** → o **backend** guarda os artefatos (storage local) e chama o **motor de IA** → o `ai-service` analisa cada modalidade, faz a **fusão** e devolve o **escore de risco** → o backend **persiste** o resultado e **emite o alerta** em tempo real quando o risco é relevante.

### Estrutura do repositório

```
ai-service/   # Motor de IA (Python/FastAPI): modelos por modalidade, fusão, relatório, métricas
backend/      # Orquestrador (Node/Express): upload, storage, persistência, alerta em tempo real
frontend/     # Dashboard de produção (React+Vite+TS): monitoramento + alerta em tempo real
docs/         # Documentação: arquitetura, contrato de API, relatório técnico, roteiro do vídeo
scripts/      # Preparação de dados, demo E2E e utilitários
data/         # Datasets sintéticos/públicos versionados (rodar/treinar sem baixar); sem dados reais (LGPD)
```

Dependências com **versões fixadas** em [`ai-service/requirements.txt`](ai-service/requirements.txt) (Python) e [`backend/package.json`](backend/package.json) (Node). Os **pesos de modelo** (`best.pt`, `*.joblib`, via **Git LFS**) e os **datasets sintéticos/públicos** são versionados para permitir rodar e retreinar **sem baixar**; **nenhum dado real de paciente** entra no Git — o job "conformidade" do CI garante isso ([`scripts/check_conformidade.py`](scripts/check_conformidade.py)).

## Stack

- **Backend/orquestrador:** Node.js + Express (alerta em tempo real via WebSocket/SSE)
- **Motor de IA:** Python + FastAPI (YOLOv8, scikit-learn, Whisper, NLP de texto)
- **Dashboard:** React + Vite + TypeScript
- **Infra/qualidade:** Docker + docker-compose, testes (pytest/jest), CI (GitHub Actions)

## Como rodar a stack

O resumo abaixo cobre o essencial; o **passo a passo completo** (portas, configuração, dados, testes, solução de problemas) está em [`docs/como-executar.md`](docs/como-executar.md).

### Com Docker (um comando)

```bash
cp .env.example .env          # storage local por padrão
docker compose up --build     # sobe ai-service (8000) e backend (3000)
```

Com `docker compose up` o **dashboard** sobe em `http://localhost:8080/`; o backend também expõe o cliente mínimo de fallback em `http://localhost:3000/`. Envie um caso em `POST /analisar` (ou pela tela "Enviar caso") e veja o alerta surgir quando a fusão fecha o risco `MEDIO`/`ALTO`.

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

> Em produção, o backend serve o build de `frontend/dist`; detalhes em [`frontend/README.md`](frontend/README.md).

### Demo ponta-a-ponta (em processo, sem subir a stack)

```bash
python -m scripts.e2e_demo    # upload local → inferência → JSON de risco → alerta (log)
```

> **Fallback local:** com `STORAGE_BACKEND=local` (padrão) tudo roda em disco, sem serviços externos.

### Privacidade e segurança (LGPD)

Os controles de privacidade/segurança ([`docs/07`](docs/07-privacidade-e-seguranca.md)) são **opt-in por variável de ambiente**, preservando a demo local sem credenciais:

- **Autenticação:** defina `API_KEY` para exigir o header `x-api-key` nas rotas de dados, e `AI_SERVICE_API_KEY` para proteger o `ai-service`. Sem essas variáveis, a demo segue aberta (`/health` e `/ready` são sempre públicos).
- **TLS na borda:** `./scripts/gerar-cert-dev.sh` e `docker compose -f docker-compose.yml -f docker-compose.tls.yml up` (HTTPS em `:8443`, HSTS).
- **Auditoria:** acessos a casos/relatórios e análises ficam na tabela `auditoria` (quem/quando/qual caso). Identidade do chamador via header `x-user-id`.
- **Retenção:** defina `RETENTION_DAYS` e rode `npm run retencao` (no `backend/`) — remove casos e artefatos expirados; `0` (padrão) desabilita.

Todas as variáveis estão documentadas em [`.env.example`](.env.example).

## Documentação

- **[Como executar o projeto](docs/como-executar.md)** — guia detalhado: Docker, local, dados, testes, LGPD.
- **[Aula: o que este projeto ensina](docs/aula-o-que-este-projeto-ensina.md)** — artigo didático para devs fullstack: modelos, stack, dados de treinamento, fusão, MLOps e LGPD.
- [Visão geral e escopo](docs/00-visao-geral-e-escopo.md) · [Casos de uso](docs/casos-de-uso.md) · [Glossário](docs/glossario.md)
- [Arquitetura](docs/arquitetura.md) · [Contrato de API](docs/contrato-api.md) · [Front-end (dashboard)](docs/frontend.md) · [Datasets](docs/datasets.md)
- [Relatórios automáticos](docs/06-relatorios-automaticos.md) · [Privacidade e Segurança (LGPD)](docs/07-privacidade-e-seguranca.md)
- [Qualidade: Docker, testes e CI](docs/qualidade-testes-ci.md) · [Plano de teste manual](docs/plano-de-teste-manual.md)
- **Componentes:** [Motor de IA (`ai-service/`)](ai-service/README.md) · [Backend orquestrador (`backend/`)](backend/README.md) · [Dashboard (`frontend/`)](frontend/README.md)

## Contexto acadêmico

Projeto do curso **Pós-Tech IA para Devs (8IADT) — Tech Challenge Fase 4**. O histórico de planejamento e a divisão do desenvolvimento por fases estão em [`PLANO_DE_DESENVOLVIMENTO.md`](PLANO_DE_DESENVOLVIMENTO.md) e em [`.specs/`](.specs/); os entregáveis (relatório técnico e roteiro do vídeo) estão em [`docs/relatorio-tecnico.md`](docs/relatorio-tecnico.md) e [`docs/roteiro-video.md`](docs/roteiro-video.md).

> ⚠️ Solução acadêmica de **apoio à decisão clínica** — não substitui avaliação médica. Ver [privacidade e segurança](docs/07-privacidade-e-seguranca.md).
