"""Testes das funções puras do detector de cicatriz (T7 métricas, T9 mapeamento)."""

from __future__ import annotations

from app.cicatriz.inferencia import detectar, mapear_evento
from app.cicatriz.treino import extrair_metricas


def test_mapeia_alerta_acima_do_limiar():
    assert mapear_evento("ferida_alerta", 0.86) == "sinal_infeccao"


def test_alerta_abaixo_do_limiar_vira_nenhum():
    assert mapear_evento("ferida_alerta", 0.5) == "nenhum"


def test_ferida_ok():
    assert mapear_evento("ferida_ok", 0.9) == "ferida_ok"


def test_sem_deteccao():
    assert mapear_evento(None, 0.0) == "nenhum"


def test_extrair_metricas(tmp_path):
    csv = tmp_path / "results.csv"
    csv.write_text(
        "epoch, metrics/precision(B), metrics/recall(B), metrics/mAP50(B)\n"
        "1, 0.5, 0.4, 0.45\n"
        "2, 0.8, 0.75, 0.82\n",
        encoding="utf-8",
    )
    m = extrair_metricas(csv)
    assert m["mAP50"] == 0.82
    assert m["precisao"] == 0.8
    assert m["recall"] == 0.75
    assert m["epocas"] == 2


def test_detectar_sem_modelo_retorna_nenhum(tmp_path):
    # Sem peso treinado, degrada para evento=nenhum (DD10).
    evid = detectar("inexistente.jpg", modelo_path=tmp_path / "nao_existe.pt")
    assert evid == {"evento": "nenhum", "confianca": 0.0}
