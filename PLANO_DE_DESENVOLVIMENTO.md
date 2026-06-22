# Plano de Desenvolvimento — Tech Challenge Fase 4 (8IADT)

> Solução de **IA Multimodal para Saúde da Mulher**: **acompanhamento contínuo no pós-parto** com análise de **vídeo** (cicatriz da cesárea + fisioterapia), **áudio de consultas/relatos**, **sinais vitais** e **texto clínico**, com **fusão multimodal** para gerar **alertas precoces** em tempo real, hospedada em **nuvem (Azure)**.

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
| Fase 2 | [`docs/02-fase2-modelos.md`](docs/02-fase2-modelos.md) | Modelos individuais (vídeo, áudio, sinais vitais, texto) |
| Fase 3 | [`docs/03-fase3-fusao-e-nuvem.md`](docs/03-fase3-fusao-e-nuvem.md) | Fusão multimodal + deploy na nuvem |
| Fase 4 | [`docs/04-fase4-entregaveis.md`](docs/04-fase4-entregaveis.md) | Repositório, relatório técnico e vídeo |
| Fase 5 _(rascunho)_ | [`docs/08-fase5-producao-e-escala.md`](docs/08-fase5-producao-e-escala.md) | Produção, escala e robustez (fecha itens em aberto) |
| Fase 6 _(rascunho)_ | [`docs/09-fase6-relatorios-automaticos.md`](docs/09-fase6-relatorios-automaticos.md) | Relatórios automáticos especializados (conteúdo por tipo + anexos com links) |
| Componente | [`docs/casos-de-uso.md`](docs/casos-de-uso.md) | Casos de uso (diagramas Mermaid) |
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

O Tech Challenge pede uma solução de IA que monitore pacientes por **dados multimodais (áudio, vídeo e texto)** para identificar **sinais precoces de risco** em saúde da mulher.

- **Funcionalidades** — escolher **pelo menos 2**.
- **Objetivos** — escolher **pelo menos 3**.
- **Entregas técnicas obrigatórias** — o PDF lista, em "Requisitos obrigatórios":
  1. **Análise de Vídeo Especializada** (YOLOv8 customizado + relatórios automáticos).
  2. **Análise de Áudio Especializada** (consultas, pré-natal, pós-parto, vítimas de violência).
- **Entregáveis da fase**: repositório Git completo, relatório técnico e vídeo de até 15 min.

> 💡 O enunciado enfatiza **monitorar continuamente** para achar **sinais precoces**. Por isso o cenário central é o **acompanhamento no pós-parto** (a paciente envia dados ao longo do tempo, de casa), e não um evento pontual de cirurgia.

---

## 3. Escopo escolhido (decisão de projeto)

Para manter o projeto realista, alinhado ao "monitoramento contínuo" do enunciado e com forte "fusão multimodal" (que é o diferencial avaliado), o escopo recomendado é:

**Cenário clínico central:** *Acompanhamento contínuo da mulher no **pós-parto** (e gestação avançada). A paciente, em casa, envia periodicamente seus dados; o sistema cruza tudo e alerta a equipe diante de **sinais precoces de risco**.*

**Riscos-alvo monitorados:** infecção da cicatriz da cesárea, pré-eclâmpsia/hipertensão, depressão pós-parto/ansiedade, violência doméstica e evolução da recuperação física.

**4 modalidades implementadas (áudio, vídeo, sinais vitais e texto):**
1. **Vídeo** — YOLOv8 detecta sinais de **infecção na cicatriz** da cesárea; **YOLOv8-pose** acompanha os **exercícios de fisioterapia**/recuperação.
2. **Sinais vitais** — modelo clássico (Random Forest / Isolation Forest) sobre dados clínicos tabulares (PA, FC, glicemia, temperatura) detecta **risco materno / pré-eclâmpsia**.
3. **Áudio** — transcrição + classificação de sinais de **depressão pós-parto, ansiedade e violência** em áudio de consulta/relato.
4. **Texto/NLP** — análise de laudos, exames e evolução clínica (fecha a tríade "áudio, vídeo e texto" do enunciado).

**Fusão multimodal (o "pulo do gato"):** um motor de regras combina os sinais **da mesma paciente** e classifica o risco em `BAIXO / MÉDIO / ALTO`, disparando **alerta em tempo real** (WebSocket/SSE) para a equipe e gerando um **relatório automático**.

**Mapeamento de requisitos:** ver tabela completa em [`docs/00-visao-geral-e-escopo.md`](docs/00-visao-geral-e-escopo.md).

---

## 4. O que liga os dados (a coerência do projeto)

Os dados **não são análises soltas**. Eles são amarrados por três "colas":

1. **A paciente + um caso** — cada paciente cadastrada recebe **um conjunto de dados** (vídeo/áudio/sinais/texto). Tudo pertence à **mesma pessoa, no mesmo episódio de cuidado**.
2. **A linha do tempo do pós-parto** — cada modalidade observa um ângulo do **mesmo acompanhamento**: o relato (áudio/texto), o corpo (cicatriz/fisioterapia em vídeo) e os números (sinais vitais).
3. **O motor de fusão** — cruza as evidências e gera **um** nível de risco, provando que a combinação vale mais que a soma das partes.

> ⚠️ **Treino x uso real.** Os **datasets públicos** servem **só para treinar** cada modelo (são de pessoas diferentes — tudo bem). O **"mesmo paciente"** só existe no **uso real**, quando alguém é cadastrado e envia os próprios dados. Para **demonstrar** a fusão sem um paciente real, montamos um **"caso de exemplo" sintético** juntando amostras (ver [Fase 1](docs/01-fase1-dados.md)).

---

## 5. Arquitetura em uma frase

**Node.js** (orquestrador: upload, API, banco, dashboard, Azure Blob) **+** **Python/FastAPI** (motor de IA: YOLO/YOLO-pose, sinais vitais, áudio, texto) **+** **Azure** (Blob Storage + hospedagem). Detalhes em [`docs/arquitetura.md`](docs/arquitetura.md).

```
Usuário → API Node.js → Azure Blob (armazena) → chama Serviço Python (FastAPI)
                                                      ↓
                    YOLO + Sinais Vitais + Áudio + Texto → Fusão → JSON + Relatório
                                                      ↓
              Node grava no banco → Dashboard (alerta em tempo real via WebSocket)
```

---

## 6. Fases em ordem (visão macro)

| Fase | Objetivo | Resultado "pronto" |
|------|----------|--------------------|
| **1 — Dados** | Obter e preparar mini-datasets de vídeo, sinais vitais, áudio e texto | Dados limpos e anotados para começar a treinar |
| **2 — Modelos** | Treinar/validar cada IA isoladamente | 4 modelos funcionando individualmente com métricas |
| **3 — Fusão + Nuvem** | Motor de regras + API + deploy Azure | Pipeline ponta-a-ponta rodando na nuvem |
| **4 — Entregáveis** | Repo, relatório e vídeo | Tudo pronto para submissão |
| **5 — Produção/Escala** _(rascunho)_ | Escalar modelos, completar áudio/pose, deploy Azure real, dashboard React | Solução de **demo-grade** elevada a **produção** (itens em aberto fechados) |
| **6 — Relatórios Automáticos** _(rascunho)_ | Especializar o relatório por tipo de risco, anexos com links reais, PDF garantido e preview no dashboard | Relatório do `docs/06` cumprido por completo (especializado + anexos navegáveis) |

> **Princípio guia:** comece com um **mini-dataset** (5 amostras por modalidade) e faça o pipeline rodar ponta-a-ponta. "Se rodar com 5, roda com 500." Só depois escale.

> **Sobre a Fase 5:** as Fases 1–4 já entregam o Tech Challenge. A **Fase 5 é um rascunho de planejamento**
> (escopo a confirmar) que consolida o que ficou **em aberto** no [checklist](docs/05-checklist-entrega.md) e
> no [`STATE.md`](.specs/project/STATE.md). Detalhes em [`docs/08-fase5-producao-e-escala.md`](docs/08-fase5-producao-e-escala.md).

> **Sobre a Fase 6:** também é um **rascunho de planejamento** (escopo a confirmar). O **relatório automático
> já existe** (Fase 3, com download no dashboard na Fase 5); a Fase 6 fecha a lacuna restante entre o
> requisito [`docs/06-relatorios-automaticos.md`](docs/06-relatorios-automaticos.md) e o código —
> **especializar o conteúdo por tipo de risco** e trazer **anexos com links reais**. Detalhes em
> [`docs/09-fase6-relatorios-automaticos.md`](docs/09-fase6-relatorios-automaticos.md).

---

## 7. Estrutura de repositório recomendada

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

## 8. Próximo passo imediato

1. Ler [`docs/00-visao-geral-e-escopo.md`](docs/00-visao-geral-e-escopo.md) e confirmar o escopo com o grupo.
2. Dividir as fases entre os integrantes (sugestão de divisão no doc da Fase 4).
3. Começar a Fase 1 pelo **mini-dataset** — ver [`docs/01-fase1-dados.md`](docs/01-fase1-dados.md).
