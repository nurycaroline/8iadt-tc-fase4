"""Pipeline de dados da **Fase 8** — baixa, traduz (EN→PT) e prepara os 3 datasets adotados.

Datasets (Hugging Face; **licença não especificada** — registrar como risco; versionar só
métricas/amostras, **nunca** os dados):

- Depressão (texto): ``ShreyaR/DepressionDetection`` (`clean_text` + `is_depression`).
- Violência (texto): ``Spiderman01/Domestic_violence_info_support_fromposts`` (só positivos).
- Violência (acústico): ``Hemg/audio-based-violence-dataset`` (`audio` + `label`).

Saídas (em ``data/`` — **ignorado pelo Git**, conforme política do repo):

- ``data/texto_clinico/fase8/depressao_pt.csv`` — ``texto,label`` (1 = depressão).
- ``data/texto_clinico/fase8/violencia_pt.csv`` — ``texto,label`` (1 = violência); **negativos**
  do **mesmo domínio** (posts do ShreyaR, misturando neutros e de depressão) traduzidos +
  textos clínicos neutros como complemento — reduz o vazamento de fonte/domínio.
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

    import io

    import soundfile as sf

    # Evita a decodificação automática do `datasets` (que exige `torchcodec`/ffmpeg):
    # lemos os bytes crus e decodificamos com `soundfile`, alinhado à política sem ffmpeg.
    try:
        from datasets import Audio

        ds = ds.cast_column(col_audio, Audio(decode=False))
    except Exception as exc:  # versão antiga do datasets ou coluna não-áudio
        LOG.warning("Não foi possível desabilitar a decodificação de áudio (%s).", exc)

    # O dataset Hemg vem ordenado por classe (todos os negativos primeiro), então pegar as
    # primeiras `limite` linhas geraria um manifest de uma única classe. Amostramos de forma
    # balanceada (até `limite//2` por classe), espelhando o pipeline de texto.
    metade = max(1, limite // 2)
    salvos = {0: 0, 1: 0}
    registros: list[dict[str, Any]] = []
    for i, reg in enumerate(ds):
        if salvos[0] >= metade and salvos[1] >= metade:
            break
        label = normalizar_rotulo_violencia(reg[col_label])
        if salvos[label] >= metade:
            continue
        nome = f"audio_{i:04d}.wav"
        destino = pasta / nome
        try:
            audio = reg[col_audio]
            if isinstance(audio, dict) and audio.get("bytes"):
                arr, sr = sf.read(io.BytesIO(audio["bytes"]))
                sf.write(destino, arr, sr)
            elif isinstance(audio, dict) and "array" in audio:
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
        salvos[label] += 1

    if not registros:
        LOG.warning("Nenhum áudio salvo de %s.", DS_VIOLENCIA_AUDIO)
        return None
    if salvos[0] == 0 or salvos[1] == 0:
        LOG.warning(
            "Manifest de áudio ficou com uma única classe (neg=%d, pos=%d). "
            "Verifique os rótulos em %s.",
            salvos[0],
            salvos[1],
            DS_VIOLENCIA_AUDIO,
        )
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
    """Gera negativos de violência do **mesmo domínio** dos positivos (posts de rede social).

    Evita o **vazamento de fonte/domínio** (positivos de um corpus, negativos de outro, o que torna
    as classes trivialmente separáveis): os negativos vêm majoritariamente do dataset de depressão
    (``ShreyaR``, mesma origem de posts), **misturando** textos **neutros** e de **depressão**.
    Assim o classificador separa *violência* de *sofrimento psíquico*, não só "agitado" de "calmo".
    Os textos clínicos neutros entram só como **complemento/fallback** (domínio diferente; cobre o
    caso sem rede do HF).

    Observação honesta: como o dataset de violência (``Spiderman01``) só traz **positivos**, ainda
    resta resíduo de viés de fonte; mitiga-se aqui com negativos do domínio mais próximo + a
    regularização do pipeline (ver ``app.texto.treino.construir_pipeline``).
    """
    sociais_en: list[str] = []
    ds = _carregar_hf(DS_DEPRESSAO)
    if ds is not None:
        col_texto = _coluna(ds, "clean_text", "text", "Text")
        col_label = _coluna(ds, "is_depression", "label", "Label")
        if col_texto:
            neutros, deprimidos = [], []
            for r in ds:
                texto = r.get(col_texto)
                if not texto:
                    continue
                rotulo = int(bool(r[col_label])) if col_label else 0
                (deprimidos if rotulo == 1 else neutros).append(str(texto))
            # Mistura equilibrada: ~metade neutros + ~metade "deprimidos" (sofrimento != violência).
            metade = max(1, qtd // 2)
            usados_neutros = neutros[:metade]
            sociais_en = usados_neutros + deprimidos[: max(0, qtd - len(usados_neutros))]

    if sociais_en:
        from .traducao import traduzir_lote

        LOG.info("Traduzindo %d negativos de violência (mesmo domínio) EN→PT...", len(sociais_en))
        negativos = traduzir_lote(sociais_en)
    else:
        negativos = []

    # Complemento/fallback de domínio clínico (poucos; cobre o caso sem rede do HF).
    if len(negativos) < qtd:
        negativos += textos_clinicos_neutros()
    return negativos[:qtd] if qtd else negativos


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
