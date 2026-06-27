"""Carregamento **tolerante** de classificadores ML locais da Fase 8 (joblib).

Os classificadores de depressão/violência (texto) e de violência acústica (áudio) são treinados
offline (ver ``scripts/treino_*``) e salvos em ``ai-service/models/<modalidade>/<nome>.joblib``. Em
produção/CI os pesos **não são versionados** (política do repo), então o carregamento precisa
**degradar sem quebrar**: se o artefato não existir ou as libs de IA faltarem, devolve ``None`` e o
módulo de inferência cai no fallback por palavras-chave (mesma filosofia DD10 das fases anteriores).
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
