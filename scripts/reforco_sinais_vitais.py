"""Reforço dos sinais vitais com pré-eclâmpsia sintética e comparação de métricas (Fase 5 — F5-05).

Carrega o dataset limpo da Fase 1 (``data/sinais_vitais/maternal_clean.csv``), gera amostras
**sintéticas de pré-eclâmpsia** (``app``/``scripts`` compartilham o pythonpath) e treina o modelo
**antes e depois** do aumento, registrando a comparação em
``ai-service/models/sinais_vitais/comparacao_preeclampsia.json``.

Os números saem de ``app.sinais_vitais.treino.treinar`` (computação real) — nenhum valor é
inventado (``AGENTS.md``). Sem o dataset base (não baixado neste ambiente), o script avisa e sai
sem fabricar métricas.

Uso (a partir da raiz do repositório)::

    python -m scripts.reforco_sinais_vitais
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ai-service"))

from app.common import get_logger, models_dir, salvar_metricas  # noqa: E402
from app.sinais_vitais.treino import carregar_dataset, comparar_com_aumento  # noqa: E402
from scripts.data_prep.preeclampsia_sintetico import gerar  # noqa: E402

LOG = get_logger("reforco_sinais_vitais")


def main() -> int:
    try:
        df_base = carregar_dataset()
    except FileNotFoundError:
        LOG.error(
            "maternal_clean.csv não encontrado. Rode a Fase 1 primeiro: "
            "python -m scripts.data_prep.sinais_vitais"
        )
        return 1

    n_extra = int(sys.argv[1]) if len(sys.argv) > 1 else 80
    df_extra = gerar(n=n_extra)
    comparacao = comparar_com_aumento(df_base, df_extra)

    destino = models_dir("sinais_vitais") / "comparacao_preeclampsia.json"
    salvar_metricas(destino, comparacao)
    LOG.info(
        "Comparação salva em %s | F1 base=%.3f -> aumentado=%.3f (delta=%+.3f)",
        destino,
        comparacao["base"]["f1_macro"],
        comparacao["aumentado"]["f1_macro"],
        comparacao["delta"]["f1_macro"],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
