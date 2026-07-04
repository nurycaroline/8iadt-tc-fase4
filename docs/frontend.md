# Front-end — Painel de Monitoramento Clínico

> O front-end é um **dashboard para a equipe médica/vigilância** acompanhar pacientes, visualizar a análise multimodal em sincronia e **receber alertas em tempo real**. A tela de "detalhe do caso" é a cena principal do vídeo de demonstração.

## 1. Objetivo
- Dar **visão em tempo real** do risco de cada paciente monitorada.
- Mostrar lado a lado as **modalidades** (vídeo da cicatriz, sinais vitais, áudio, texto) e a **decisão da fusão**.
- Disparar **alerta visual/sonoro** quando o risco for `MÉDIO`/`ALTO`.
- Permitir **upload de caso** e **download do relatório automático**.

## 2. Stack sugerida
| Camada | Tecnologia | Motivo |
|--------|-----------|--------|
| Framework | **React + Vite + TypeScript** | Ecossistema maduro, rápido, tipado |
| UI | **TailwindCSS + shadcn/ui** (ou Material UI) | Componentes prontos e visual clínico limpo |
| Gráficos | **Recharts** (ou Chart.js) | Séries temporais de sinais vitais |
| Vídeo | `<video>` HTML5 + canvas overlay (ou **video.js**) | Player com bounding boxes do YOLO |
| Tempo real | **socket.io-client** (WebSocket) ou EventSource (SSE) | Alertas em tempo real do backend Node |
| Dados | **React Query** (REST) + **Zustand**/Context | Cache de requisições + estado de UI |

> **Fora do escopo:** login e permissionamento não fazem parte deste projeto (foco em resolver o problema). Os cuidados com dados sensíveis seguem em [privacidade/LGPD](07-privacidade-e-seguranca.md) via pseudonimização e dados sintéticos.

> Alternativa mais simples para a demo: um SPA leve ou até um template server-side. Mas React entrega a melhor experiência de "tempo real" e impressiona na avaliação.

## 3. Telas

### 3.1 Pacientes (lista)
- Lista de pacientes com **primeiro nome, idade, gestante/idade gestacional** e status do monitoramento.
- Botão **"Dar entrada"** (cria novo paciente) e ação **excluir** por linha.
- Sem edição: a gestão é enxuta (criar, listar, excluir).

### 3.2 Dar entrada de paciente
- Formulário curto: **primeiro nome**, **idade**, **gestante** (sim/não) e **idade gestacional** (semanas — só aparece se gestante = sim).
- Ao salvar, **cria um paciente novo** e segue direto para o envio dos dados do caso (3.3).

### 3.3 Enviar dados do caso (upload)
- Para o paciente recém-criado, enviar **vídeo, sinais vitais (CSV), áudio e/ou texto**.
- Indicador de **status de processamento** (enviando → analisando → concluído).

### 3.4 Dashboard (visão geral)
- Grade de **casos/pacientes ativos**, cada um com **primeiro nome** + **badge de risco** (🟢 baixo / 🟡 médio / 🔴 alto).
- **Banner de alerta** no topo quando chega um risco alto em tempo real.
- Contadores: nº de casos por nível de risco.

### 3.5 Detalhe do caso — **a tela principal**
- Cabeçalho com os dados do paciente (primeiro nome, idade, gestante/idade gestacional ou semanas de pós-parto).
Layout em painéis por modalidade:
- **Vídeo/foto da cicatriz** com *bounding box* do YOLO + badge (`ferida_ok` / `ferida_alerta`).
- **Sinais vitais** (PA, FC, glicemia, temperatura) com **destaque de limiar** (ex.: PA≥140/90) e a classe de risco do modelo.
- **Painel de áudio**: forma de onda + transcrição + badge da categoria (depressão pós-parto, ansiedade, violência...).
- **Painel de texto/NLP**: laudo/exame/evolução com **trechos de risco destacados**.
- **Painel de fusão**: medidor de risco (gauge `BAIXO/MÉDIO/ALTO`), lista de evidências e a `mensagem_alerta`.
- Botão **"Ver/baixar relatório"** (PDF gerado automaticamente).

### 3.6 Histórico
- Casos passados com filtro por risco/data e link para o relatório.

## 4. Sistema de cores de risco
| Risco | Cor | Ação na UI |
|-------|-----|-----------|
| BAIXO | 🟢 verde | Apenas exibe |
| MÉDIO | 🟡 amarelo | Destaque + toast |
| ALTO | 🔴 vermelho | Banner fixo + som + notificação |

## 5. Fluxo de dados com o backend
```
Front-end (React)
   │  REST (React Query)         WebSocket (socket.io)
   ▼                                   ▲
Backend Node.js  ── grava no banco ──┘  (push do alerta quando risco MÉDIO/ALTO)
   │  POST /inferencia
   ▼
Serviço Python (IA) → JSON de risco + relatorio_url
```
- **REST** para gestão de pacientes (`POST /pacientes`, `GET /pacientes`, `DELETE /pacientes/{id}`), upload/análise (`POST /analisar`), detalhe do caso e download do relatório.
- **WebSocket/SSE** para **empurrar** o alerta assim que a fusão classificar o risco (ver [Fase 3, Tarefa 3.3b](03-fase3-fusao-e-nuvem.md)).
- O contrato do JSON consumido está em [contrato-api.md](contrato-api.md).

## 6. Wireframe (ASCII)

**Pacientes (lista):**
```
┌───────────────────────────────────────────────────────────┐
│ Pacientes                              [ + Dar entrada ]    │
├───────────────────────────────────────────────────────────┤
│ Maria · 31 · gestante 28 sem   🔴 alto      [ excluir ]    │
│ Ana   · 27 · não gestante      🟢 baixo     [ excluir ]    │
│ Júlia · 35 · gestante 12 sem   🟡 médio     [ excluir ]    │
└───────────────────────────────────────────────────────────┘
```

**Dashboard:**
```
┌───────────────────────────────────────────────────────────┐
│ 🔴 ALERTA: Maria (#A123) — cicatriz infectada + febre      │
├───────────────────────────────────────────────────────────┤
│ Monitoramento            🟢 3   🟡 1   🔴 1                 │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐            │
│ │Maria 🔴 │ │Júlia 🟡 │ │Ana   🟢 │ │Bia   🟢 │            │
│ │Pós-parto│ │Pré-eclâ.│ │Pós-parto│ │Fisiot.  │            │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘            │
└───────────────────────────────────────────────────────────┘
```

**Detalhe do caso:**
```
┌────────────────────────────┬──────────────────────────────┐
│  VÍDEO CICATRIZ (YOLO)      │  SINAIS VITAIS                │
│  ▢ ferida_alerta 0.86       │  PA 150/95  ⚠ ≥140/90         │
│                             │  classe: pré-eclâmpsia        │
├────────────────────────────┼──────────────────────────────┤
│  FISIOTERAPIA (pose)        │  TEXTO/LAUDO: "relato de febre │
│  ⦿ execução: incorreta      │  e dor na cicatriz" (risco)    │
├────────────────────────────┴──────────────────────────────┤
│  ÁUDIO: "tom de tristeza" ▁▂▅▇▅▂▁  → depressão_pos_parto    │
├─────────────────────────────────────────────────────────────┤
│  FUSÃO:  🔴 RISCO ALTO   "Sinal de infecção + febre/dor"    │
│          [ Ver relatório PDF ]                              │
└─────────────────────────────────────────────────────────────┘
```

## 7. Boas práticas
- **Desktop-first** (estação de monitoramento), mas responsivo.
- **Acessibilidade**: cor + ícone + texto (não depender só da cor para o risco).
- **Estados de UI**: loading, processando, erro e vazio bem tratados.
- **Disclaimer** visível: apoio à decisão, não diagnóstico.

## 8. Foco para a demonstração
A tela de **detalhe do caso** é o "money shot" do vídeo: o avaliador vê a cicatriz com o sinal detectado pelo YOLO, os sinais vitais classificados, o áudio/texto analisados e, ao processar o caso, o **alerta vermelho da fusão** aparecendo em tempo real. Priorize deixar essa tela impecável.
