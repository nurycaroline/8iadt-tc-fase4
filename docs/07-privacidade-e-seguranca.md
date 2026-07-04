# Privacidade e Segurança (LGPD)

> O PDF exige "os mais altos padrões de privacidade e segurança para dados sensíveis". Dados de saúde são **dados sensíveis** pela LGPD (Lei 13.709/2018). Esta seção precisa aparecer no relatório técnico.

> ✅ **Fase 7 — implementada.** Os controles técnicos descritos abaixo foram **implementados no código** (antes eram, em parte, aspiracionais): autenticação por credencial de serviço, TLS opt-in na borda, auditoria de acesso, retenção/expiração, pseudonimização reforçada (`case_id` opaco + minimização de PII) e hardening HTTP. Detalhes e rastreabilidade em [`docs/10-fase7-privacidade-e-seguranca.md`](10-fase7-privacidade-e-seguranca.md) e na spec [`.specs/features/fase7-privacidade-e-seguranca/`](../.specs/features/fase7-privacidade-e-seguranca/spec.md). O provisionamento de **RBAC/Private Endpoint reais na Azure** permanece ação humana/infra (depende de conta — F5-03).

## 1. Princípios adotados
- **Minimização:** coletar/usar apenas o necessário para o caso.
- **Anonimização/pseudonimização:** remover identificadores diretos (nome, CPF, prontuário) antes do processamento; usar `case_id` opaco.
- **Finalidade:** dados usados só para o monitoramento clínico.
- **Apoio à decisão, não diagnóstico:** a solução assiste a equipe; a decisão é humana.

## 2. Controles técnicos

| Camada | Controle |
|--------|----------|
| Em trânsito | HTTPS/TLS em todas as chamadas (Node ↔ Python ↔ Azure) |
| Em repouso | Criptografia do Azure Blob (server-side encryption) |
| Segredos | **Azure Key Vault** ou `.env` (nunca no Git); `.gitignore` cobrindo credenciais |
| Acesso | **RBAC** no Azure; SAS tokens com expiração para o Blob |
| Rede | Restringir origem das chamadas ao serviço Python (não expor publicamente sem auth) |
| Auditoria | Log de quem acessou qual caso e quando |
| Retenção | Política de expiração/limpeza de dados após o uso |

## 3. Dados no repositório Git
- **Nunca** versionar dados reais/identificáveis de pacientes da solução.
- Versionar **apenas datasets sintéticos/públicos** (UCI Maternal, AZH Wound, datasets HF traduzidos,
  casos de demo), para permitir rodar e retreinar **sem baixar**. O que entra em `data/` é controlado
  pela **allowlist** de `scripts/check_conformidade.py` (job "conformidade" no CI, F7-08).
- `.env`, chaves e certificados **sempre** fora do Git (o check falha se algum for versionado).
- Pesos de modelo grandes (`best.pt`, `*.joblib`) via **Git LFS** (não dados clínicos).

## 4. Dados sintéticos como estratégia de privacidade
Usar dados sintéticos (o **caso de exemplo** que junta amostras numa paciente fictícia, sinais vitais e áudios em TTS) **resolve dois problemas de uma vez**: viabiliza a demonstração da fusão e elimina o risco de expor paciente real. Cite isso como decisão de privacidade no relatório.

## 5. Disclaimer ético (incluir no README e no relatório)
> Esta é uma solução acadêmica de **apoio à decisão clínica**. Não realiza diagnóstico nem substitui a avaliação de profissionais de saúde. Não deve ser usada em ambiente real sem validação clínica e regulatória adequada.

## 6. Checklist de conformidade
- [x] Nenhum dado real de paciente no repositório — só datasets sintéticos/públicos versionados (allowlist); `.env`/chaves fora do Git; verificação automática no CI (`scripts/check_conformidade.py`, F7-08)
- [x] Credenciais fora do código (Key Vault / `.env`) — `.env` ignorado; carregamento opcional do **Azure Key Vault** com fallback `.env` (`backend/src/seguranca/segredos.js`, F7-07)
- [x] HTTPS/TLS nas integrações — TLS opt-in na borda (`frontend/nginx.tls.conf` + `docker-compose.tls.yml`); Node↔Python aceita `https://`; fallback HTTP documentado (F7-02)
- [x] Blob com criptografia + SAS token com expiração — SAS com `AZURE_SAS_EXPIRY_MINUTES` (`backend/src/storage/azureBlob.js`); criptografia server-side default do Azure
- [x] **Autenticação/restrição de acesso** — credencial de serviço no backend e no `ai-service` (`x-api-key`); `/health`/`/ready` públicos (F7-01)
- [x] **Auditoria de acesso** — trilha "quem/quando/qual caso/ação" (tabela `auditoria`, sem conteúdo clínico) (F7-03)
- [x] **Retenção/expiração** — TTL `RETENTION_DAYS` + rotina `npm run retencao` (F7-04)
- [x] **Pseudonimização** — `case_id` opaco/validado + minimização de PII no payload à IA (`backend/src/seguranca/pseudonimizacao.js`, F7-05)
- [x] **Hardening HTTP** — `helmet`, CORS por allowlist (REST + socket.io), security headers no nginx, validação de MIME no upload (F7-06)
- [x] Disclaimer ético visível — seção dedicada no `README.md` e no relatório técnico
- [x] Seção de privacidade/LGPD no relatório técnico — `docs/relatorio-tecnico.md` §5

> ⚠️ **Permanece ação humana / bloqueado por ambiente:** provisionar **RBAC/Private Endpoint reais na Azure** (depende de conta — F5-03) e **gravar o vídeo** demonstrando os controles (DD-F4-5).
