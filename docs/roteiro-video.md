# Roteiro do Vídeo de Demonstração (≤ 15 min)

> Entregável da Tarefa 4.3 ([`docs/04-fase4-entregaveis.md`](04-fase4-entregaveis.md)). Roteiro **bloco a
> bloco** cobrindo os **8 pontos** do roteiro sugerido, com o que falar, o que mostrar na tela, o **comando**
> a rodar e a **evidência** a exibir. Total estimado: **~14 min** (margem para o limite de 15 min).
>
> **Gravação/publicação é ação humana** (DD-F4-5): grave a tela seguindo este roteiro, publique como
> **"Não listado"** no YouTube/Vimeo e **cole o link no [`README.md`](../README.md)**.

## Antes de gravar (setup)

```bash
cp .env.example .env          # padrão = storage local (sem precisar de Azure)
docker compose up --build     # sobe ai-service (8000) e backend (3000)
# Em outro terminal, deixe pronto:
python -m scripts.e2e_demo    # demo ponta a ponta em processo (alerta no log)
```

Abra no navegador o **cliente do alerta** em `http://localhost:3000/` e o
[relatório técnico](relatorio-tecnico.md) e o [diagrama](relatorio/diagrama-arquitetura.md) para apoio.

> **Degradação documentada (DD-F4-6):** se o ambiente **não tiver os pesos do YOLO/ASR**, as modalidades de
> vídeo/áudio degradam (evidência `nenhum`/ausente) e a **fusão decide com sinais vitais + texto** — o
> alerta ainda acontece (`MEDIO`). Nos blocos 2 e 4, mostre o código/saída padronizada e **explique** que,
> com os pesos treinados, o caso escala para `ALTO` (cenário de referência em [`e2e-log.txt`](relatorio/e2e-log.txt)).

## Roteiro bloco a bloco

| # | Bloco (ponto do roteiro) | Fala (resumo) | O que mostrar / comando | Evidência | Duração |
| - | ------------------------ | ------------- | ----------------------- | --------- | ------- |
| 1 | **Problema + arquitetura** | Acompanhamento no pós-parto enfraquece; sinais ficam espalhados. Apresentar a solução de fusão multimodal e o diagrama. | Slide/abrir [`diagrama-arquitetura.md`](relatorio/diagrama-arquitetura.md) e [`arquitetura.md`](arquitetura.md) | Diagrama do fluxo (2 serviços + storage + fusão + alerta) | 2:00 |
| 2 | **Vídeo — YOLO (cicatriz + pose)** | Cicatriz da cesárea via **YOLOv8**; fisioterapia via **YOLOv8-pose**. Saída padronizada (contrato §3). | Mostrar [`app/cicatriz/`](../ai-service/app/cicatriz/) e [`app/fisioterapia/`](../ai-service/app/fisioterapia/); citar mAP em [`cicatriz/metrics.json`](../ai-service/models/cicatriz/metrics.json) | mAP@50 = 0,995 (41 épocas, precisão/recall ≈0,99); pesos `best.pt` versionados | 1:30 |
| 3 | **Sinais vitais** | Classificação por **Random Forest** (PA/FC/glicemia). | Abrir [`sinais_vitais/metrics.json`](../ai-service/models/sinais_vitais/metrics.json) + [`matriz_confusao.png`](../ai-service/models/sinais_vitais/matriz_confusao.png) | Acurácia 0,646 / F1 0,624; classe `high` F1 0,79 | 1:30 |
| 4 | **Áudio + texto/NLP** | Áudio transcrito (Whisper) + classificação; texto/laudo por regras de NLP (febre/dor → infecção). | Mostrar [`app/audio/`](../ai-service/app/audio/) e [`app/texto/nlp.py`](../ai-service/app/texto/nlp.py); baseline texto 5/5 | [`baseline.json`](../ai-service/models/baseline.json) (texto 1,0/1,0) | 1:30 |
| 5 | **O momento da fusão (alerta vermelho)** | Cicatriz com infecção **+** PA alta/febre → **infecção puerperal (ALTO)** em tempo real. Motor de **regras explícitas**. | `python -m scripts.e2e_demo` e/ou `POST /analisar` do `caso_alto`; mostrar [`app/fusao.py`](../ai-service/app/fusao.py) | Log "Fusão concluída: risco=…"; alerta socket.io no cliente | 2:30 |
| 6 | **Relatório automático** | Cada caso gera um **relatório clínico** (Markdown → HTML/PDF) com gatilhos e recomendação. | Abrir [`exemplo-relatorio-automatico.md`](relatorio/exemplo-relatorio-automatico.md) (ou `.html`) | Relatório do `caso-alto` (ALTO, infecção puerperal) | 1:30 |
| 7 | **Integração Azure** | Storage com adaptador **Azure Blob \| local**; TLS, criptografia, SAS. Fallback local garante a demo. | Mostrar [`app/storage*.py`](../ai-service/app/) e [`deploy-azure.md`](deploy-azure.md); `.env` `STORAGE_BACKEND` | Adaptador Azure/local; nota de fallback | 1:30 |
| 8 | **Alerta chegando ao cliente** | O alerta `MEDIO`/`ALTO` chega **instantaneamente** ao dashboard via WebSocket. | No `http://localhost:3000/`, disparar `POST /analisar` e ver o alerta surgir | Alerta em tempo real no cliente (socket.io) | 1:30 |
| — | **Encerramento** | Recapitular o ganho da fusão (recall 1,0 / FP 0,0) e o disclaimer ético. Créditos. | Tabela de [`metricas-fusao.md`](relatorio/metricas-fusao.md) | Ganho da fusão vs. modalidade única | 0:30 |

**Total estimado: ~14:00** (≤ 15 min).

## Comandos de apoio (resumo)

```bash
docker compose up --build                 # sobe a stack (ai-service 8000 + backend 3000)
python -m scripts.e2e_demo                # demo ponta a ponta (alerta no log) — caso_alto
python -m scripts.e2e_demo --caso caso_medio
python -m scripts.gerar_evidencias        # regera o exemplo de relatório automático
python -m scripts.exportar_relatorio      # exporta o relatório técnico (PDF ou HTML)
```

Exemplo de `POST /analisar` (bloco 5/8), com o backend no ar:

```bash
curl -s -X POST http://localhost:3000/analisar \
  -H "Content-Type: application/json" \
  --data @data/casos/caso_alto.json | jq .
```

## Checklist do vídeo (espelha [`docs/05-checklist-entrega.md`](05-checklist-entrega.md))

- [ ] Demonstra análise de **áudio e vídeo (e texto)**.
- [ ] Mostra detecção e **resposta a anomalias em tempo real**.
- [ ] Mostra o **relatório automático** gerado.
- [ ] Mostra a **integração Azure** (ou o fallback local, explicando a integração).
- [ ] Mostra o **fluxo final do alerta** à equipe médica.
- [ ] Publicado no YouTube/Vimeo (**"Não listado"**) e **link no README**.
