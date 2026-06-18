# STATE — Memória do Projeto

> Memória persistente entre sessões (decisões, blockers, lições, todos, ideias adiadas).
> Visão e roadmap completos vivem em [`PLANO_DE_DESENVOLVIMENTO.md`](../../PLANO_DE_DESENVOLVIMENTO.md)
> e em [`docs/`](../../docs).

## Fase atual

**Fase 1 — Aquisição e Preparação de Dados** — **implementada**.
Plano em [`.specs/features/fase1-dados/`](../features/fase1-dados/) (spec → design → tasks).
Código em `scripts/data_prep/` (+ testes em `scripts/tests/`); estrutura em `data/`.
Gate verde: `ruff check scripts` + `pytest` (12 testes). Orquestrador `python -m scripts.data_prep`
validado: sinais vitais (UCI) e cicatriz (AZH Wound, download+conversão+preview) baixam de verdade;
texto/caso sintético gerados offline. Áudio e fisioterapia exigem obtenção manual (sem download
público simples) e aparecem como passos opcionais.

## Decisões registradas

| #   | Decisão                                                            | Origem                |
| --- | ----------------------------------------------------------------- | --------------------- |
| S1  | Scripts de dados em `scripts/data_prep/` (não em `ai-service/`)    | design.md DD1         |
| S2  | `requirements-data.txt` separado das deps do serviço de IA        | design.md DD2         |
| S3  | Caso sintético segue o objeto de requisição do contrato de API    | design.md DD4         |
| S4  | Testes unitários só em funções puras (limpeza/conversão/builder)  | design.md DD5         |
| S5  | `data/` ignorado pelo Git; só `data/README.md` versionado         | design.md DD7         |
| S6  | **Python 3.13** (não 3.14): whisper não suporta 3.14 ainda        | design.md DD8         |

## Blockers / dependências externas

- Acesso/licença dos datasets pode exigir login (IntelliRehabDS, Androids). Fallback: obtenção manual
  documentada em `data/README.md` (T2).
- Decisão pendente do grupo: usar **Whisper local** ou **Azure Speech-to-Text** para transcrição
  (T7) — design deixa o backend trocável por env var.

## Todos / próximos passos

- [ ] Implementar a Fase 1 seguindo `tasks.md` (T1→T4 sequencial; T5–T9 em paralelo; T10→T11).
- [ ] Confirmar versões estáveis dos pacotes ao criar `requirements-data.txt` (T3).
- [ ] Após o gate da Fase 1, iniciar planejamento da Fase 2 (modelos).

## Ideias adiadas

- Escalar mini-dataset (de 5 para mais amostras) só após o pipeline rodar ponta-a-ponta (Fase 3).
- Datasets sintéticos extras de pré-eclâmpsia (HF) para reforçar a modalidade de sinais vitais.

## Lições

- (a preencher durante a execução)
