"""Testes de detecção/inferência de áudio e fisioterapia (nomes/extensões flexíveis)."""

from __future__ import annotations

from scripts.data_prep.audio_transcrever import (
    inferir_categoria,
    listar_audios,
)
from scripts.data_prep.fisioterapia_pose import (
    coletar_amostras,
    inferir_execucao,
    montar_metadado,
    parse_intellirehab,
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


def test_parse_intellirehab():
    info = parse_intellirehab("106_18_2_3_1_stand")
    assert info == {
        "subject": "106", "date": "18", "gesture": "2",
        "repeticao": "3", "correct_label": "1", "position": "stand",
    }
    assert parse_intellirehab("nome_qualquer") is None


def test_inferir_execucao_fisio():
    # CorrectLabel do padrão IntelliRehabDS (5º campo): 1=correto, 2=incorreto.
    assert inferir_execucao("106_18_2_3_1_stand") == "correto"
    assert inferir_execucao("106_18_2_3_2_stand") == "incorreto"
    # Fallback por palavra-chave quando não casa o padrão.
    assert inferir_execucao("agachamento_incorreto.mp4") == "incorreto"
    assert inferir_execucao("agachamento_01.mp4") == "correto"


def test_coletar_amostras_sequencia_depth(tmp_path):
    # Pasta de gesto com frames PNG -> 1 amostra (sequência), não 1 por imagem.
    seq = tmp_path / "DepthImages1-2" / "106_18_2_3_2_stand"
    seq.mkdir(parents=True)
    for n in ("52978.png", "52979.png", "52980.png"):
        (seq / n).write_bytes(b"\x89PNG")
    registros = coletar_amostras(tmp_path)
    assert len(registros) == 1
    r = registros[0]
    assert r["tipo"] == "sequencia_depth"
    assert r["n_frames"] == 3
    assert r["execucao"] == "incorreto"
    assert r["subject"] == "106" and r["gesture"] == "2"


def test_coletar_amostras_esqueleto_e_video(tmp_path):
    (tmp_path / "108_5_1_2_1_sit.csv").write_text("kp")
    (tmp_path / "exercicio.mp4").write_bytes(b"\x00")
    (tmp_path / "metadados.json").write_text("[]")
    registros = coletar_amostras(tmp_path)
    tipos = {r["arquivo"]: r["tipo"] for r in registros}
    assert tipos == {"108_5_1_2_1_sit.csv": "esqueleto", "exercicio.mp4": "video"}


def test_montar_metadado_valida_execucao():
    m = montar_metadado("ex1.mp4", "ex1", "correto", None)
    assert m["execucao"] == "correto"
    assert m["arquivo"] == "ex1.mp4"
