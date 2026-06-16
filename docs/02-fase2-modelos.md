# Fase 2 — Desenvolvimento dos Modelos Individuais

> Objetivo: construir e **validar cada IA separadamente** antes de uni-las. Cada modelo entrega métricas próprias.

## Resultado esperado (Definition of Done)
- [ ] Modelo de **vídeo** (YOLOv8) treinado e exportado (`.pt`/`.onnx`) com métricas (mAP, precisão/recall).
- [ ] Modelo de **sinais vitais** treinado com métricas (acurácia, F1, matriz de confusão).
- [ ] Módulo de **áudio** funcionando (transcrição + classificação) com exemplos.
- [ ] Módulo de **texto/NLP** funcionando com exemplos.
- [ ] **Limiares clínicos** documentados.
- [ ] **Baseline por modalidade única** registrada (para comparar com a fusão na Fase 3).

---

## Tarefa 2.1 — Detecção visual (YOLOv8)
- **Biblioteca:** `ultralytics`.
- **Passos:**
  1. Fine-tuning de **YOLOv8n** ou **YOLOv8s** (modelos leves) com as imagens anotadas na Fase 1.
  2. Treinar em GPU (Colab) com poucas épocas no mini-dataset; depois escalar.
  3. Avaliar **mAP@0.5**, precisão e recall por classe.
  4. Exportar em **ONNX** (ou PyTorch) para a inferência.
- **Estratégia para sangramento (anomalia visual):** como dataset de sangue é raro, combinar:
  - Segmentação de anatomia/instrumentos (AutoLaparo) **+**
  - Classificador leve "presença de sangue" por frame.

## Tarefa 2.2 — Análise de sinais vitais
- **Biblioteca:** `scikit-learn`.
- **Modelos:** **Random Forest** (classificação supervisionada com rótulos do CTG) e/ou **Isolation Forest** (detecção de anomalia não supervisionada).
- **Passos:**
  1. Treinar com as features extraídas na Fase 1.
  2. Avaliar acurácia, F1 e matriz de confusão.
  3. Salvar o modelo (`joblib`).

## Tarefa 2.3 — Análise de áudio
- **Pipeline:** áudio → **transcrição** (Whisper/Azure Speech) → **classificação** de risco.
- **Classificação:** pode ser por palavras-chave + análise de sentimento (Azure Text Analytics) ou um classificador simples treinado nos 5 rótulos.
- **Saída:** categoria (`ansiedade`, `depressao_pos_parto`, `violencia`, `neutro`) + confiança.

## Tarefa 2.4 — Análise de texto (NLP)
- **Entrada:** laudos, prescrições hormonais e evolução clínica (Fase 1, Tarefa 1.4).
- **Abordagem (enxuta):** extração de palavras-chave de risco + **análise de sentimento** (Azure Text Analytics) ou um classificador simples.
- **Saída:** lista de achados de risco no texto + categoria (ex.: `complicacao`, `prescricao_risco`, `neutro`).
- Padronizar a saída num dicionário para a fusão.

## Tarefa 2.5 — Baseline por modalidade única
- Antes da fusão, registre a performance de **cada modalidade isolada** detectando o evento de risco.
- Servirá de comparação para provar, na Fase 3, que a **fusão reduz falsos positivos / melhora a detecção**.

## Tarefa 2.6 — Definição de limiares clínicos (gatilhos)
Documentar os disparadores matemáticos do alerta, por exemplo:

| Sinal | Condição de alerta |
|-------|--------------------|
| PA sistólica | `< 90 mmHg` |
| Frequência cardíaca fetal (FHR) | fora de `110–160 bpm` |
| Detecção visual de sangue | confiança `≥ 0.85` |
| Risco no áudio | categoria de risco com confiança `≥ 0.7` |
| Achado no texto clínico | termo/categoria de risco identificado |

> Esses limiares alimentam o **motor de fusão** da Fase 3.

---

## Dicas
- Treine sempre primeiro no **mini-dataset** (rápido) e só depois escale.
- Guarde os **gráficos e métricas** — vão direto para o relatório técnico e o vídeo.
- Padronize a saída de cada modelo num dicionário Python para facilitar a fusão.
