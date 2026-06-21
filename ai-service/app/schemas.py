"""Construtores dos dicionários de **evidência** padronizados por modalidade.

Cada função garante que apenas valores do **contrato de API** (docs/contrato-api.md §3) sejam
produzidos. Valor fora do domínio levanta :class:`ValueError`. A Fase 3 (motor de fusão) consome
esses dicionários diretamente, sem adaptação.
"""

from __future__ import annotations

from typing import Any

# Domínios de valores (contrato-api.md §3).
EVENTOS_CICATRIZ = ("ferida_ok", "sinal_infeccao", "nenhum")
EXECUCOES_FISIOTERAPIA = ("correta", "incorreta", "nao_avaliado")
TIPOS_SINAIS_VITAIS = ("normal", "risco_medio", "hipertensao", "pre_eclampsia")
CATEGORIAS_AUDIO = ("neutro", "ansiedade", "depressao_pos_parto", "violencia", "fadiga")
ACHADOS_TEXTO = ("complicacao", "sinal_infeccao", "neutro")


def _validar(valor: str, dominio: tuple[str, ...], campo: str) -> str:
    if valor not in dominio:
        raise ValueError(f"{campo} inválido: {valor!r}. Use um de {dominio}.")
    return valor


def _confianca(valor: float) -> float:
    conf = float(valor)
    if not 0.0 <= conf <= 1.0:
        raise ValueError(f"confianca fora de [0, 1]: {conf!r}.")
    return round(conf, 4)


def evidencia_cicatriz(evento: str, confianca: float) -> dict[str, Any]:
    """Evidência do detector de cicatriz: ``{evento, confianca}``."""
    return {
        "evento": _validar(evento, EVENTOS_CICATRIZ, "evento"),
        "confianca": _confianca(confianca),
    }


def evidencia_fisioterapia(execucao: str, amplitude: str | None = None) -> dict[str, Any]:
    """Evidência da fisioterapia: ``{execucao, amplitude}`` (amplitude opcional)."""
    evid: dict[str, Any] = {
        "execucao": _validar(execucao, EXECUCOES_FISIOTERAPIA, "execucao")
    }
    if amplitude is not None:
        evid["amplitude"] = str(amplitude)
    return evid


def evidencia_sinais_vitais(tipo: str, valor: str) -> dict[str, Any]:
    """Evidência dos sinais vitais: ``{tipo, valor}``."""
    return {
        "tipo": _validar(tipo, TIPOS_SINAIS_VITAIS, "tipo"),
        "valor": str(valor),
    }


def evidencia_audio(categoria: str, confianca: float) -> dict[str, Any]:
    """Evidência do áudio: ``{categoria, confianca}``."""
    return {
        "categoria": _validar(categoria, CATEGORIAS_AUDIO, "categoria"),
        "confianca": _confianca(confianca),
    }


def evidencia_texto(achado: str, trecho: str = "") -> dict[str, Any]:
    """Evidência do texto clínico: ``{achado, trecho}``."""
    return {
        "achado": _validar(achado, ACHADOS_TEXTO, "achado"),
        "trecho": str(trecho),
    }
