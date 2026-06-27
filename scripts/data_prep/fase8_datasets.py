"""Pipeline de dados da **Fase 8** — baixa, traduz (EN→PT) e prepara os 3 datasets adotados.

Datasets (Hugging Face; **licença não especificada** — registrar como risco; versionar só
métricas/amostras, **nunca** os dados):

- Depressão (texto): ``ShreyaR/DepressionDetection`` (`clean_text` + `is_depression`).
- Violência (texto): ``Spiderman01/Domestic_violence_info_support_fromposts`` (só positivos).
- Violência (acústico): ``Hemg/audio-based-violence-dataset`` (`audio` + `label`).

Saídas (em ``data/`` — **ignorado pelo Git**, conforme política do repo):

- ``data/texto_clinico/fase8/depressao_pt.csv`` — ``texto,label`` (1 = depressão).
- ``data/texto_clinico/fase8/violencia_pt.csv`` — ``texto,label`` (1 = violência); **negativos**
  vêm de amostras neutras (``is_depression=0``) do ShreyaR traduzidas + textos clínicos neutros.
- ``data/audio/fase8/violencia/manifest.csv`` — ``caminho,label`` (1 = violência) + áudios.
- ``data/<...>/fase8/relatorio.json`` — contagens/idioma/licença (amostra para o relatório).

**Idempotente** e **offline após o download**: já existindo as saídas, não rebaixa nada. Se a rede
do HF não estiver disponível, o passo correspondente **avisa e segue** (não trava a tarefa).

Uso::

    python -m scripts.data_prep.fase8_datasets --limite 400        # texto (dep.) + violência
    python -m scripts.data_prep.fase8_datasets --apenas audio      # só o acústico
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from .common import data_dir, get_logger, write_csv, write_json

LOG = get_logger("fase8_datasets")

DS_DEPRESSAO = "ShreyaR/DepressionDetection"
DS_VIOLENCIA_TEXTO = "Spiderman01/Domestic_violence_info_support_fromposts"
DS_VIOLENCIA_AUDIO = "Hemg/audio-based-violence-dataset"


def _fase8_dir(modalidade: str) -> Path:
    pasta = data_dir(modalidade) / "fase8"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def normalizar_rotulo_violencia(label: Any) -> int:
    """Normaliza o rótulo do dataset acústico (`violence`/`Nonvoilence` *sic*) para 1/0."""
    txt = str(label).strip().lower()
    if txt in ("1", "violence", "violencia", "violent"):
        return 1
    if txt in ("0", "nonvoilence", "nonviolence", "non-violence", "neutro", "neutral"):
        return 0
    # Heurística final: qualquer coisa que comece com "non" é negativo.
    return 0 if txt.startswith("non") else 1


def textos_clinicos_neutros() -> list[str]:
    """Coleta textos clínicos **neutros** existentes (negativos de violência de domínio próximo)."""
    pasta = data_dir("texto_clinico")
    rotulos = pasta / "rotulos.json"
    if not rotulos.exists():
        return []
    import json

    registros = json.loads(rotulos.read_text(encoding="utf-8"))
    neutros = []
    for reg in registros:
        if reg.get("achado") == "neutro":
            arq = pasta / reg["arquivo"]
            if arq.exists():
                neutros.append(arq.read_text(encoding="utf-8").strip())
    return neutros


def _carregar_hf(nome: str, split: str = "train"):
    """Carrega um dataset do HF (lazy import); devolve ``None`` (com aviso) se indisponível."""
    try:
        from datasets import load_dataset

        return load_dataset(nome, split=split)
    except Exception as exc:
        LOG.warning(
            "Download de %r indisponível (%s). Baixe manualmente (ver docs/datasets.md) e rode "
            "de novo — a tarefa não trava por isso.",
            nome,
            exc,
        )
        return None


def _coluna(ds, *candidatas: str) -> str | None:
    cols = set(getattr(ds, "column_names", []) or [])
    for c in candidatas:
        if c in cols:
            return c
    return None


def preparar_depressao(limite: int) -> dict[str, Any] | None:
    """Baixa ShreyaR, amostra `limite` linhas balanceadas, traduz EN→PT e salva o CSV."""
    saida = _fase8_dir("texto_clinico") / "depressao_pt.csv"
    if saida.exists():
        LOG.info("depressao_pt.csv já existe (%s); pulando.", saida)
        return {"arquivo": str(saida), "status": "existente"}

    ds = _carregar_hf(DS_DEPRESSAO)
    if ds is None:
        return None
    col_texto = _coluna(ds, "clean_text", "text", "Text")
    col_label = _coluna(ds, "is_depression", "label", "Label")
    if not (col_texto and col_label):
        LOG.warning("Colunas de texto/rótulo não encontradas em %s.", DS_DEPRESSAO)
        return None

    linhas = _amostrar_balanceado(ds, col_texto, col_label, limite)
    from .traducao import traduzir_lote

    LOG.info("Traduzindo %d textos de depressão EN→PT...", len(linhas))
    textos_pt = traduzir_lote([t for t, _ in linhas])
    _salvar_csv_texto(saida, textos_pt, [int(bool(rotulo)) for _, rotulo in linhas])
    return {"arquivo": str(saida), "n": len(linhas), "idioma": "pt", "fonte": DS_DEPRESSAO}


def preparar_violencia_texto(limite: int) -> dict[str, Any] | None:
    """Baixa Spiderman01 (positivos), gera **negativos** e salva o CSV de violência (texto)."""
    saida = _fase8_dir("texto_clinico") / "violencia_pt.csv"
    if saida.exists():
        LOG.info("violencia_pt.csv já existe (%s); pulando.", saida)
        return {"arquivo": str(saida), "status": "existente"}

    ds = _carregar_hf(DS_VIOLENCIA_TEXTO)
    if ds is None:
        return None
    col_texto = _coluna(ds, "text", "post", "content", "Text", "body")
    if not col_texto:
        LOG.warning("Coluna de texto não encontrada em %s.", DS_VIOLENCIA_TEXTO)
        return None

    positivos_en = [str(r[col_texto]) for r in ds if r.get(col_texto)][:limite]
    from .traducao import traduzir_lote

    LOG.info("Traduzindo %d posts de violência EN→PT...", len(positivos_en))
    positivos_pt = traduzir_lote(positivos_en)

    negativos = _negativos_violencia(len(positivos_pt))
    textos = positivos_pt + negativos
    labels = [1] * len(positivos_pt) + [0] * len(negativos)
    _salvar_csv_texto(saida, textos, labels)
    return {
        "arquivo": str(saida),
        "positivos": len(positivos_pt),
        "negativos": len(negativos),
        "idioma": "pt",
        "fonte": DS_VIOLENCIA_TEXTO,
    }


def preparar_violencia_audio(limite: int) -> dict[str, Any] | None:
    """Baixa Hemg, salva os áudios e um ``manifest.csv`` (caminho,label) para o treino acústico."""
    pasta = _fase8_dir("audio") / "violencia"
    pasta.mkdir(parents=True, exist_ok=True)
    manifest = pasta / "manifest.csv"
    if manifest.exists():
        LOG.info("manifest.csv já existe (%s); pulando.", manifest)
        return {"arquivo": str(manifest), "status": "existente"}

    ds = _carregar_hf(DS_VIOLENCIA_AUDIO)
    if ds is None:
        return None
    col_audio = _coluna(ds, "audio", "file", "path")
    col_label = _coluna(ds, "label", "Label", "class")
    if not (col_audio and col_label):
        LOG.warning("Colunas de áudio/rótulo não encontradas em %s.", DS_VIOLENCIA_AUDIO)
        return None

    import soundfile as sf

    registros: list[dict[str, Any]] = []
    for i, reg in enumerate(ds):
        if i >= limite:
            break
        label = normalizar_rotulo_violencia(reg[col_label])
        nome = f"audio_{i:04d}.wav"
        destino = pasta / nome
        try:
            audio = reg[col_audio]
            if isinstance(audio, dict) and "array" in audio:
                sf.write(destino, audio["array"], int(audio.get("sampling_rate", 16000)))
            elif isinstance(audio, dict) and audio.get("path"):
                import shutil

                shutil.copyfile(audio["path"], destino)
            else:
                continue
        except Exception as exc:
            LOG.warning("Falha ao salvar áudio %d (%s); pulando.", i, exc)
            continue
        registros.append({"caminho": nome, "label": label})

    if not registros:
        LOG.warning("Nenhum áudio salvo de %s.", DS_VIOLENCIA_AUDIO)
        return None
    _salvar_manifest(manifest, registros)
    return {"arquivo": str(manifest), "n": len(registros), "fonte": DS_VIOLENCIA_AUDIO}


def _amostrar_balanceado(ds, col_texto: str, col_label: str, limite: int) -> list[tuple[str, int]]:
    """Amostra até `limite` linhas balanceadas entre as classes 0/1."""
    pos, neg = [], []
    metade = max(1, limite // 2)
    for r in ds:
        texto, label = r.get(col_texto), r.get(col_label)
        if not texto:
            continue
        alvo = pos if int(bool(label)) == 1 else neg
        if len(alvo) < metade:
            alvo.append((str(texto), int(bool(label))))
        if len(pos) >= metade and len(neg) >= metade:
            break
    return pos + neg


def _negativos_violencia(qtd: int) -> list[str]:
    """Gera negativos de violência: ShreyaR neutro (PT) + textos clínicos neutros existentes."""
    negativos = list(textos_clinicos_neutros())
    faltam = max(0, qtd - len(negativos))
    if faltam:
        ds = _carregar_hf(DS_DEPRESSAO)
        if ds is not None:
            col_texto = _coluna(ds, "clean_text", "text", "Text")
            col_label = _coluna(ds, "is_depression", "label", "Label")
            neutros_en = [
                str(r[col_texto])
                for r in ds
                if col_texto and col_label and r.get(col_texto) and int(bool(r[col_label])) == 0
            ][:faltam]
            if neutros_en:
                from .traducao import traduzir_lote

                LOG.info("Traduzindo %d negativos (neutros) EN→PT...", len(neutros_en))
                negativos += traduzir_lote(neutros_en)
    return negativos[: qtd] if qtd else negativos


def _salvar_csv_texto(caminho: Path, textos: list[str], labels: list[int]) -> None:
    import pandas as pd

    df = pd.DataFrame({"texto": textos, "label": labels})
    write_csv(df, caminho)
    LOG.info("Salvo %s (%d linhas).", caminho, len(df))


def _salvar_manifest(caminho: Path, registros: list[dict[str, Any]]) -> None:
    import pandas as pd

    write_csv(pd.DataFrame(registros), caminho)
    LOG.info("Salvo %s (%d áudios).", caminho, len(registros))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pipeline de dados da Fase 8 (download+tradução).")
    parser.add_argument("--limite", type=int, default=400, help="máx. de amostras por dataset")
    parser.add_argument(
        "--apenas",
        choices=("depressao", "violencia_texto", "audio", "tudo"),
        default="tudo",
    )
    args = parser.parse_args(argv)

    relatorio: dict[str, Any] = {}
    if args.apenas in ("depressao", "tudo"):
        relatorio["depressao_texto"] = preparar_depressao(args.limite)
    if args.apenas in ("violencia_texto", "tudo"):
        relatorio["violencia_texto"] = preparar_violencia_texto(args.limite)
    if args.apenas in ("audio", "tudo"):
        relatorio["violencia_audio"] = preparar_violencia_audio(args.limite)

    write_json(_fase8_dir("texto_clinico") / "relatorio.json", relatorio)
    feitos = [k for k, v in relatorio.items() if v]
    LOG.info("Fase 8 — datasets preparados: %s", ", ".join(feitos) or "nenhum (ver avisos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
