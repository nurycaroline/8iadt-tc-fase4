"""Testes do adaptador de storage local (Tarefa 3.4 — fallback)."""

from __future__ import annotations

from app.storage import LocalStorage, get_storage


def test_salvar_e_abrir_round_trip(tmp_path):
    storage = LocalStorage(base=tmp_path)
    url = storage.salvar(b"conteudo binario", "relatorios/c1.html", tipo="text/html")
    assert url.endswith("relatorios/c1.html")
    caminho = storage.abrir(url)
    with open(caminho, "rb") as fh:
        assert fh.read() == b"conteudo binario"


def test_salvar_aceita_string(tmp_path):
    storage = LocalStorage(base=tmp_path)
    url = storage.salvar("texto utf-8 ção", "n.txt")
    with open(storage.abrir(url), encoding="utf-8") as fh:
        assert fh.read() == "texto utf-8 ção"


def test_remover_apaga_arquivo(tmp_path):
    storage = LocalStorage(base=tmp_path)
    url = storage.salvar(b"x", "a.bin")
    storage.remover(url)
    assert get_storage  # sanity: símbolo exportado
    from pathlib import Path

    assert not Path(url).exists()


def test_get_storage_default_e_local(monkeypatch):
    monkeypatch.delenv("STORAGE_BACKEND", raising=False)
    assert isinstance(get_storage(), LocalStorage)
    assert isinstance(get_storage("local"), LocalStorage)
