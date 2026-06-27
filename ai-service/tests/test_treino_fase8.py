"""Testes dos treinos da Fase 8 — funções puras com fixtures pequenas (sem download/treino pesado).

Validam que o baseline (TF-IDF+LogReg / MFCC+LogReg) **treina com poucas amostras** ("se rodar com
5, roda com 500"), produz um pipeline com ``predict_proba`` e métricas no formato esperado.
"""

from __future__ import annotations

import numpy as np

from app.audio.treino import treinar_acustico
from app.texto.treino import treinar_texto

TEXTOS = [
    "me sinto triste e sem esperanca, choro o tempo todo",
    "tristeza profunda, vazio e anedonia constante",
    "nao sinto prazer em nada, desanimo total",
    "sem vontade de viver, muita tristeza e culpa",
    "consulta tranquila, tudo bem, sem queixas",
    "pressao normal, amamentando bem, rotina",
    "exames normais, paciente estavel",
    "acompanhamento de rotina sem intercorrencias",
]
LABELS = [1, 1, 1, 1, 0, 0, 0, 0]


def test_treinar_texto_pipeline_e_metricas():
    pipeline, metricas, y_te, y_pred = treinar_texto(TEXTOS, LABELS)
    # O pipeline expõe predict_proba para a inferência de confiança.
    proba = pipeline.predict_proba(["estou muito triste e sem esperanca"])[0]
    assert len(proba) == 2
    assert {"f1_macro", "acuracia", "matriz_confusao", "n_treino", "n_teste"} <= set(metricas)
    assert len(y_te) == len(y_pred)


def test_treinar_texto_poucas_amostras_in_sample():
    # 4 amostras: cai no modo in-sample sem quebrar (filosofia mini-dataset).
    pipeline, metricas, _, _ = treinar_texto(TEXTOS[:2] + TEXTOS[4:6], [1, 1, 0, 0])
    assert metricas["avaliacao"].startswith("in-sample")
    assert pipeline.predict(["tudo bem, rotina"]).shape == (1,)


def test_treinar_acustico_com_features_sinteticas():
    rng = np.random.default_rng(0)
    # 2 classes separáveis em 40 dimensões (como o vetor MFCC média+desvio).
    pos = rng.normal(2.0, 0.5, size=(6, 40))
    neg = rng.normal(-2.0, 0.5, size=(6, 40))
    features = np.vstack([pos, neg])
    labels = [1] * 6 + [0] * 6
    pipeline, metricas, y_te, y_pred = treinar_acustico(features, labels)
    assert pipeline.predict_proba(features[:1]).shape[1] == 2
    assert metricas["f1_macro"] >= 0.5
