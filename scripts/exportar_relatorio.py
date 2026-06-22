"""Exporta o relatório técnico (Markdown) para PDF — com fallback para HTML (Fase 4, Tarefa 4.2).

Reaproveita a mesma abordagem do relatório automático da Fase 3
(``ai-service/app/relatorio.py``): ``markdown`` → HTML → ``weasyprint``. Política de
degradação (DD-F4-2 / F3-DD7): **o HTML é sempre garantido**; o PDF é melhor-esforço e
só é gerado quando ``weasyprint`` (e suas libs de sistema) está disponível. Sem ele, o
processo grava o HTML e instrui como gerar o PDF localmente — sem quebrar.

Uso (a partir da raiz do repositório)::

    python -m scripts.exportar_relatorio                 # docs/relatorio-tecnico.md → .pdf ou .html
    python -m scripts.exportar_relatorio --entrada docs/outro.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ai-service"))

from app.relatorio import _markdown_para_html, _tentar_pdf  # noqa: E402

INSTRUCAO_PDF = (
    "PDF não gerado (weasyprint indisponível). HTML salvo como fallback.\n"
    "Para gerar o PDF localmente, instale as libs e rode novamente:\n"
    "  pip install weasyprint   # requer libs de sistema (pango/cairo)\n"
    "  python -m scripts.exportar_relatorio\n"
    "Alternativa: pandoc docs/relatorio-tecnico.md -o docs/relatorio-tecnico.pdf"
)


def exportar(entrada: Path) -> Path:
    """Converte ``entrada`` (Markdown) em PDF se possível, senão HTML. Devolve o caminho gerado."""
    md = entrada.read_text(encoding="utf-8")
    html = _markdown_para_html(md)
    pdf = _tentar_pdf(html)

    if pdf is not None:
        destino = entrada.with_suffix(".pdf")
        destino.write_bytes(pdf)
        print(f"PDF gerado em {destino}")
    else:
        destino = entrada.with_suffix(".html")
        destino.write_text(html, encoding="utf-8")
        print(f"{INSTRUCAO_PDF}\nHTML gerado em {destino}")
    return destino


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Exporta o relatório técnico (fallback HTML).")
    parser.add_argument(
        "--entrada",
        default="docs/relatorio-tecnico.md",
        help="caminho do Markdown de entrada (padrão: docs/relatorio-tecnico.md)",
    )
    args = parser.parse_args(argv)

    entrada = (RAIZ / args.entrada).resolve()
    if not entrada.exists():
        print(f"Arquivo não encontrado: {entrada}", file=sys.stderr)
        return 1
    exportar(entrada)
    return 0


if __name__ == "__main__":
    sys.exit(main())
