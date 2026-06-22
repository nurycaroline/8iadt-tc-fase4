# Fase 5 — Produção, Escala e Robustez — Tasks

**Spec**: [`spec.md`](spec.md) · **Doc**: [`docs/08-fase5-producao-e-escala.md`](../../../docs/08-fase5-producao-e-escala.md)
**Status**: **Parcialmente implementada**. Implementado o viável neste ambiente (F5-04, F5-05, F5-06);
F5-01/02/03 ficam **bloqueados por ambiente** (GPU/Colab, datasets com licença, conta Azure) — código
pronto/Azure-ready e degradação documentada (DD10). **Gate verde** em todas as mudanças
(ruff + pytest; eslint + jest [backend]; eslint + vitest + build [frontend]).

> Convenções (`AGENTS.md`): commits atômicos por mudança lógica; nunca inventar métricas; não regredir o
> gate; versões estáveis atuais das dependências.

---

## Implementado

### T1 — Backend: consulta de casos + readiness (F5-04, F5-06)
- **Onde**: `backend/src/rotas/casos.js`, `backend/src/db/repositorios.js`, `backend/src/app.js`.
- **O quê**: `GET /casos`, `GET /casos/:id`, `GET /casos/:id/relatorio` (streama local / redireciona SAS),
  `GET /ready`; app serve `frontend/dist` (SPA) quando existe, com fallback ao cliente mínimo.
- **Done when**: testes `backend/tests/casos.test.js` verdes. ✅ (18 testes Node)

### T2 — Frontend: dashboard React de produção (F5-04)
- **Onde**: `frontend/` (React+Vite+TS, react-router, @tanstack/react-query, socket.io-client).
- **O quê**: telas Dashboard, Pacientes, Dar entrada, Enviar caso, **Detalhe do caso** (painéis por
  modalidade + fusão), Histórico; alerta em tempo real (banner acessível: cor+ícone+texto); estados de
  UI (loading/erro/vazio); disclaimer de apoio à decisão.
- **Done when**: `npm run lint`, `npm test` (vitest), `npm run build` verdes; smoke de serving do backend
  (API + SPA fallback) confirmado. ✅ (7 testes)

### T3 — Reforço dos sinais vitais com pré-eclâmpsia sintética (F5-05)
- **Onde**: `scripts/data_prep/preeclampsia_sintetico.py`, `ai-service/app/sinais_vitais/treino.py`
  (`comparar_com_aumento`), `scripts/reforco_sinais_vitais.py`.
- **O quê**: gerador sintético determinístico (esquema do Maternal Health Risk; hipertensão; rótulo
  `high`); comparação treino base × base+sintéticas (computação real); script que grava
  `models/sinais_vitais/comparacao_preeclampsia.json` (degrada sem o dataset base).
- **Done when**: testes verdes (gerador 4 + comparação 2); script roda e degrada sem o CSV base. ✅

### T4 — Hardening: CI do frontend + Docker/compose (F5-06)
- **Onde**: `.github/workflows/ci.yml` (job `frontend`), `frontend/Dockerfile` + `frontend/nginx.conf`
  (proxy REST + WebSocket), serviço `frontend` no `docker-compose.yml`.
- **Done when**: job de CI definido; imagem do dashboard servível por nginx com proxy ao backend. ✅

### T5 — Documentação + memória
- **Onde**: `docs/08-fase5-producao-e-escala.md`, `spec.md` (traceability), `.specs/project/STATE.md`,
  `README.md`, `frontend/README.md`.
- **Done when**: estado por requisito documentado; itens bloqueados explicados; STATE atualizado. ✅

---

## Bloqueado por ambiente (ação humana / infra)

### T6 — Escalar detector de cicatriz (F5-01) ⛔
- **Bloqueio**: exige **GPU/Colab** + dataset ampliado (AZH Wound + classe de alerta).
- **Desbloqueio**: treinar `app/cicatriz/treino.py` em GPU; validar limiar; `scripts/e2e_demo.py` com
  `caso_alto` deve fechar **ALTO**. Decidir versionamento dos pesos (Git LFS vs. métricas + download).

### T7 — Completar áudio + fisioterapia (F5-02) ⛔
- **Bloqueio**: amostras exigem **login/licença** (Androids/DEPAC; IntelliRehabDS) — obtenção manual.
- **Desbloqueio**: obter dados (`data/README.md`), preparar via `scripts/data_prep/`, rodar baseline e
  publicar métricas; decidir Whisper local vs. Azure Speech.

### T8 — Deploy real na Azure (F5-03) ⛔
- **Bloqueio**: exige **conta/credenciais Azure** (não disponíveis no agente).
- **Desbloqueio**: seguir `docs/deploy-azure.md` (Storage Account + ACI/App Service), rodar o **smoke
  pós-deploy** (`/health`, `POST /analisar`); fallback local mantém paridade.

---

## Gate (status atual)

```
ruff check scripts ai-service        # ✅
pytest -q                            # ✅ (Python: 96 base + 6 da Fase 5)
cd backend && npm run lint && npm test   # ✅ (11 base + 7 da Fase 5 = 18)
cd frontend && npm run lint && npm test && npm run build  # ✅ (7)
```
