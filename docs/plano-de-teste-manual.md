# Plano de Teste Manual — IA Multimodal para Saúde da Mulher

> Roteiro de **validação manual (UAT)** de ponta a ponta das Fases 1–7. Complementa os testes
> automatizados (`pytest`, `jest`, `vitest`) descritos em
> [`qualidade-testes-ci.md`](qualidade-testes-ci.md): aqui o foco é **verificação humana** do
> comportamento observável (telas, API, alertas, relatórios e controles de LGPD).

> ⚠️ **Dados sintéticos apenas.** Todos os cenários usam o mini-dataset/casos sintéticos do
> repositório. **Nunca** use dados reais de pacientes (ver
> [privacidade e segurança](07-privacidade-e-seguranca.md)).

## Sumário

- [1. Objetivo e escopo](#1-objetivo-e-escopo)
- [2. Pré-requisitos e preparação do ambiente](#2-pré-requisitos-e-preparação-do-ambiente)
- [3. Como usar este plano](#3-como-usar-este-plano)
- [4. Suíte A — Ambiente e dados (Fase 1)](#4-suíte-a--ambiente-e-dados-fase-1)
- [5. Suíte B — Modelos por modalidade (Fase 2)](#5-suíte-b--modelos-por-modalidade-fase-2)
- [6. Suíte C — Fusão, API, nuvem e tempo real (Fase 3)](#6-suíte-c--fusão-api-nuvem-e-tempo-real-fase-3)
- [7. Suíte D — Entregáveis e relatório técnico (Fase 4)](#7-suíte-d--entregáveis-e-relatório-técnico-fase-4)
- [8. Suíte E — Dashboard de produção (Fase 5)](#8-suíte-e--dashboard-de-produção-fase-5)
- [9. Suíte F — Relatórios automáticos especializados (Fase 6)](#9-suíte-f--relatórios-automáticos-especializados-fase-6)
- [10. Suíte G — Privacidade e segurança / LGPD (Fase 7)](#10-suíte-g--privacidade-e-segurança--lgpd-fase-7)
- [11. Suíte H — Regressão de gate (testes automatizados)](#11-suíte-h--regressão-de-gate-testes-automatizados)
- [12. Matriz de rastreabilidade (requisito → teste)](#12-matriz-de-rastreabilidade-requisito--teste)
- [13. Registro de execução e sign-off](#13-registro-de-execução-e-sign-off)

---

## 1. Objetivo e escopo

Validar manualmente que a solução cumpre os requisitos do desafio em um ambiente limpo:

- **Funcional:** upload multimodal → inferência por modalidade → fusão → JSON de risco padronizado →
  alerta em tempo real → relatório automático.
- **Não funcional:** reprodutibilidade (`docker compose up`), degradação graciosa sem dados/credenciais
  (fallback local) e controles de privacidade/segurança (LGPD) **opt-in** da Fase 7.

**Fora de escopo (ação humana / ambiente):** provisionamento real de RBAC/Private Endpoint na Azure e
gravação/publicação do vídeo. Onde aplicável, validamos apenas o **fallback local** e a documentação.

## 2. Pré-requisitos e preparação do ambiente

| Ferramenta | Versão mínima | Observação |
|------------|---------------|------------|
| Python | 3.12+ | serviço de IA + scripts |
| Node.js | 20+ | backend e frontend |
| Docker + Docker Compose | atual | suíte com a stack containerizada |
| Navegador | atual | dashboard e cliente de tempo real |

> Detalhes completos de instalação e execução em [`como-executar.md`](como-executar.md). Antes de iniciar,
> rode `cp .env.example .env` na raiz.

**Dados de teste.** Os casos sintéticos `data/casos/caso_baixo.json`, `caso_medio.json` e `caso_alto.json`
já estão versionados. Artefatos pesados (imagens/áudio/vídeo) **não** ficam no Git; gere o mini-dataset com:

```bash
pip install -r scripts/requirements-data.txt
python -m scripts.data_prep
```

> Áudio pode aparecer como `FALHOU`/`nao_avaliado` se as amostras manuais não forem colocadas em
> `data/audio/` — esse é o comportamento esperado de **degradação graciosa** (DD10) e é validado
> nos casos C-04 e B-04.

## 3. Como usar este plano

Cada caso de teste segue o formato:

- **ID** — identificador estável (ex.: `C-03`).
- **Objetivo** — o que se valida.
- **Pré-condições** — estado necessário antes de começar.
- **Passos** — ações a executar, na ordem.
- **Resultado esperado** — critério objetivo de aprovação.

Registre o resultado (`PASSOU` / `FALHOU` / `N/A`) na [seção 13](#13-registro-de-execução-e-sign-off).
Um caso só é `PASSOU` quando **todos** os critérios do resultado esperado forem atendidos.

---

## 4. Suíte A — Ambiente e dados (Fase 1)

### A-01 — Preparação do mini-dataset
- **Objetivo:** confirmar que o pipeline de dados gera a estrutura esperada sem dados reais.
- **Pré-condições:** repositório clonado; `.env` criado; `scripts/requirements-data.txt` instalado.
- **Passos:**
  1. Rode `python -m scripts.data_prep`.
  2. Inspecione `data/` (ex.: `data/sinais_vitais/`, `data/video_cicatriz/`, `data/texto_clinico/`).
- **Resultado esperado:** o comando conclui (modalidades sem fonte podem reportar `FALHOU`, o que é
  aceitável); são criados artefatos de sinais vitais, cicatriz (YOLO) e texto; nenhum dado real de
  paciente é baixado.

### A-02 — Casos sintéticos versionados
- **Objetivo:** garantir que os três casos de demonstração existem e são coerentes.
- **Pré-condições:** repositório clonado.
- **Passos:** abra `data/casos/caso_baixo.json`, `caso_medio.json` e `caso_alto.json`.
- **Resultado esperado:** cada arquivo referencia modalidades coerentes com o nível de risco (ex.:
  `caso_alto` com cicatriz em alerta + sinais vitais alterados + texto de infecção).

### A-03 — `.gitignore` protege dados sensíveis
- **Objetivo:** confirmar que conteúdo de `data/` e `.env` não vão para o Git.
- **Pré-condições:** mini-dataset gerado (A-01).
- **Passos:** rode `git status --porcelain` na raiz.
- **Resultado esperado:** arquivos de mídia/áudio/vídeo gerados e o `.env` **não** aparecem como
  versionáveis; apenas metadados leves (ex.: `data/casos/*.json`, `data/**/data.yaml`) seriam rastreados.

---

## 5. Suíte B — Modelos por modalidade (Fase 2)

> Estes casos validam cada modelo isoladamente. Podem ser executados via REPL Python a partir de
> `ai-service/` ou observados no detalhe do caso do dashboard (Suíte E).

### B-01 — Sinais vitais (classificação de risco)
- **Objetivo:** validar a inferência de pressão arterial/risco.
- **Pré-condições:** `pip install -r ai-service/requirements.txt`; modelo treinado
  (`python -m app.sinais_vitais.treino` em `ai-service/`) ou uso dos limiares.
- **Passos:** com um registro de PA elevada (ex.: sistólica ≥ 140 / diastólica ≥ 90), chame
  `app.sinais_vitais.inferencia.prever(registro)`.
- **Resultado esperado:** retorna `{tipo, valor}` com `tipo` indicando risco (ex.: `hipertensao` /
  `risco_medio`) e `valor` no formato `"150/95"`.

### B-02 — Cicatriz (detecção YOLOv8)
- **Objetivo:** validar a detecção de sinal de infecção na cicatriz.
- **Pré-condições:** pesos da cicatriz disponíveis (`python -m app.cicatriz.treino`) ou imagem de exemplo.
- **Passos:** chame `app.cicatriz.inferencia.detectar(imagem)` com uma imagem `ferida_alerta`.
- **Resultado esperado:** retorna `{evento, confianca}` com `evento` em
  `ferida_ok|sinal_infeccao|nenhum` e `confianca` entre 0 e 1.

### B-03 — Texto / NLP (achado clínico)
- **Objetivo:** validar a extração de achado em texto clínico.
- **Pré-condições:** ambiente Python do `ai-service`.
- **Passos:** passe um texto com palavras-chave de infecção (ex.: "febre, dor e secreção na cicatriz") ao
  classificador `app/texto/nlp.py`.
- **Resultado esperado:** retorna `{achado, trecho}` com `achado` em `complicacao|sinal_infeccao|neutro`
  e `trecho` citando o texto-fonte.

### B-04 — Áudio (transcrição + classificação)
- **Objetivo:** validar a categorização do relato em áudio.
- **Pré-condições:** amostra de áudio em `data/audio/` (opcional).
- **Passos:** execute a classificação de áudio sobre uma amostra rotulada.
- **Resultado esperado:** com amostra, retorna `{categoria, confianca}` (ex.: `depressao_pos_parto`,
  `violencia`, `ansiedade`); **sem** amostra, a modalidade degrada graciosamente (omitida), sem quebrar.

### B-05 — Métricas por modalidade existem
- **Objetivo:** confirmar que métricas reais estão versionadas (sem números inventados).
- **Pré-condições:** repositório clonado.
- **Passos:** abra `ai-service/models/baseline.json`, `ai-service/models/cicatriz/metrics.json` e
  `ai-service/models/sinais_vitais/metrics.json`.
- **Resultado esperado:** arquivos existem e contêm métricas (precisão/recall/mAP conforme a modalidade).

---

## 6. Suíte C — Fusão, API, nuvem e tempo real (Fase 3)

### C-01 — Health checks dos serviços
- **Objetivo:** confirmar que ambos os serviços sobem e respondem.
- **Pré-condições:** stack no ar (`docker compose up --build`).
- **Passos:**
  1. `curl http://localhost:8000/health`
  2. `curl http://localhost:3000/health`
  3. `curl http://localhost:3000/ready`
- **Resultado esperado:** `/health` retorna `{"status":"ok"}` em ambos; `/ready` retorna `ready` com o
  backend de storage indicado (ou `503` se dependência indisponível).

### C-02 — Contrato da API `/inferencia` (caso ALTO)
- **Objetivo:** validar a resposta padronizada do `ai-service` (contrato §2).
- **Pré-condições:** `ai-service` no ar; mini-dataset gerado.
- **Passos:** envie `POST http://localhost:8000/inferencia` com um corpo apontando para o `caso_alto`
  (cicatriz em alerta + vitais + texto de infecção).
- **Resultado esperado:** HTTP 200 com `risco_detectado: "ALTO"`, bloco `evidencias` por modalidade,
  `mensagem_alerta` preenchida e `relatorio_url` (ou `null` se a geração degradar).

### C-03 — Demo ponta-a-ponta em processo
- **Objetivo:** validar o fluxo upload local → IA → JSON → alerta sem subir a stack HTTP.
- **Pré-condições:** ambiente Python; `STORAGE_BACKEND=local` (padrão).
- **Passos:**
  1. `python -m scripts.e2e_demo`
  2. `python -m scripts.e2e_demo --caso caso_medio`
  3. `python -m scripts.e2e_demo --caso caso_baixo`
- **Resultado esperado:** cada execução imprime o JSON de risco coerente (`ALTO`/`MEDIO`/`BAIXO`) e o log
  de alerta simulado; `caso_baixo` **não** dispara alerta.

### C-04 — Fusão eleva o risco vs. modalidade única
- **Objetivo:** validar que a fusão agrega valor (o cerne do projeto).
- **Pré-condições:** ambiente Python.
- **Passos:** abra `ai-service/models/metricas_fusao.json` (ou rode `python -m app.metricas_fusao` em
  `ai-service/`) e compare `fusao` com `so_video`/`so_vitais`/`so_audio_texto`.
- **Resultado esperado:** a coluna `fusao` apresenta precisão/recall **iguais ou superiores** às
  modalidades isoladas no conjunto sintético, evidenciando o ganho da fusão.

### C-05 — Fluxo HTTP completo `POST /analisar`
- **Objetivo:** validar upload → storage → IA → persistência → resposta.
- **Pré-condições:** stack no ar; existe um paciente cadastrado (ver E-02) cujo `id` será usado.
- **Passos:** envie `POST http://localhost:3000/analisar` (multipart) com `paciente_id` e ao menos
  `texto_clinico` com palavras de infecção; opcionalmente anexe um CSV de sinais vitais.
- **Resultado esperado:** HTTP 200 com o JSON de risco + `caso_id`; o caso fica persistido (visível em
  `GET /casos`).

### C-06 — Alerta em tempo real (cliente mínimo)
- **Objetivo:** validar a emissão do evento `alerta` por WebSocket.
- **Pré-condições:** stack no ar; abrir `http://localhost:3000/` (cliente socket.io de demonstração).
- **Passos:** com a página aberta, dispare um caso de risco `MEDIO`/`ALTO` via `POST /analisar` (C-05).
- **Resultado esperado:** o cliente recebe o evento `alerta` com `case_id`, `risco_detectado`,
  `mensagem_alerta` e dados mínimos do paciente; **caso BAIXO não** gera alerta.

### C-07 — Fallback de storage local (sem Azure)
- **Objetivo:** garantir que a demo roda sem credenciais de nuvem.
- **Pré-condições:** `.env` com `STORAGE_BACKEND=local` (padrão).
- **Passos:** rode C-05 e verifique os arquivos salvos em `data/_storage/<case_id>/`.
- **Resultado esperado:** uploads e relatórios são gravados localmente; o fluxo funciona sem
  `AZURE_STORAGE_CONNECTION_STRING`.

### C-08 — Resiliência a falha do `ai-service`
- **Objetivo:** validar tratamento de erro quando a IA está indisponível.
- **Pré-condições:** backend no ar; `ai-service` parado.
- **Passos:** envie um `POST /analisar` válido.
- **Resultado esperado:** o backend responde `502`/`504` (sem travar) e o upload permanece preservado no
  storage; nenhum caso "fantasma" é persistido como sucesso.

---

## 7. Suíte D — Entregáveis e relatório técnico (Fase 4)

### D-01 — Exportação do relatório técnico
- **Objetivo:** validar a geração do relatório técnico em PDF/HTML.
- **Pré-condições:** ambiente Python.
- **Passos:** rode `python -m scripts.exportar_relatorio`.
- **Resultado esperado:** gera o relatório a partir de `docs/relatorio-tecnico.md`; se faltarem libs de
  PDF, cai no **fallback HTML** sem erro.

### D-02 — Completude do relatório técnico (6 seções)
- **Objetivo:** confirmar o conteúdo mínimo exigido.
- **Pré-condições:** repositório clonado.
- **Passos:** abra `docs/relatorio-tecnico.md`.
- **Resultado esperado:** contém fluxo multimodal (diagrama), modelos por modalidade, lógica de fusão +
  ganho, resultados/métricas, e a **seção §5 de privacidade/LGPD**.

### D-03 — Roteiro do vídeo e disclaimer ético
- **Objetivo:** confirmar entregáveis documentais.
- **Pré-condições:** repositório clonado.
- **Passos:** abra `docs/roteiro-video.md` e o topo do `README.md`.
- **Resultado esperado:** roteiro (≤15 min) presente; **disclaimer ético** visível no README e no
  relatório técnico.

---

## 8. Suíte E — Dashboard de produção (Fase 5)

> Em Docker, o dashboard fica em `http://localhost:8080/`. Em dev, `http://localhost:5173/` com o backend
> em `:3000`.

### E-01 — Dashboard carrega e mostra status de tempo real
- **Objetivo:** validar o carregamento do painel e a conexão WebSocket.
- **Pré-condições:** stack no ar.
- **Passos:** abra o dashboard e observe a barra superior.
- **Resultado esperado:** painel carrega; indicador mostra "tempo real conectado"; contadores de risco
  (BAIXO/MÉDIO/ALTO) são exibidos.

### E-02 — Cadastro de paciente
- **Objetivo:** validar a criação de paciente.
- **Pré-condições:** dashboard aberto.
- **Passos:** vá em "Pacientes" → "Dar entrada", preencha o nome (e dados opcionais) e salve.
- **Resultado esperado:** paciente criado (HTTP 201) e listado; redireciona para o envio de caso.

### E-03 — Envio de caso multimodal
- **Objetivo:** validar o upload pela UI.
- **Pré-condições:** paciente criado (E-02).
- **Passos:** na tela "Enviar caso", anexe ao menos texto clínico (e arquivos opcionais) e envie.
- **Resultado esperado:** a requisição conclui e o usuário é levado ao detalhe do caso recém-criado.

### E-04 — Detalhe do caso (painéis por modalidade + fusão)
- **Objetivo:** validar a visualização consolidada.
- **Pré-condições:** caso criado (E-03).
- **Passos:** abra `/casos/:id`.
- **Resultado esperado:** painéis por modalidade (cicatriz, vitais, áudio, texto) e o
  **painel de fusão** com `RiscoBadge` e `mensagem_alerta`; modalidades ausentes aparecem como
  não avaliadas (sem quebrar a tela).

### E-05 — Alerta em tempo real no dashboard
- **Objetivo:** validar o banner de alerta na UI.
- **Pré-condições:** dashboard aberto em uma aba.
- **Passos:** em outra aba/terminal, dispare um caso `MEDIO`/`ALTO`.
- **Resultado esperado:** um banner de alerta dismissível aparece para `MÉDIO`/`ALTO`; os contadores do
  dashboard se atualizam.

### E-06 — Histórico e filtro por risco
- **Objetivo:** validar a tela de histórico.
- **Pré-condições:** ao menos 2 casos de riscos diferentes.
- **Passos:** abra "Histórico" e filtre por nível de risco.
- **Resultado esperado:** lista os casos passados e o filtro restringe corretamente por nível.

### E-07 — Reforço de sinais vitais (pré-eclâmpsia)
- **Objetivo:** validar o aumento sintético e as métricas antes/depois (Fase 5).
- **Pré-condições:** ambiente Python.
- **Passos:** rode `python -m scripts.reforco_sinais_vitais`.
- **Resultado esperado:** o script gera os dados sintéticos e imprime/salva métricas antes/depois sem
  erro.

---

## 9. Suíte F — Relatórios automáticos especializados (Fase 6)

### F-01 — Relatório por caso é gerado
- **Objetivo:** validar a geração automática do relatório no fluxo.
- **Pré-condições:** caso processado (C-05/E-03) com `relatorio_url` preenchido.
- **Passos:** chame `GET /casos/:id/relatorio` (ou clique em "Relatório" no detalhe do caso).
- **Resultado esperado:** o relatório (HTML/PDF) é entregue; em modo local, é o arquivo em
  `data/_storage/...`; em Azure, redireciona para a URL SAS.

### F-02 — Conteúdo especializado por gatilho
- **Objetivo:** confirmar que o relatório reflete o gatilho de risco do caso.
- **Pré-condições:** um caso `ALTO` de infecção e um caso `MEDIO` psicológico.
- **Passos:** abra os relatórios dos dois casos.
- **Resultado esperado:** o conteúdo (resumo, evidências, gatilhos, recomendações) **varia** conforme o
  gatilho — ex.: infecção puerperal vs. desconforto psicológico.

### F-03 — Pré-visualização no dashboard
- **Objetivo:** validar o `RelatorioModal` na UI.
- **Pré-condições:** detalhe de um caso com relatório.
- **Passos:** clique em pré-visualizar/abrir relatório no detalhe do caso.
- **Resultado esperado:** o modal exibe o relatório em iframe e oferece link de download.

### F-04 — Geração de evidências de exemplo
- **Objetivo:** validar o script de evidências do relatório técnico.
- **Pré-condições:** ambiente Python.
- **Passos:** rode `python -m scripts.gerar_evidencias`.
- **Resultado esperado:** regenera o exemplo de relatório automático em `docs/relatorio/` sem erro.

---

## 10. Suíte G — Privacidade e segurança / LGPD (Fase 7)

> Os controles são **opt-in por variável de ambiente** — a demo local segue aberta por padrão. Cada caso
> abaixo ativa explicitamente o controle a validar.

### G-01 — Autenticação por `x-api-key` (backend)
- **Objetivo:** validar a proteção das rotas de dados (F7-01).
- **Pré-condições:** suba o backend com `API_KEY=segredo-teste` no `.env`.
- **Passos:**
  1. `curl http://localhost:3000/casos` **sem** header → observe o status.
  2. `curl -H "x-api-key: segredo-teste" http://localhost:3000/casos` → observe o status.
  3. `curl http://localhost:3000/health` (sem header).
- **Resultado esperado:** (1) `401`; (2) `200`; (3) `/health` sempre público (`200`).

### G-02 — Auth de serviço backend→ai-service
- **Objetivo:** validar a credencial de serviço para o `ai-service` (F7-01).
- **Pré-condições:** `AI_SERVICE_API_KEY=segredo-ia` no `.env` para ambos os serviços.
- **Passos:**
  1. `curl -X POST http://localhost:8000/inferencia` **sem** header (corpo válido).
  2. Dispare um `POST /analisar` pelo backend (que envia o header automaticamente).
- **Resultado esperado:** (1) `401` direto no `ai-service`; (2) o fluxo pelo backend funciona, pois ele
  injeta o `x-api-key`.

### G-03 — Fail-safe sem `API_KEY` em produção
- **Objetivo:** validar o default seguro (F7-01).
- **Pré-condições:** `API_KEY` vazia e `AUTH_REQUIRED=true`.
- **Passos:** chame uma rota de dados (ex.: `GET /casos`).
- **Resultado esperado:** retorna `503` (negação fail-safe) em vez de servir dados sem credencial.

### G-04 — TLS na borda (HTTPS)
- **Objetivo:** validar a terminação TLS com cert de dev (F7-02).
- **Pré-condições:** rodar `./scripts/gerar-cert-dev.sh`.
- **Passos:**
  1. `docker compose -f docker-compose.yml -f docker-compose.tls.yml up --build`
  2. Acesse `https://localhost:8443/` (aceite o cert autoassinado) e verifique o header `Strict-Transport-Security`.
- **Resultado esperado:** o dashboard responde por HTTPS em `:8443`; o header HSTS está presente.

### G-05 — Trilha de auditoria
- **Objetivo:** validar o registro de acesso (F7-03).
- **Pré-condições:** stack no ar; sqlite acessível em `data/_storage/app.sqlite`.
- **Passos:**
  1. Faça chamadas com `-H "x-user-id: tester"` a `GET /casos`, `GET /casos/:id` e `POST /analisar`.
  2. Inspecione a tabela `auditoria` (ex.: `sqlite3 data/_storage/app.sqlite "select * from auditoria"`).
- **Resultado esperado:** existem linhas com `usuario=tester`, `acao` (`listar_casos`/`ler_caso`/
  `analisar`), `case_id` e `timestamp`; **nenhum** conteúdo clínico é gravado na trilha.

### G-06 — Política de retenção (TTL)
- **Objetivo:** validar a limpeza por expiração (F7-04).
- **Pré-condições:** ao menos um caso antigo; `RETENTION_DAYS` definido (ex.: `1`).
- **Passos:** em `backend/`, rode `npm run retencao`.
- **Resultado esperado:** casos/artefatos fora do período são removidos (banco + storage) e a ação é
  auditada (`retencao_remover`); com `RETENTION_DAYS=0` o comando é no-op.

### G-07 — Pseudonimização do payload e `case_id` opaco
- **Objetivo:** validar minimização de PII (F7-05).
- **Pré-condições:** stack no ar (logs do `ai-service` observáveis).
- **Passos:**
  1. Dispare `POST /analisar` e observe o payload enviado ao `ai-service` (logs).
  2. Em produção (`NODE_ENV=production`), envie um `case_id` **não-UUID**.
- **Resultado esperado:** o payload ao `ai-service` **não** contém `primeiro_nome` (somente
  `id`/idade/gestante/idade gestacional); em produção, `case_id` não-UUID é rejeitado com `400`.

### G-08 — Hardening HTTP (helmet, CORS, MIME)
- **Objetivo:** validar headers de segurança e validação de upload (F7-06).
- **Pré-condições:** stack no ar.
- **Passos:**
  1. Inspecione os headers de resposta (ex.: `curl -I http://localhost:3000/`) procurando headers do helmet.
  2. Em `POST /analisar`, anexe um arquivo com MIME inválido para um campo de mídia.
  3. Anexe um arquivo acima de 50 MB.
- **Resultado esperado:** (1) headers de segurança presentes; (2) MIME inválido → `400`; (3) arquivo
  grande → `413`.

### G-09 — Segredos via Key Vault (fallback `.env`)
- **Objetivo:** validar o carregamento opcional de segredos (F7-07).
- **Pré-condições:** `AZURE_KEY_VAULT_URL` **vazio**.
- **Passos:** suba o backend e observe o bootstrap.
- **Resultado esperado:** o serviço sobe usando os segredos do `.env` (fallback), sem exigir Key Vault.

### G-10 — Conformidade (sem segredos/dados reais no Git)
- **Objetivo:** validar a checagem de conformidade do CI (F7-08).
- **Pré-condições:** ambiente Python.
- **Passos:** rode `python -m scripts.check_conformidade`.
- **Resultado esperado:** a checagem passa em um repositório limpo; falharia se houvesse `.env` versionado
  ou dados reais de paciente.

---

## 11. Suíte H — Regressão de gate (testes automatizados)

> Não é teste manual, mas deve estar **verde** antes do sign-off final.

### H-01 — Lint + testes Python
- **Passos:** na raiz, rode `ruff check scripts ai-service` e `pytest -q`.
- **Resultado esperado:** lint sem erros; suíte `pytest` verde.

### H-02 — Lint + testes Node (backend)
- **Passos:** em `backend/`, rode `npm run lint` e `npm test`.
- **Resultado esperado:** lint sem erros; suíte `jest` verde (IA mockada).

### H-03 — Lint + testes + build do frontend
- **Passos:** em `frontend/`, rode `npm run lint`, `npm test` e `npm run build`.
- **Resultado esperado:** lint sem erros; `vitest` verde; build gera `frontend/dist`.

### H-04 — Subida limpa via Docker
- **Passos:** `cp .env.example .env` e `docker compose up --build`.
- **Resultado esperado:** os três serviços sobem; `ai-service` fica saudável (healthcheck) antes do
  backend; dashboard acessível em `:8080`.

---

## 12. Matriz de rastreabilidade (requisito → teste)

| Requisito / componente | Fase | Casos de teste |
|------------------------|------|----------------|
| Mini-dataset e dados sintéticos | 1 | A-01, A-02, A-03 |
| Análise de vídeo (cicatriz, YOLOv8) | 2 | B-02, E-04 |
| Análise de áudio especializada | 2 | B-04, E-04 |
| Modalidade texto (NLP) | 2 | B-03, C-05 |
| Sinais vitais | 2 | B-01, E-07 |
| Métricas por modalidade | 2 | B-05 |
| Motor de fusão + JSON padronizado | 3 | C-02, C-03, C-04 |
| Ganho da fusão vs. modalidade única | 3 | C-04 |
| API `/inferencia` e `/analisar` | 3 | C-02, C-05 |
| Alerta em tempo real (WebSocket) | 3 | C-06, E-05 |
| Integração nuvem (Azure) + fallback local | 3 | C-07 |
| Resiliência a falhas | 3 | C-08 |
| Relatório técnico + roteiro do vídeo | 4 | D-01, D-02, D-03 |
| Dashboard de produção | 5 | E-01..E-06 |
| Reforço de sinais vitais | 5 | E-07 |
| Relatórios automáticos especializados | 6 | F-01, F-02, F-03, F-04 |
| Autenticação / restrição de acesso | 7 | G-01, G-02, G-03 |
| TLS/HTTPS | 7 | G-04 |
| Auditoria de acesso | 7 | G-05 |
| Retenção/expiração | 7 | G-06 |
| Pseudonimização / minimização | 7 | G-07 |
| Hardening HTTP (helmet/CORS/MIME) | 7 | G-08 |
| Segredos (Key Vault / `.env`) | 7 | G-09 |
| Conformidade no CI | 7 | G-10 |
| Reprodutibilidade / gate de qualidade | todas | H-01..H-04 |

---

## 13. Registro de execução e sign-off

> Preencha a cada rodada de validação. Para itens dependentes de ambiente (ex.: Azure real), use `N/A`
> com justificativa.

**Ambiente da execução**

| Campo | Valor |
|-------|-------|
| Data | _\<preencher\>_ |
| Responsável | _\<preencher\>_ |
| Commit / branch | _\<preencher\>_ |
| Modo (Docker / local) | _\<preencher\>_ |

**Resultados**

| Caso | Resultado | Observações |
|------|-----------|-------------|
| A-01 | | |
| A-02 | | |
| A-03 | | |
| B-01 | | |
| B-02 | | |
| B-03 | | |
| B-04 | | |
| B-05 | | |
| C-01 | | |
| C-02 | | |
| C-03 | | |
| C-04 | | |
| C-05 | | |
| C-06 | | |
| C-07 | | |
| C-08 | | |
| D-01 | | |
| D-02 | | |
| D-03 | | |
| E-01 | | |
| E-02 | | |
| E-03 | | |
| E-04 | | |
| E-05 | | |
| E-06 | | |
| E-07 | | |
| F-01 | | |
| F-02 | | |
| F-03 | | |
| F-04 | | |
| G-01 | | |
| G-02 | | |
| G-03 | | |
| G-04 | | |
| G-05 | | |
| G-06 | | |
| G-07 | | |
| G-08 | | |
| G-09 | | |
| G-10 | | |
| H-01 | | |
| H-02 | | |
| H-03 | | |
| H-04 | | |

**Conclusão da rodada:** _\<aprovada / aprovada com ressalvas / reprovada\>_ — _\<resumo\>_
