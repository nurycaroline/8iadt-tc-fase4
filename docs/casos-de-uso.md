# Casos de Uso

> Escopo focado em **resolver o problema** (sem login/permissionamento). Cobre: envio do caso, análise multimodal, fusão/classificação de risco, alerta em tempo real e relatório automático.

## 1. Atores

| Ator | Tipo | Papel |
|------|------|-------|
| **Equipe Médica/Assistencial** (médico ou enfermeiro) | Primário (humano) | Recebe alertas e consulta relatórios; também pode enviar casos |
| **Operador de Monitoramento** | Primário (humano) | Envia os dados do caso para análise |
| **Paciente** | Secundário | Origem dos dados (vídeo, áudio, sinais vitais, texto) |
| **Serviço de IA** | Secundário (sistema) | Executa os modelos de análise (Python) |
| **Azure** | Secundário (sistema) | Armazenamento (Blob) e serviços cognitivos |

## 2. Diagrama geral de casos de uso

```mermaid
flowchart LR
    EM["👩‍⚕️ Equipe Médica/Assistencial"]
    OP["🧑‍💻 Operador de Monitoramento"]
    PAC["🤰 Paciente"]
    IA["🤖 Serviço de IA"]
    AZ["☁️ Azure"]

    subgraph SIS["Sistema de Monitoramento Multimodal"]
        UC1(["UC1 · Enviar caso para análise"])
        UC2(["UC2 · Analisar dados multimodais"])
        UC3(["UC3 · Fundir evidências e classificar risco"])
        UC4(["UC4 · Emitir alerta em tempo real"])
        UC5(["UC5 · Gerar e visualizar relatório automático"])
    end

    OP --- UC1
    EM --- UC1
    EM --- UC4
    EM --- UC5
    PAC -. fornece dados .-> UC1

    UC1 -. «include» .-> UC2
    UC2 -. «include» .-> UC3
    UC4 -. «extend» .-> UC3
    UC3 -. «include» .-> UC5

    UC2 --- IA
    UC1 --- AZ
    UC5 --- AZ
```

> **Nota sobre o `«extend»`:** o **UC4 (alerta)** é condicional — só é acionado quando a classificação resulta em risco **MÉDIO** ou **ALTO**.

## 3. Detalhe do UC2 (análise multimodal)

O UC2 decompõe-se em uma análise por modalidade (relação `«include»`):

```mermaid
flowchart LR
    UC2(["UC2 · Analisar dados multimodais"])
    A1(["Analisar vídeo · YOLOv8"])
    A2(["Analisar sinais vitais · RF / Isolation Forest"])
    A3(["Analisar áudio · ASR + classificação"])
    A4(["Analisar texto · NLP"])

    UC2 -. «include» .-> A1
    UC2 -. «include» .-> A2
    UC2 -. «include» .-> A3
    UC2 -. «include» .-> A4
```

## 4. Descrição curta dos casos de uso

| ID | Caso de uso | Ator(es) | Descrição |
|----|-------------|----------|-----------|
| **UC1** | Enviar caso para análise | Operador, Equipe Médica | Envia os dados do caso (vídeo, áudio, sinais vitais e/ou texto); o sistema os armazena no Azure Blob e inicia o processamento |
| **UC2** | Analisar dados multimodais | Serviço de IA | Processa cada modalidade com seu modelo (YOLOv8 para vídeo, RF/Isolation Forest para sinais vitais, ASR+classificação para áudio, NLP para texto) |
| **UC3** | Fundir evidências e classificar risco | Serviço de IA | O motor de regras combina as saídas das modalidades e classifica o risco em `BAIXO` / `MÉDIO` / `ALTO` |
| **UC4** | Emitir alerta em tempo real | Equipe Médica | Quando o risco é `MÉDIO`/`ALTO`, o sistema notifica a equipe no dashboard em tempo real (WebSocket/SSE) |
| **UC5** | Gerar e visualizar relatório automático | Equipe Médica | O sistema gera o relatório clínico do caso (PDF) e a equipe visualiza/baixa pelo painel |

## 5. Fluxo principal (do caso ao alerta)

```mermaid
sequenceDiagram
    actor OP as Operador
    participant FE as Dashboard
    participant API as Backend (Node)
    participant AZ as Azure Blob
    participant IA as Serviço de IA (Python)
    actor EM as Equipe Médica

    OP->>FE: Envia dados do caso (UC1)
    FE->>API: POST /analisar-cirurgia
    API->>AZ: Armazena arquivos
    API->>IA: POST /inferencia
    IA->>IA: Analisa modalidades (UC2)
    IA->>IA: Fusão e classificação de risco (UC3)
    IA->>AZ: Salva relatório automático (UC5)
    IA-->>API: JSON de risco + relatorio_url
    API-->>FE: Atualiza caso
    alt risco MÉDIO ou ALTO
        API-->>EM: Alerta em tempo real (UC4)
    end
    EM->>FE: Visualiza relatório (UC5)
```

## 6. Referências
- Contrato dos dados trocados: [contrato-api.md](contrato-api.md)
- Lógica da fusão e alerta em tempo real: [03-fase3-fusao-e-nuvem.md](03-fase3-fusao-e-nuvem.md)
- Relatório automático: [06-relatorios-automaticos.md](06-relatorios-automaticos.md)
- Telas do dashboard: [frontend.md](frontend.md)
