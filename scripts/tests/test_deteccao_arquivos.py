"""Testes de detecção/inferência de áudio (nomes/extensões flexíveis)."""

from __future__ import annotations

from scripts.data_prep.audio_transcrever import (
    inferir_categoria,
    listar_audios,
)


def test_inferir_categoria_audio():
    assert inferir_categoria("relato_ansiedade.wav") == "ansiedade"
    assert inferir_categoria("01-DEPRESSAO-maria.mp3") == "depressao_pos_parto"
    assert inferir_categoria("violencia_caso2.m4a") == "violencia"
    assert inferir_categoria("audio_qualquer.wav") is None
    # Androids Corpus: pasta HC (healthy control) -> neutro.
    assert inferir_categoria("Androids-Corpus/Interview-Task/audio/HC/01_CF56_1.wav") == "neutro"


def test_listar_audios_detecta_qualquer_nome(tmp_path):
    (tmp_path / "qualquer_nome.wav").write_bytes(b"\x00")
    (tmp_path / "OUTRO.MP3").write_bytes(b"\x00")
    (tmp_path / "ignorar.txt").write_text("x")
    achados = {p.name for p in listar_audios(tmp_path)}
    assert achados == {"qualquer_nome.wav", "OUTRO.MP3"}


def test_listar_audios_recursivo_em_subpastas(tmp_path):
    sub = tmp_path / "lote1" / "neutro"
    sub.mkdir(parents=True)
    (sub / "a.wav").write_bytes(b"\x00")
    (tmp_path / "topo.mp3").write_bytes(b"\x00")
    achados = {p.relative_to(tmp_path).as_posix() for p in listar_audios(tmp_path)}
    assert achados == {"lote1/neutro/a.wav", "topo.mp3"}


