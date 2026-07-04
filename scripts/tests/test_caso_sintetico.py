"""Testes do builder e das variantes do caso sintético (T10/T11)."""

from __future__ import annotations

import pytest

from scripts.data_prep.caso_sintetico import gerar_variantes, montar_caso

PACIENTE = {"id": "pac-001", "primeiro_nome": "Maria", "idade": 31}


def test_montar_caso_estrutura_contrato():
    caso = montar_caso(
        "abc-123",
        PACIENTE,
        dados_vitais_csv="data/sinais_vitais/x.csv",
        texto_clinico="data/texto_clinico/e1.txt",
    )
    assert caso["case_id"] == "abc-123"
    assert caso["paciente"]["id"] == "pac-001"
    assert caso["dados_vitais"] == {"csv_url": "data/sinais_vitais/x.csv"}
    assert caso["texto_clinico"] == "data/texto_clinico/e1.txt"


def test_montar_caso_omite_modalidade_ausente():
    caso = montar_caso("abc-1", PACIENTE, dados_vitais_csv="x.csv")
    # Modalidades não fornecidas não aparecem no JSON (campos opcionais no contrato).
    assert "audio_url" not in caso
    assert "video_cicatriz_url" not in caso


def test_montar_caso_valida_obrigatorios():
    with pytest.raises(ValueError):
        montar_caso("", PACIENTE)
    with pytest.raises(ValueError):
        montar_caso("abc", {"primeiro_nome": "Maria"})


def test_gerar_variantes_tres_niveis():
    variantes = gerar_variantes()
    assert set(variantes) == {"caso_baixo", "caso_medio", "caso_alto"}
    # ALTO tem cicatriz de alerta + texto de sinal de infecção.
    assert "ferida_alerta" in variantes["caso_alto"]["video_cicatriz_url"]
    assert variantes["caso_alto"]["texto_clinico"].endswith("evolucao_02.txt")
    # BAIXO referencia ferida_ok e evolução neutra.
    assert "ferida_ok" in variantes["caso_baixo"]["video_cicatriz_url"]
    # MEDIO é risco isolado: sem vídeo de cicatriz.
    assert "video_cicatriz_url" not in variantes["caso_medio"]
    # Todas as variantes seguem o contrato (case_id + paciente.id).
    for caso in variantes.values():
        assert caso["case_id"]
        assert caso["paciente"]["id"]
