"""Testes da verificação de conformidade LGPD (Fase 7 — F7-08)."""

from __future__ import annotations

from scripts.check_conformidade import violacoes_dados, violacoes_segredos


def test_allowlist_data_permite_metadados_sinteticos():
    arquivos = [
        "data/README.md",
        "data/casos/caso_alto.json",
        "data/texto_clinico/rotulos.json",
        "data/video_cicatriz/data.yaml",
        "src/app.js",
    ]
    assert violacoes_dados(arquivos) == []


def test_allowlist_permite_datasets_sinteticos_versionados():
    # Datasets sintéticos/públicos versionados para reprodutibilidade (rodar/treinar sem baixar).
    arquivos = [
        "data/audio/fase8/violencia/audio_0000.wav",
        "data/audio/fase8/violencia/manifest.csv",
        "data/sinais_vitais/maternal_clean.csv",
        "data/texto_clinico/evolucao_01.txt",
        "data/texto_clinico/fase8/violencia_pt.csv",
        "data/video_cicatriz/Train.zip",
        "data/casos/audio-violencia.mp3",
    ]
    assert violacoes_dados(arquivos) == []


def test_data_fora_da_allowlist_e_violacao():
    # Um CSV solto em data/casos/ ou áudio fora da pasta de treino ainda é violação (dado real).
    arquivos = ["data/casos/paciente_real.csv", "data/audio/gravacao.wav"]
    assert set(violacoes_dados(arquivos)) == set(arquivos)


def test_env_e_chaves_sao_violacao():
    arquivos = [".env", "backend/.env", "certs/server.key", "certs/server.crt", "src/app.js"]
    violacoes = violacoes_segredos(arquivos)
    assert ".env" in violacoes
    assert "backend/.env" in violacoes
    assert "certs/server.key" in violacoes
    assert "certs/server.crt" in violacoes
    assert "src/app.js" not in violacoes
