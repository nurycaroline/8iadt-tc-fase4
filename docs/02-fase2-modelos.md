# Fase 2 — Desenvolvimento dos Modelos Individuais

> Objetivo: construir e **validar cada IA separadamente** antes de uni-las. Cada modelo entrega métricas próprias.

> **Implementação:** código em [`ai-service/`](../ai-service/) (um módulo por modalidade em `app/`),
> planejamento em [`.specs/features/fase2-modelos/`](../.specs/features/fase2-modelos/). Cada modalidade
> expõe uma função de inferência que devolve o **dicionário de evidência** do
> [contrato de API §3](contrato-api.md). Limiares clínicos em `app/limiares.py`; baseline por
> modalidade única em `ai-service/models/baseline.json`. Como treinar/inferir: ver
> [`ai-service/README.md`](../ai-service/README.md).

## Resultado esperado (Definition of Done)
- [ ] Modelo de **vídeo — cicatriz** (YOLOv8) treinado e exportado (`.pt`/`.onnx`) com métricas (mAP, precisão/recall).
- [ ] Modelo de **vídeo — fisioterapia** (YOLOv8-pose) funcionando com avaliação de movimento.
- [ ] Modelo de **sinais vitais** treinado com métricas (acurácia, F1, matriz de confusão).
- [ ] Módulo de **áudio** funcionando (transcrição + classificação) com exemplos.
- [ ] Módulo de **texto/NLP** funcionando com exemplos.
- [ ] **Limiares clínicos** documentados.
- [ ] **Baseline por modalidade única** registrada (para comparar com a fusão na Fase 3).

---

## Tarefa 2.1 — Detecção visual da cicatriz (YOLOv8)
- **Biblioteca:** `ultralytics`.
- **Passos:**
  1. Fine-tuning de **YOLOv8n** ou **YOLOv8s** (modelos leves) com as imagens anotadas na Fase 1 (AZH Wound).
  2. Treinar em GPU (Colab) com poucas épocas no mini-dataset; depois escalar.
  3. Avaliar **mAP@0.5**, precisão e recall por classe (`ferida_ok` vs. `ferida_alerta`).
  4. Exportar em **ONNX** (ou PyTorch) para a inferência.
- **Objetivo clínico:** sinalizar **sinal de infecção** (vermelhidão, secreção, deiscência) na cicatriz da cesárea.

## Tarefa 2.2 — Análise de fisioterapia (YOLOv8-pose)
- **Biblioteca:** `ultralytics` (modelo `*-pose`).
- **Passos:**
  1. Estimar **keypoints** do corpo nos vídeos de exercício (IntelliRehabDS).
  2. Derivar ângulos/repetições e classificar a execução como `correto / incorreto` (ou medir amplitude/evolução).
  3. Avaliar com os rótulos de correção do dataset.
- **Objetivo clínico:** acompanhar a **recuperação física** ao longo do tempo.

## Tarefa 2.3 — Análise de sinais vitais
- **Biblioteca:** `scikit-learn`.
- **Modelos:** **Random Forest** (classificação supervisionada com o rótulo `RiskLevel` do Maternal Health Risk) e/ou **Isolation Forest** (detecção de anomalia não supervisionada).
- **Passos:**
  1. Treinar com as features extraídas na Fase 1 (PA, FC, glicemia, temperatura).
  2. Avaliar acurácia, F1 e matriz de confusão.
  3. Salvar o modelo (`joblib`).
- **Objetivo clínico:** sinalizar **risco materno / pré-eclâmpsia**.

## Tarefa 2.4 — Análise de áudio
- **Pipeline:** áudio → **transcrição** (Whisper/Azure Speech) → **classificação** de risco.
- **Classificação:** por palavras-chave + análise de sentimento (Azure Text Analytics) ou um classificador simples treinado nos rótulos.
- **Saída:** categoria (`depressao_pos_parto`, `ansiedade`, `violencia`, `fadiga`, `neutro`) + confiança.

## Tarefa 2.5 — Análise de texto (NLP)
- **Entrada:** laudos, exames e evolução clínica (Fase 1, Tarefa 1.5).
- **Abordagem (enxuta):** extração de palavras-chave de risco + **análise de sentimento** (Azure Text Analytics) ou um classificador simples.
- **Saída:** lista de achados de risco no texto + categoria (ex.: `complicacao`, `sinal_infeccao`, `neutro`).
- Padronizar a saída num dicionário para a fusão.

## Tarefa 2.6 — Baseline por modalidade única
- Antes da fusão, registre a performance de **cada modalidade isolada** detectando o evento de risco.
- Servirá de comparação para provar, na Fase 3, que a **fusão reduz falsos positivos / melhora a detecção**.

## Tarefa 2.7 — Definição de limiares clínicos (gatilhos)
Documentar os disparadores matemáticos do alerta, por exemplo:

| Sinal | Condição de alerta |
|-------|--------------------|
| PA sistólica / diastólica | `≥ 140/90 mmHg` (sinal de hipertensão/pré-eclâmpsia) |
| Modelo de sinais vitais | classe `high risk` |
| Detecção visual na cicatriz | classe `ferida_alerta` com confiança `≥ 0.7` |
| Fisioterapia (pose) | execução `incorreta` / regressão na amplitude |
| Risco no áudio | categoria de risco com confiança `≥ 0.7` |
| Achado no texto clínico | termo/categoria de risco identificado |

> Esses limiares alimentam o **motor de fusão** da Fase 3.

---

## Dicas
- Treine sempre primeiro no **mini-dataset** (rápido) e só depois escale.
- Guarde os **gráficos e métricas** — vão direto para o relatório técnico e o vídeo.
- Padronize a saída de cada modelo num dicionário Python para facilitar a fusão.
