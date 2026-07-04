"""Motor de fusão clínica (Tarefa 3.1) — o núcleo de valor da Fase 3.

Cruza as **evidências** das modalidades da mesma paciente (cada uma no formato do contrato §3,
produzido pela Fase 2) e devolve **um** nível de risco explicável + os gatilhos acionados.

Princípio (docs/00 D5): a fusão é um **motor de regras explícito**, não end-to-end. A IA das
modalidades produz evidências; a regra de negócio decide e explica o alerta. Tudo determinístico,
puro e testável (sem IO, sem rede).

Saída::

    {
      "risco_detectado": "ALTO" | "MEDIO" | "BAIXO",
      "mensagem_alerta": "<texto explicável>",
      "gatilhos": ["infeccao_puerperal", ...],   # rastreabilidade para o relatório
    }

Regras (contrato §4 + docs/03 Tarefa 3.1):

- **Matriz base** (cicatriz × sinais vitais): infecção+risco → ``ALTO``; infecção+normal →
  ``MEDIO``; ok/nenhum+risco → ``MEDIO``; ok/nenhum+normal → ``BAIXO``.
- **Elevação por contexto** (texto/áudio): cicatriz infecção + febre/dor → infecção puerperal
  (``ALTO``); vitais de risco + cefaleia/proteinúria → pré-eclâmpsia (``ALTO``); **violência**
  (acústica no som, relato em áudio ou classificador ML de texto) → protocolo de proteção
  (``ALTO``); **depressão** (classificador ML de texto) ou áudio de depressão/ansiedade →
  desconforto psicológico (≥ ``MEDIO``).
- **Contexto isolado**: quando a única fonte de risco é texto/áudio fraco, o teto é ``MEDIO`` (o
  contrato trata texto/áudio como contexto adicional) — a única exceção é a **violência**, que
  aciona o protocolo mesmo isolada.
"""

from __future__ import annotations

from typing import Any

from app.limiares import confianca_suficiente, confianca_texto_suficiente

# Ordem dos níveis de risco (para escolher o maior gatilho acionado).
NIVEIS = ("BAIXO", "MEDIO", "ALTO")
_ORDEM = {nivel: i for i, nivel in enumerate(NIVEIS)}

# Tipos de sinais vitais considerados "de risco" na matriz base (contrato §4).
TIPOS_VITAIS_RISCO = ("risco_medio", "hipertensao", "pre_eclampsia")

# Mensagem padronizada por gatilho (explicabilidade do alerta).
MENSAGENS = {
    "infeccao_puerperal": (
        "Sinal de infecção na cicatriz associado a febre/dor ou sinais vitais de risco — "
        "suspeita de infecção puerperal."
    ),
    "pre_eclampsia": (
        "Sinais vitais de risco com cefaleia/proteinúria — suspeita de pré-eclâmpsia."
    ),
    "violencia": (
        "Indício de violência no relato em áudio — acionar protocolo de proteção."
    ),
    "desconforto_psicologico": (
        "Relato com sinais de depressão pós-parto/ansiedade — encaminhamento psicológico."
    ),
    "cicatriz_infeccao": (
        "Sinal de infecção na cicatriz sem febre/PA associadas — reavaliar a ferida operatória."
    ),
    "sinais_vitais_risco": (
        "Sinais vitais alterados (PA/condição de risco) — monitorar a paciente."
    ),
    "texto_complicacao": (
        "Achado de complicação no texto clínico — contexto adicional para a avaliação."
    ),
    "texto_infeccao": (
        "Relato de febre/dor na evolução clínica — contexto adicional para a avaliação."
    ),
}

# Recomendação/encaminhamento por nível (usada pelo relatório, docs/06 §4).
RECOMENDACAO = {
    "ALTO": "Acionar a equipe imediatamente e priorizar avaliação médica.",
    "MEDIO": "Agendar reavaliação e acompanhar a evolução de perto.",
    "BAIXO": "Manter o acompanhamento de rotina.",
}


def _nivel_max(a: str, b: str) -> str:
    return a if _ORDEM[a] >= _ORDEM[b] else b


def _texto_violencia(texto: dict[str, Any] | None) -> bool:
    """True se a subevidência de violência do texto (Fase 8) atinge o limiar de risco."""
    sub = (texto or {}).get("violencia") or {}
    return sub.get("rotulo") == "violencia" and confianca_texto_suficiente(
        sub.get("confianca", 0.0)
    )


def _texto_depressao(texto: dict[str, Any] | None) -> bool:
    """True se a subevidência de depressão do texto (Fase 8) atinge o limiar de risco."""
    sub = (texto or {}).get("depressao") or {}
    return sub.get("rotulo") == "depressao" and confianca_texto_suficiente(
        sub.get("confianca", 0.0)
    )


def avaliar_fusao(evidencias: dict[str, Any]) -> dict[str, Any]:
    """Cruza as evidências e devolve ``{risco_detectado, mensagem_alerta, gatilhos}``.

    ``evidencias`` é um dicionário com chaves opcionais ``video_cicatriz``, ``sinais_vitais``,
    ``audio`` e ``texto`` (cada valor no formato do contrato §3). Modalidade ausente é simplesmente
    ignorada (a fusão avalia com o que tem, sem quebrar).
    """
    cic = evidencias.get("video_cicatriz") or {}
    vit = evidencias.get("sinais_vitais") or {}
    aud = evidencias.get("audio") or {}
    txt = evidencias.get("texto") or {}

    cic_infeccao = cic.get("evento") == "sinal_infeccao"
    vitais_risco = vit.get("tipo") in TIPOS_VITAIS_RISCO
    pre_eclampsia_explicita = vit.get("tipo") == "pre_eclampsia"
    texto_infeccao = txt.get("achado") == "sinal_infeccao"
    texto_complicacao = txt.get("achado") == "complicacao"
    audio_categoria = aud.get("categoria")
    audio_forte = confianca_suficiente(aud.get("confianca", 0.0))

    # Trilha acústica de violência (Fase 8): classificador do som, gatilho com confiança >= 0.7.
    aud_acustico = aud.get("acustico") or {}
    violencia_acustica = aud_acustico.get("rotulo") == "violencia" and confianca_suficiente(
        aud_acustico.get("confianca", 0.0)
    )

    # Sinais ML de texto (Fase 8): considera o texto digitado **e** a transcrição do áudio.
    aud_texto = aud.get("texto")
    violencia_texto = _texto_violencia(txt) or _texto_violencia(aud_texto)
    depressao_texto = _texto_depressao(txt) or _texto_depressao(aud_texto)

    # Febre/dor relatada (contexto de infecção): laudo de infecção ou áudio de fadiga/dor.
    relato_febre_dor = texto_infeccao or (audio_categoria == "fadiga" and audio_forte)

    gatilhos: list[str] = []
    risco = "BAIXO"

    def acionar(gatilho: str, nivel: str) -> None:
        nonlocal risco
        if gatilho not in gatilhos:
            gatilhos.append(gatilho)
        risco = _nivel_max(risco, nivel)

    # 1) Regras de elevação (ALTO) — combinam modalidades "fortes" (cicatriz/vitais) com contexto.
    if cic_infeccao and (vitais_risco or relato_febre_dor):
        acionar("infeccao_puerperal", "ALTO")
    if (vitais_risco and texto_complicacao) or pre_eclampsia_explicita:
        acionar("pre_eclampsia", "ALTO")
    # Violência aciona o protocolo mesmo isolada: som (acústico), relato (áudio legado) ou texto ML.
    if (audio_categoria == "violencia" and audio_forte) or violencia_acustica or violencia_texto:
        acionar("violencia", "ALTO")

    # 2) Desconforto psicológico — ao menos MEDIO: áudio legado ou depressão no texto (ML).
    if (audio_categoria in ("depressao_pos_parto", "ansiedade") and audio_forte) or depressao_texto:
        acionar("desconforto_psicologico", "MEDIO")

    # 3) Matriz base — contribuições MEDIO que não foram subsumidas por um gatilho ALTO acima.
    if cic_infeccao and "infeccao_puerperal" not in gatilhos:
        acionar("cicatriz_infeccao", "MEDIO")
    if vitais_risco and "pre_eclampsia" not in gatilhos:
        acionar("sinais_vitais_risco", "MEDIO")

    # 4) Contexto isolado (texto) — eleva no máximo para MEDIO (contrato §4: contexto adicional).
    if texto_complicacao and "pre_eclampsia" not in gatilhos:
        acionar("texto_complicacao", "MEDIO")
    if texto_infeccao and "infeccao_puerperal" not in gatilhos:
        acionar("texto_infeccao", "MEDIO")

    return {
        "risco_detectado": risco,
        "mensagem_alerta": _montar_mensagem(risco, gatilhos),
        "gatilhos": gatilhos,
    }


def _montar_mensagem(risco: str, gatilhos: list[str]) -> str:
    """Concatena as mensagens dos gatilhos acionados (ou mensagem neutra se nenhum)."""
    if not gatilhos:
        return "Sem evidências suficientes de risco no momento."
    partes = [MENSAGENS[g] for g in gatilhos if g in MENSAGENS]
    return " ".join(partes) if partes else "Sem evidências suficientes de risco no momento."
