"""Adaptador de armazenamento com interface única (Azure Blob | local) — Tarefa 3.4.

Interface comum (espelhada no Node em ``backend/src/storage/``):

- ``salvar(conteudo, nome, *, tipo=None) -> url``: grava bytes/str e devolve a URL/caminho;
- ``abrir(url) -> caminho_local``: resolve a URL para um arquivo local utilizável pela inferência;
- ``remover(url)``: apaga o artefato.

O backend é escolhido por ``STORAGE_BACKEND`` (``local`` por padrão; ``azure`` exige credencial —
ver :func:`get_storage`). O modo **local** (fallback da demo) grava sob ``data/_storage/`` (ignorado
pelo Git) e resolve caminhos relativos à raiz do projeto.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from app.common import get_logger, project_root

LOG = get_logger("storage")


def _base_dir() -> Path:
    return project_root() / os.environ.get("STORAGE_DIR", "data/_storage")


class LocalStorage:
    """Armazenamento em disco — fallback funcional para a demonstração (design DD8)."""

    def __init__(self, base: str | Path | None = None) -> None:
        self.base = Path(base) if base is not None else _base_dir()

    def salvar(self, conteudo: bytes | str, nome: str, *, tipo: str | None = None) -> str:
        destino = self.base / nome
        destino.parent.mkdir(parents=True, exist_ok=True)
        dados = conteudo.encode("utf-8") if isinstance(conteudo, str) else conteudo
        destino.write_bytes(dados)
        LOG.info("Artefato salvo localmente em %s (%s).", destino, tipo or "?")
        return str(destino)

    def abrir(self, url: str) -> str:
        """Resolve uma URL/caminho para um arquivo local (já é local neste backend)."""
        caminho = Path(url)
        if caminho.exists():
            return str(caminho)
        for candidato in (self.base / url, project_root() / url):
            if candidato.exists():
                return str(candidato)
        # Não encontrado: devolve o melhor palpite (o chamador trata a ausência).
        return str(caminho)

    def remover(self, url: str) -> None:
        caminho = Path(self.abrir(url))
        if caminho.exists():
            caminho.unlink()


def get_storage(backend: str | None = None) -> Any:
    """Seleciona o adaptador de storage por env (``local`` padrão; ``azure`` em :mod:`app`)."""
    backend = (backend or os.environ.get("STORAGE_BACKEND", "local")).lower()
    if backend == "azure":
        try:
            from app.storage_azure import AzureBlobStorage

            return AzureBlobStorage()
        except Exception as exc:  # pragma: no cover - depende de credencial/SDK
            LOG.warning("Storage Azure indisponível (%s); usando fallback local.", exc)
            return LocalStorage()
    return LocalStorage()
