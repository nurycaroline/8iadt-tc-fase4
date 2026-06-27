"""Baseline por modalidade única — Tarefa 2.6.

Mede a performance de **cada modalidade isolada** detectando o evento de risco (binário:
risco vs. não-risco) sobre o mini-dataset da Fase 1. Serve de comparação para provar, na Fase 3,
que a fusão reduz falsos positivos / melhora a detecção (Tarefa 3.1b).

Salva ``ai-service/models/baseline.json``. Modalidades sem dados/modelo são omitidas (DD10).

Uso (a partir de ai-service/):
    python -m app.baseline
"""

from __future__ import annotations

import json
import sys

from app.common import data_dir, get_logger, models_dir, salvar_metricas

LOG = get_logger("baseline")


def metricas_modalidade(y_true, y_pred) -> dict:
    """Precisão, recall e taxa de falsos positivos para detecção binária de risco (função pura).

    ``y_true``/``y_pred`` são sequências booleanas (``True`` = risco detectado).
    """
    yt = [bool(x) for x in y_true]
    yp = [bool(x) for x in y_pred]
    if len(yt) != len(yp):
        raise ValueError("y_true e y_pred têm tamanhos diferentes.")

    tp = sum(t and p for t, p in zip(yt, yp, strict=True))
    fp = sum((not t) and p for t, p in zip(yt, yp, strict=True))
    fn = sum(t and (not p) for t, p in zip(yt, yp, strict=True))
    tn = sum((not t) and (not p) for t, p in zip(yt, yp, strict=True))

    precisao = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    fp_rate = fp / (fp + tn) if (fp + tn) else 0.0
    return {
        "n": len(yt),
        "precisao": round(precisao, 4),
        "recall": round(recall, 4),
        "taxa_falsos_positivos": round(fp_rate, 4),
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
    }


def _baseline_texto() -> dict | None:
    from app.texto.nlp import analisar

    pasta = data_dir("texto_clinico")
    rotulos = pasta / "rotulos.json"
    if not rotulos.exists():
        return None
    registros = json.loads(rotulos.read_text(encoding="utf-8"))
    y_true, y_pred = [], []
    for reg in registros:
        arq = pasta / reg["arquivo"]
        if not arq.exists():
            continue
        evid = analisar(arq.read_text(encoding="utf-8"))
        # Fase 8: risco no texto = achado clínico OU depressão/violência (ML/keywords).
        risco_pred = (
            evid["achado"] != "neutro"
            or evid["depressao"]["rotulo"] != "neutro"
            or evid["violencia"]["rotulo"] != "neutro"
        )
        y_true.append(reg["achado"] != "neutro")
        y_pred.append(risco_pred)
    return metricas_modalidade(y_true, y_pred) if y_true else None


def _baseline_audio() -> dict | None:
    from app.audio.classificacao import classificar

    meta = data_dir("audio") / "metadados.json"
    if not meta.exists():
        return None
    registros = json.loads(meta.read_text(encoding="utf-8"))
    y_true, y_pred = [], []
    for reg in registros:
        categoria = reg.get("categoria", "neutro")
        y_true.append(categoria not in ("neutro", "nao_rotulado"))
        y_pred.append(classificar(reg.get("transcricao", ""))["categoria"] != "neutro")
    return metricas_modalidade(y_true, y_pred) if y_true else None


def _baseline_sinais_vitais() -> dict | None:
    import joblib
    import pandas as pd

    from app.limiares import pa_em_alerta

    csv = data_dir("sinais_vitais") / "maternal_clean.csv"
    modelo_path = models_dir("sinais_vitais") / "modelo.joblib"
    if not (csv.exists() and modelo_path.exists()):
        return None
    df = pd.read_csv(csv)
    bundle = joblib.load(modelo_path)
    features = bundle["features"]
    preds = bundle["modelo"].predict(df[features])
    y_true = [str(r) == "high" for r in df["RiskLevel"]]
    y_pred = [
        str(p) == "high" or pa_em_alerta(s, d)
        for p, s, d in zip(preds, df["SystolicBP"], df["DiastolicBP"], strict=True)
    ]
    return metricas_modalidade(y_true, y_pred)


def gerar_baseline() -> dict:
    """Roda o baseline de cada modalidade disponível e devolve o dicionário consolidado."""
    modalidades = {
        "texto": _baseline_texto,
        "audio": _baseline_audio,
        "sinais_vitais": _baseline_sinais_vitais,
    }
    baseline = {}
    for nome, fn in modalidades.items():
        try:
            resultado = fn()
        except Exception as exc:  # pragma: no cover - robustez de dados/ambiente
            LOG.warning("Baseline de %s falhou (%s); omitido.", nome, exc)
            resultado = None
        if resultado is None:
            LOG.info("Baseline de %s omitido (sem dados/modelo).", nome)
            continue
        baseline[nome] = resultado
    return baseline


def main() -> int:
    baseline = gerar_baseline()
    if not baseline:
        LOG.error("Nenhuma modalidade disponível para baseline. Rode a Fase 1 e os treinos.")
        return 1
    saida = salvar_metricas(models_dir() / "baseline.json", baseline)
    LOG.info("Baseline salvo em %s (%d modalidade(s)).", saida, len(baseline))
    return 0


if __name__ == "__main__":
    sys.exit(main())
