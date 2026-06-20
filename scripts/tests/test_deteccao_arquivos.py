"""Testes de detecção/inferência de áudio e fisioterapia (nomes/extensões flexíveis)."""

from __future__ import annotations

from scripts.data_prep.audio_transcrever import (
    inferir_categoria,
    listar_audios,
)
from scripts.data_prep.fisioterapia_pose import (
    inferir_execucao,
    listar_amostras,
    montar_metadado,
)


def test_inferir_categoria_audio():
    assert inferir_categoria("relato_ansiedade.wav") == "ansiedade"
    assert inferir_categoria("01-DEPRESSAO-maria.mp3") == "depressao_pos_parto"
    assert inferir_categoria("violencia_caso2.m4a") == "violencia"
    assert inferir_categoria("audio_qualquer.wav") is None


def test_listar_audios_detecta_qualquer_nome(tmp_path):
    (tmp_path / "qualquer_nome.wav").write_bytes(b"\x00")
    (tmp_path / "OUTRO.MP3").write_bytes(b"\x00")
    (tmp_path / "ignorar.txt").write_text("x")
    achados = {p.name for p in listar_audios(tmp_path)}
    assert achados == {"qualquer_nome.wav", "OUTRO.MP3"}


def test_inferir_execucao_fisio():
    assert inferir_execucao("agachamento_incorreto.mp4") == "incorreto"
    assert inferir_execucao("exercicio_errado.avi") == "incorreto"
    assert inferir_execucao("agachamento_01.mp4") == "correto"


def test_listar_amostras_fisio_videos_e_esqueletos(tmp_path):
    (tmp_path / "ex1.mp4").write_bytes(b"\x00")
    (tmp_path / "ex2.txt").write_text("skeleton")
    (tmp_path / "metadados.json").write_text("[]")
    (tmp_path / ".oculto.mp4").write_bytes(b"\x00")
    achados = {p.name for p in listar_amostras(tmp_path)}
    assert achados == {"ex1.mp4", "ex2.txt"}


def test_montar_metadado_valida_execucao():
    m = montar_metadado("ex1.mp4", "ex1", "correto", None)
    assert m["execucao"] == "correto"
    assert m["arquivo"] == "ex1.mp4"
