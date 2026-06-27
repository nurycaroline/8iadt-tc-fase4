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
# Categoria legada de áudio — mantida por compatibilidade; na Fase 8 é **derivada** da análise
# dupla (acústico + texto), não mais por palavras-chave (ver evidencia_audio_unificada).
CATEGORIAS_AUDIO = ("neutro", "ansiedade", "depressao_pos_parto", "violencia", "fadiga")
ACHADOS_TEXTO = ("complicacao", "sinal_infeccao", "neutro")
# Rótulos binários dos classificadores ML da Fase 8 (texto e áudio acústico).
ROTULOS_DEPRESSAO = ("depressao", "neutro")
ROTULOS_VIOLENCIA = ("violencia", "neutro")


def _validar(valor: str, dominio: tuple[str, ...], campo: str) -> str:
    if valor not in dominio:
        raise ValueError(f"{campo} inválido: {valor!r}. Use um de {dominio}.")
    return valor


def _confianca(valor: float) -> float:
    conf = float(valor)
    if not 0.0 <= conf <= 1.0:
        raise ValueError(f"confianca fora de [0, 1]: {conf!r}.")
    return round(conf, 4)


def _subevidencia(
    valor: Any, dominio: tuple[str, ...], neutro: str = "neutro"
) -> dict[str, Any]:
    """Constrói uma subevidência binária ``{rotulo, confianca}`` (depressão/violência).

    ``valor`` pode ser ``None`` (→ ``neutro`` com confiança 0), um par ``(rotulo, confianca)`` ou
    um dicionário ``{"rotulo", "confianca"}``. O rótulo é validado contra ``dominio``.
    """
    if valor is None:
        return {"rotulo": neutro, "confianca": 0.0}
    if isinstance(valor, dict):
        rotulo, conf = valor.get("rotulo", neutro), valor.get("confianca", 0.0)
    else:
        rotulo, conf = valor
    return {
        "rotulo": _validar(rotulo, dominio, "rotulo"),
        "confianca": _confianca(conf),
    }


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
    """Evidência **legada** do áudio: ``{categoria, confianca}`` (contrato §3 pré-Fase 8).

    Mantida por compatibilidade (testes/baseline e métrica da fusão). Na Fase 8, o módulo de áudio
    passa a produzir :func:`evidencia_audio_unificada` (análise dupla acústico + texto).
    """
    return {
        "categoria": _validar(categoria, CATEGORIAS_AUDIO, "categoria"),
        "confianca": _confianca(confianca),
    }


def _derivar_categoria_legada(
    acustico: dict[str, Any], texto: dict[str, Any]
) -> tuple[str, float]:
    """Deriva a categoria legada do áudio (compat) a partir da análise dupla da Fase 8.

    Regra (decisão da Fase 8): ``violencia`` se o acústico **ou** o texto indicarem violência;
    ``depressao_pos_parto`` se o texto indicar depressão; senão ``neutro``.
    """
    viol_ac = acustico.get("rotulo") == "violencia"
    viol_txt_sub = (texto.get("violencia") or {})
    viol_txt = viol_txt_sub.get("rotulo") == "violencia"
    if viol_ac or viol_txt:
        conf = max(
            float(acustico.get("confianca", 0.0)) if viol_ac else 0.0,
            float(viol_txt_sub.get("confianca", 0.0)) if viol_txt else 0.0,
        )
        return "violencia", _confianca(conf)
    depr_sub = texto.get("depressao") or {}
    if depr_sub.get("rotulo") == "depressao":
        return "depressao_pos_parto", _confianca(depr_sub.get("confianca", 0.0))
    return "neutro", 0.5


def evidencia_audio_unificada(
    acustico: Any, transcricao: str, texto: dict[str, Any]
) -> dict[str, Any]:
    """Evidência de áudio da Fase 8: análise **dupla** (acústico + transcrição→texto unificado).

    ``{acustico: {rotulo, confianca}, transcricao, texto: {…evidência de texto…}}`` mais os campos
    **legados** ``categoria``/``confianca`` derivados (compatibilidade com a fusão/relatório).
    """
    ac = _subevidencia(acustico, ROTULOS_VIOLENCIA)
    categoria, confianca = _derivar_categoria_legada(ac, texto)
    return {
        "acustico": ac,
        "transcricao": str(transcricao or ""),
        "texto": texto,
        "categoria": categoria,
        "confianca": confianca,
    }


def evidencia_texto(
    achado: str,
    trecho: str = "",
    *,
    depressao: Any = None,
    violencia: Any = None,
) -> dict[str, Any]:
    """Evidência do texto clínico unificada (Fase 8).

    ``{achado, trecho, depressao: {rotulo, confianca}, violencia: {rotulo, confianca}}``. O
    ``achado`` segue as keywords de infecção/complicação (preservadas); ``depressao``/``violencia``
    vêm dos classificadores ML (ou do fallback por keywords). Sem os sinais, ficam ``neutro``.
    """
    return {
        "achado": _validar(achado, ACHADOS_TEXTO, "achado"),
        "trecho": str(trecho),
        "depressao": _subevidencia(depressao, ROTULOS_DEPRESSAO),
        "violencia": _subevidencia(violencia, ROTULOS_VIOLENCIA),
    }
