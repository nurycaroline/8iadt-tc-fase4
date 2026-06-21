"""Inferência de sinais vitais → dicionário de evidência padronizado (contrato §3).

Carrega o modelo treinado (Random Forest), prediz a classe de risco e **deriva o ``tipo``** do
contrato a partir da classe + limiares de PA. A derivação (:func:`derivar_tipo`) é pura e testável.
"""

from __future__ import annotations

from app import limiares
from app.common import get_logger, models_dir
from app.schemas import evidencia_sinais_vitais

LOG = get_logger("sinais_vitais")


def derivar_tipo(
    classe: str | None, sistolica: float | None, diastolica: float | None
) -> str:
    """Mapeia (classe do modelo + PA) para o ``tipo`` do contrato.

    - PA em alerta (>= 140/90) -> ``hipertensao`` (pré-eclâmpsia exige contexto extra na fusão);
    - classe ``high``/``mid`` sem PA em alerta -> ``risco_medio``;
    - classe ``low`` sem alerta -> ``normal``.
    """
    if limiares.pa_em_alerta(sistolica, diastolica):
        return "hipertensao"
    chave = (str(classe).strip().lower() if classe is not None else "")
    if chave in ("high", "mid"):
        return "risco_medio"
    if chave == "low":
        return "normal"
    return "normal"


def _formatar_valor(sistolica, diastolica) -> str:
    if sistolica is not None and diastolica is not None:
        return f"{int(round(float(sistolica)))}/{int(round(float(diastolica)))}"
    return "n/d"


def _carregar_modelo(modelo_path=None):
    import joblib

    if modelo_path is None:
        modelo_path = models_dir("sinais_vitais") / "modelo.joblib"
    if not modelo_path.exists():
        return None
    return joblib.load(modelo_path)


def prever(registro: dict, modelo_path=None) -> dict:
    """Prediz a evidência de sinais vitais a partir de um registro de features.

    ``registro`` deve conter ``SystolicBP``/``DiastolicBP`` (e demais features se o modelo existir).
    Sem modelo treinado, deriva o ``tipo`` apenas pelos limiares de PA (degrada sem quebrar — DD10).
    """
    sis = registro.get("SystolicBP")
    dia = registro.get("DiastolicBP")

    bundle = _carregar_modelo(modelo_path)
    classe = None
    if bundle is not None:
        import pandas as pd

        features = bundle["features"]
        X = pd.DataFrame([{c: registro.get(c) for c in features}])
        classe = str(bundle["modelo"].predict(X)[0])
    else:
        LOG.warning("Modelo de sinais vitais ausente; derivando tipo só pela PA.")

    tipo = derivar_tipo(classe, sis, dia)
    return evidencia_sinais_vitais(tipo, _formatar_valor(sis, dia))


if __name__ == "__main__":
    exemplo = {
        "Age": 35, "SystolicBP": 150, "DiastolicBP": 95,
        "BS": 7, "BodyTemp": 98, "HeartRate": 80,
    }
    print(prever(exemplo))
