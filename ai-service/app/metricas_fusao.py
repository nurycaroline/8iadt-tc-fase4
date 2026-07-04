"""Métrica do ganho da fusão (Tarefa 3.1b) — o diferencial avaliado.

Compara, sobre um conjunto de casos rotulados, a detecção de **caso crítico** em 4 cenários:
``só-vídeo``, ``só-vitais``, ``só-áudio/texto`` e ``fusão``. Reusa
:func:`app.baseline.metricas_modalidade` para precisão, recall e **taxa de falsos positivos**.

Hipótese clínica (docs/03 §3.1b): um sistema de **modalidade única**, para não perder casos, alerta
diante de **qualquer** sinal isolado (gerando falsos positivos e perdendo o que não enxerga); a
**fusão** só eleva ao alerta vermelho (``ALTO``) quando há **corroboração** entre modalidades —
reduzindo falsos positivos e aumentando o recall dos casos realmente críticos.

Por isso:

- cenário de **modalidade única**: prediz "crítico" quando a fusão **restrita àquela modalidade**
  sai do ``BAIXO`` (qualquer sinal de risco);
- cenário de **fusão**: prediz "crítico" apenas quando o risco combinado é ``ALTO``.

Uso (a partir de ai-service/)::

    python -m app.metricas_fusao
"""

from __future__ import annotations

import sys

from app.baseline import metricas_modalidade
from app.common import get_logger, models_dir, salvar_metricas
from app.fusao import avaliar_fusao
from app.schemas import (
    evidencia_audio,
    evidencia_cicatriz,
    evidencia_sinais_vitais,
    evidencia_texto,
)

LOG = get_logger("metricas_fusao")

# Modalidades incluídas em cada cenário de modalidade única.
CENARIOS = {
    "so_video": ("video_cicatriz",),
    "so_vitais": ("sinais_vitais",),
    "so_audio_texto": ("audio", "texto"),
}


def casos_avaliacao() -> list[dict]:
    """Conjunto sintético rotulado (``critico`` = exige alerta vermelho) para a comparação.

    Inclui casos críticos que exigem corroboração multimodal e "quase-alertas" isolados (uma única
    modalidade com sinal fraco) que **não** devem disparar o vermelho — base do ganho da fusão.
    """
    return [
        {
            "nome": "infeccao_puerperal",
            "critico": True,
            "evidencias": {
                "video_cicatriz": evidencia_cicatriz("sinal_infeccao", 0.9),
                "sinais_vitais": evidencia_sinais_vitais("hipertensao", "150/95"),
            },
        },
        {
            "nome": "pre_eclampsia",
            "critico": True,
            "evidencias": {
                "sinais_vitais": evidencia_sinais_vitais("hipertensao", "152/98"),
                "texto": evidencia_texto("complicacao", "cefaleia e proteinuria"),
            },
        },
        {
            "nome": "violencia",
            "critico": True,
            "evidencias": {"audio": evidencia_audio("violencia", 0.9)},
        },
        {
            "nome": "vermelhidao_leve_isolada",
            "critico": False,
            "evidencias": {"video_cicatriz": evidencia_cicatriz("sinal_infeccao", 0.8)},
        },
        {
            "nome": "ansiedade_isolada",
            "critico": False,
            "evidencias": {"audio": evidencia_audio("ansiedade", 0.8)},
        },
        {
            "nome": "tudo_normal",
            "critico": False,
            "evidencias": {
                "video_cicatriz": evidencia_cicatriz("ferida_ok", 0.8),
                "sinais_vitais": evidencia_sinais_vitais("normal", "110/70"),
                "audio": evidencia_audio("neutro", 0.5),
                "texto": evidencia_texto("neutro", ""),
            },
        },
    ]


def _predizer_modalidade(evidencias: dict, chaves: tuple[str, ...]) -> bool:
    sub = {k: evidencias[k] for k in chaves if k in evidencias}
    return avaliar_fusao(sub)["risco_detectado"] != "BAIXO"


def _predizer_fusao(evidencias: dict) -> bool:
    return avaliar_fusao(evidencias)["risco_detectado"] == "ALTO"


def comparar(casos: list[dict] | None = None) -> dict:
    """Avalia os 4 cenários e devolve a tabela comparativa (precisão/recall/taxa de FP)."""
    casos = casos if casos is not None else casos_avaliacao()
    y_true = [c["critico"] for c in casos]

    resultado: dict = {}
    for nome, chaves in CENARIOS.items():
        y_pred = [_predizer_modalidade(c["evidencias"], chaves) for c in casos]
        resultado[nome] = metricas_modalidade(y_true, y_pred)
    y_pred_fusao = [_predizer_fusao(c["evidencias"]) for c in casos]
    resultado["fusao"] = metricas_modalidade(y_true, y_pred_fusao)
    return resultado


def main() -> int:
    comparacao = comparar()
    saida = salvar_metricas(models_dir() / "metricas_fusao.json", comparacao)
    LOG.info("Métricas da fusão salvas em %s (%d cenários).", saida, len(comparacao))
    for nome, m in comparacao.items():
        LOG.info(
            "%-16s precisao=%.2f recall=%.2f fp=%.2f",
            nome,
            m["precisao"],
            m["recall"],
            m["taxa_falsos_positivos"],
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
