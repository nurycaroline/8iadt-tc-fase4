"""Gera o exemplo de relatório automático para o relatório técnico (Fase 4, Tarefa 4.2).

Reaproveita o **mesmo motor** da Fase 3 (``app.fusao.avaliar_fusao`` +
``app.relatorio.gerar_markdown``) para produzir, a partir do caso sintético
``data/casos/caso_alto.json``, um relatório clínico estruturado em Markdown/HTML —
**gerado por código, não escrito à mão** (DD-F4-4).

As evidências usadas são as do **cenário de referência ALTO** (cicatriz com pesos
treinados), o mesmo demonstrado por ``scripts/e2e_demo._showcase_alto``. Neste ambiente
sem os pesos do YOLO/ASR a fusão sobre o caso degrada para ``MEDIO`` (ver
``docs/relatorio/e2e-log.txt``); aqui exibimos o relatório do caso corroborado ponta a
ponta, como ocorre com os modelos treinados (degradação documentada — DD-F4-6).

Uso (a partir da raiz do repositório)::

    python -m scripts.gerar_evidencias
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ai-service"))

from app.fusao import avaliar_fusao  # noqa: E402
from app.relatorio import (  # noqa: E402
    _artefatos_da_requisicao,
    _markdown_para_html,
    gerar_markdown,
)

# Timestamp fixo para um artefato versionado determinístico (re-rodar não gera diff espúrio).
TIMESTAMP_REFERENCIA = "2026-06-10T21:15:00Z"

# Evidências do cenário de referência ALTO (cicatriz com pesos treinados) para o caso_alto.
# Mesmo conjunto corroborado de scripts/e2e_demo._showcase_alto (contrato §3).
EVIDENCIAS_REFERENCIA = {
    "video_cicatriz": {"evento": "sinal_infeccao", "confianca": 0.88},
    "sinais_vitais": {"tipo": "hipertensao", "valor": "150/95"},
    "texto": {"achado": "sinal_infeccao", "trecho": "Queixa de febre (38,5°C) e dor na cicatriz"},
}


def gerar_exemplo_relatorio() -> tuple[str, str]:
    """Devolve ``(markdown, html)`` do relatório automático do caso de referência."""
    caso = json.loads((RAIZ / "data" / "casos" / "caso_alto.json").read_text(encoding="utf-8"))
    fusao = avaliar_fusao(EVIDENCIAS_REFERENCIA)
    md = gerar_markdown(
        case_id=caso["case_id"],
        paciente=caso["paciente"],
        fusao=fusao,
        evidencias=EVIDENCIAS_REFERENCIA,
        artefatos=_artefatos_da_requisicao(caso),
        timestamp=TIMESTAMP_REFERENCIA,
    )
    return md, _markdown_para_html(md)


def main() -> int:
    md, html = gerar_exemplo_relatorio()
    destino = RAIZ / "docs" / "relatorio"
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "exemplo-relatorio-automatico.md").write_text(md, encoding="utf-8")
    (destino / "exemplo-relatorio-automatico.html").write_text(html, encoding="utf-8")
    print(f"Exemplo de relatório automático gerado em {destino} (.md e .html)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
