# Diagrama de arquitetura e fluxo multimodal

> Fonte de verdade: [`docs/arquitetura.md`](../arquitetura.md) §1 e [`docs/casos-de-uso.md`](../casos-de-uso.md).
> Diagrama em **Mermaid inline** (a skill `mermaid-studio` não está instalada neste ambiente; com ela, o
> bloco abaixo pode ser renderizado em SVG/PNG e temizado — DD-F4-3).

## Fluxo ponta a ponta (upload → storage → IA → fusão → alerta/relatório)

```mermaid
flowchart TD
    P["Paciente / app<br/>áudio · vídeo · sinais vitais · texto"] -->|upload HTTPS| N

    subgraph ORQ["Backend orquestrador — Node.js + Express"]
        N["POST /analisar<br/>(upload + validação)"]
        DB[("SQLite<br/>Paciente / Caso")]
        RT["Alerta em tempo real<br/>socket.io"]
    end

    subgraph STO["Armazenamento (adaptador)"]
        AZ["Azure Blob Storage"]
        LOC["Storage local<br/>(fallback da demo)"]
    end

    subgraph IA["Motor de IA — Python + FastAPI"]
        API["POST /inferencia<br/>(pipeline)"]
        M1["Cicatriz<br/>YOLOv8"]
        M3["Sinais vitais<br/>Random Forest"]
        M4["Áudio<br/>Whisper + regras"]
        M5["Texto/NLP<br/>regras/palavras-chave"]
        FUS{{"Motor de fusão<br/>(regras explícitas)"}}
        REL["Relatório automático<br/>Markdown → HTML/PDF"]
    end

    N -->|salva artefatos| STO
    N -->|HTTP POST /inferencia| API
    API --> M1 & M3 & M4 & M5
    M1 & M3 & M4 & M5 --> FUS
    FUS --> REL
    FUS -->|JSON de risco<br/>contrato §2| N
    REL -->|relatorio_url| STO
    N -->|persiste| DB
    N -->|risco MEDIO/ALTO| RT
    RT -->|WebSocket| D["Dashboard / cliente<br/>(alerta em tempo real)"]
```

## Leitura do diagrama

1. **Upload** — a paciente envia as modalidades para o **Node (Express)** via HTTPS (`POST /analisar`).
2. **Armazenamento** — o Node grava os artefatos no **Azure Blob** ou no **storage local** (fallback da
   demo), por trás do mesmo adaptador (escolha por variável de ambiente).
3. **Inferência** — o Node chama o **serviço Python (FastAPI)** em `POST /inferencia`; o pipeline roda os
   modelos por modalidade (cicatriz, sinais vitais, áudio, texto).
4. **Fusão** — o **motor de fusão** cruza as evidências e decide **um** nível de risco explicável
   (`BAIXO`/`MEDIO`/`ALTO`) com os gatilhos acionados.
5. **Relatório** — para o caso é gerado um **relatório automático** (Markdown → HTML/PDF) salvo no storage.
6. **Resposta + persistência** — o Python devolve o **JSON de risco** (contrato §2); o Node persiste em
   **SQLite** (Paciente/Caso).
7. **Alerta em tempo real** — risco `MEDIO`/`ALTO` dispara um evento **socket.io** que chega ao
   **dashboard/cliente** instantaneamente.
