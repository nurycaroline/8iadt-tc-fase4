"""Orquestrador da Fase 1 — baixa/gera todo o mini-dataset de uma vez.

Uso:
    python -m scripts.data_prep

Executa cada modalidade de forma independente (best-effort) e imprime um resumo. Passos
*essenciais* são auto-baixáveis/geráveis; *opcionais* (áudio) dependem de obtenção manual
(TTS/gravações próprias ou datasets com formulário) — ver data/README.md.
"""

from __future__ import annotations

import sys

from . import (
    audio_transcrever,
    caso_sintetico,
    cicatriz_yolo,
    sinais_vitais,
    texto_clinico,
)
from .common import get_logger

LOG = get_logger("orquestrador")

# (nome, função, essencial?) — essenciais entram no código de saída.
PASSOS = [
    ("texto_clinico", texto_clinico.main, True),
    ("sinais_vitais", sinais_vitais.main, True),
    ("cicatriz_yolo", cicatriz_yolo.main, True),
    ("audio", audio_transcrever.main, False),
    ("caso_sintetico", caso_sintetico.main, True),
]


def main() -> int:
    resultados: list[tuple[str, int, bool]] = []
    for nome, fn, essencial in PASSOS:
        LOG.info("== %s ==", nome)
        try:
            rc = fn()
        except Exception as exc:  # noqa: BLE001 - best-effort por passo
            LOG.error("Passo %s falhou: %s", nome, exc)
            rc = 1
        resultados.append((nome, rc, essencial))

    print("\n===== RESUMO DA FASE 1 =====")
    for nome, rc, essencial in resultados:
        tag = "essencial" if essencial else "opcional"
        status = "OK" if rc == 0 else "FALHOU"
        print(f"  [{status:6}] {nome:16} ({tag})")

    falhas_essenciais = [n for n, rc, e in resultados if e and rc != 0]
    if falhas_essenciais:
        print(f"\nPassos essenciais com falha: {', '.join(falhas_essenciais)}")
        print("Veja data/README.md para obtenção manual quando o download exigir rede/licença.")
        return 1
    print("\nMini-dataset essencial pronto. Áudio pode exigir passos manuais.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
