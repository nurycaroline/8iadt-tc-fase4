"""Carregamento **tolerante** de classificadores ML locais da Fase 8 (joblib).

Os classificadores de depressão/violência (texto) e de violência acústica (áudio) são treinados
offline (ver ``scripts/treino_*``) e salvos em ``ai-service/models/<modalidade>/<nome>.joblib``. Os
pesos são versionados via **Git LFS**, mas o carregamento precisa **degradar sem quebrar** quando
estiverem ausentes (ex.: o CI **não baixa** o conteúdo LFS) ou as libs de IA faltarem: nesses casos
devolve ``None`` e o módulo de inferência cai no fallback por palavras-chave (filosofia DD10).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.common import get_logger, models_dir

LOG = get_logger("ml")

# Cache simples por caminho (evita recarregar o joblib a cada inferência).
_CACHE: dict[str, Any] = {}


def carregar_modelo(modalidade: str, nome: str) -> Any | None:
    """Carrega ``models/<modalidade>/<nome>.joblib`` (cacheado) ou ``None`` se indisponível."""
    caminho = models_dir(modalidade) / f"{nome}.joblib"
    chave = str(caminho)
    if chave in _CACHE:
        return _CACHE[chave]
    bundle = _carregar(caminho)
    _CACHE[chave] = bundle
    return bundle


def _carregar(caminho: Path) -> Any | None:
    if not caminho.exists():
        return None
    try:
        import joblib

        return joblib.load(caminho)
    except Exception as exc:  # pragma: no cover - robustez de ambiente
        LOG.warning("Modelo %s indisponível (%s); usando fallback por keywords.", caminho, exc)
        return None


def limpar_cache() -> None:
    """Esvazia o cache (útil em testes após treinar/remover um artefato)."""
    _CACHE.clear()
