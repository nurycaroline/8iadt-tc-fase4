"""Tradução EN→PT em lote, **local/offline** (Fase 8).

Padrão: **Argos Translate** (`argostranslate`, CPU, licença MIT, leve) — baixa **uma vez** o pacote
de idioma `en→pt` e traduz offline a partir daí. Opção preferencial **X-ALMA** (qualidade SOTA,
local) fica selecionável por ``TRADUCAO_BACKEND=xalma`` — apenas **estruturada/documentada** aqui;
o fluxo padrão **não** exige baixar o modelo de 13B (ver ``docs/11-fase8-…``).

Uso programático::

    from scripts.data_prep.traducao import traduzir_lote
    pt = traduzir_lote(["I feel sad and hopeless"])  # -> ["Eu me sinto triste e sem esperança"]
"""

from __future__ import annotations

import os

from .common import get_logger

LOG = get_logger("traducao")

DE = "en"
PARA = "pt"


def _backend() -> str:
    return os.environ.get("TRADUCAO_BACKEND", "argos").strip().lower()


def instalar_idioma_argos() -> None:
    """Garante o pacote de idioma ``en→pt`` do Argos instalado (baixa uma vez; idempotente)."""
    from argostranslate import package, translate

    instalados = {(lng.code) for lng in translate.get_installed_languages()}
    if DE in instalados and PARA in instalados:
        return
    LOG.info("Baixando índice de pacotes Argos e instalando %s→%s...", DE, PARA)
    package.update_package_index()
    disponiveis = package.get_available_packages()
    alvo = next(
        (p for p in disponiveis if p.from_code == DE and p.to_code == PARA), None
    )
    if alvo is None:
        raise RuntimeError(
            f"Pacote Argos {DE}->{PARA} não encontrado no índice. Verifique a rede/versão."
        )
    package.install_from_path(alvo.download())


def _traduzir_argos(textos: list[str]) -> list[str]:
    from argostranslate import translate

    instalar_idioma_argos()
    linguas = {lng.code: lng for lng in translate.get_installed_languages()}
    traducao = linguas[DE].get_translation(linguas[PARA])
    return [traducao.translate(t or "") for t in textos]


def _traduzir_xalma(textos: list[str]) -> list[str]:
    """Backend preferencial (X-ALMA, local). Estruturado, não exigido no fluxo padrão.

    Carrega ``haoranxu/X-ALMA-13B-Group2`` (Group 2 inclui ``pt``) via ``transformers`` em fp16
    (MPS no Apple Silicon). Requer baixar o modelo de 13B — habilite só se já tiver os pesos
    localmente. Ver instruções em ``docs/11-fase8-audio-texto-unificado.md``.
    """
    raise NotImplementedError(
        "Backend X-ALMA é opcional e não baixa o modelo de 13B no fluxo padrão. "
        "Use TRADUCAO_BACKEND=argos (default) ou implemente o carregamento local do X-ALMA "
        "seguindo docs/11-fase8-audio-texto-unificado.md."
    )


def traduzir_lote(textos: list[str]) -> list[str]:
    """Traduz uma lista de textos EN→PT com o backend configurado (Argos por padrão)."""
    if not textos:
        return []
    backend = _backend()
    if backend == "xalma":
        return _traduzir_xalma(textos)
    return _traduzir_argos(textos)


def traduzir(texto: str) -> str:
    """Traduz um único texto EN→PT."""
    return traduzir_lote([texto])[0]
