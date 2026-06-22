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


def test_data_fora_da_allowlist_e_violacao():
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
