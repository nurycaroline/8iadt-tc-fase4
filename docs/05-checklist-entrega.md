# Checklist de Entrega

Use este checklist antes de submeter. Cada item corresponde a algo avaliado.

> **Status (Fase 4):** revisado item a item. **Gate verde** num ambiente limpo:
> `ruff check scripts ai-service` ✅ + `pytest` ✅ (**96 testes** Python); `npm run lint` ✅ +
> `npm test` ✅ (**11 testes** Node). Itens marcados `[x]` estão prontos; itens deixados `[ ]` são
> **ação humana** (gravação/publicação do vídeo, nomes dos integrantes) ou **dependentes de ambiente**
> (conta Azure), com justificativa ao lado. Nenhum número foi inventado (`AGENTS.md`).

## Pré-requisitos de ferramentas
- [x] Python: `fastapi`, `uvicorn`, `ultralytics`, `pandas`, `scikit-learn`, `opencv-python`, `joblib`, `pytest` — ver [`ai-service/requirements.txt`](../ai-service/requirements.txt)
- [x] Node.js: `express`, `axios`, `dotenv`, `socket.io` (tempo real), SDK do Azure Storage, `jest` — ver [`backend/package.json`](../backend/package.json)
- [ ] Conta Azure ativa + Blob Storage testado (upload via código funciona) — _ação humana/ambiente; o adaptador Azure existe e a demo roda com **fallback local** (`STORAGE_BACKEND=local`), ver [deploy-azure.md](deploy-azure.md)_
- [x] (Áudio) Whisper ou Azure Speech configurado — `openai-whisper` nas deps; backend trocável por env (degrada sem dados — F2-DD10)
- [x] (Texto) Azure Text Analytics ou classificador de NLP configurado — classificador por regras em [`app/texto/nlp.py`](../ai-service/app/texto/nlp.py)
- [x] Docker + docker-compose instalados — [`docker-compose.yml`](../docker-compose.yml) + Dockerfiles dos dois serviços

## Escopo (requisitos do PDF)
- [x] Pelo menos **2 funcionalidades** implementadas
- [x] Pelo menos **3 objetivos** atendidos
- [x] **Análise de vídeo** com YOLOv8 customizado ✅ obrigatório — _treino **escalado** (GPU/Colab, 41 épocas, mAP@50 0,995, precisão/recall ≈0,99); `best.pt` versionado_
- [x] **Análise de áudio** especializada ✅ obrigatório — _Whisper + trilha **acústica** (Fase 8, F1≈0,94); degrada p/ keywords sem amostras (F2-DD10)_
- [x] **Relatórios automáticos especializados** ✅ obrigatório — [`app/relatorio.py`](../ai-service/app/relatorio.py)
- [x] Modalidade **texto** (laudos/prescrições/evolução) contemplada
- [x] Detecção de anomalias em **tempo real** — socket.io
- [x] Integração com **nuvem (Azure)** — adaptador Azure Blob | local (fallback p/ a demo)

## Técnico
- [x] 4 modelos funcionando individualmente com **métricas** — vitais (F1≈0,62), cicatriz (mAP@50 0,995), texto (depressão F1≈0,93; violência F1=1,0 ⚠️ ver §4.3.1) e áudio acústico (F1≈0,94) com métricas reais
- [x] **Motor de fusão** retornando o JSON padronizado — [`app/fusao.py`](../ai-service/app/fusao.py)
- [x] **Métrica do ganho da fusão** vs. modalidade única — [`models/metricas_fusao.json`](../ai-service/models/metricas_fusao.json)
- [x] **Alerta em tempo real** (WebSocket/SSE) no dashboard — socket.io + cliente mínimo
- [x] **Relatório automático** gerado por caso
- [x] Pipeline **ponta-a-ponta** (upload → IA → alerta) testado — [`scripts/e2e_demo.py`](../scripts/e2e_demo.py)
- [x] Tratamento de **privacidade/LGPD** (sem dados reais no Git, `.env`/Key Vault)

## Qualidade de engenharia
- [x] `docker compose up` sobe a stack
- [x] Testes do **motor de fusão** passando (`pytest`) — 96 testes Python
- [x] **CI** (GitHub Actions) verde no PR — [`.github/workflows/ci.yml`](../.github/workflows/ci.yml)
- [x] Logging com `case_id` rastreável

## Repositório Git
- [x] Estrutura em pastas (`/ai-service`, `/backend`, `/docs`, `/scripts`)
- [x] `requirements.txt` e `package.json` com versões
- [x] `README.md` com instruções de execução
- [x] `.gitignore` (`.env`/chaves fora do Git) — pesos grandes (`best.pt`, `*.joblib`) via **Git LFS**; datasets sintéticos/públicos versionados; guardrail no CI (`check_conformidade.py`)
- [x] **Disclaimer ético** visível — README e relatório técnico

## Relatório técnico
- [x] Descrição do fluxo multimodal (diagrama) — [`relatorio-tecnico.md`](relatorio-tecnico.md) §1
- [x] Modelos por tipo de dado + justificativas — §2
- [x] Lógica de fusão explicada + **métrica do ganho** — §3
- [x] Resultados/métricas + exemplos de anomalias detectadas — §4
- [x] Seção de **privacidade/LGPD** — §5

## Vídeo (máx. 15 min)
> Roteiro pronto em [`roteiro-video.md`](roteiro-video.md); a **gravação/publicação é ação humana** (DD-F4-5).
- [ ] Demonstra análise de áudio **e** vídeo (e texto) — _coberto pelo roteiro (blocos 2–4)_
- [ ] Mostra detecção e resposta a anomalias em tempo real — _roteiro bloco 5/8_
- [ ] Mostra o **relatório automático** gerado — _roteiro bloco 6_
- [ ] Mostra integração Azure — _roteiro bloco 7_
- [ ] Mostra o fluxo final do alerta à equipe médica — _roteiro bloco 8_
- [ ] Publicado no YouTube/Vimeo (público ou **não listado**) — _ação humana_
- [ ] Link do vídeo no README — _placeholder pronto no README; preencher após publicar_

## Antes de submeter
- [x] Rodar o pipeline limpo do zero seguindo só o README — gate verde validado em ambiente limpo
- [x] Conferir que tudo está commitado e no repositório
- [ ] Revisar nome dos integrantes e créditos — _ação humana; tabela de créditos com placeholders no README_
