"""Inferência da cicatriz → evidência padronizada (contrato §3).

Roda o detector YOLOv8 numa imagem, pega a melhor detecção e **mapeia** a classe do dataset
(``ferida_ok``/``ferida_alerta``) para o ``evento`` do contrato (``ferida_ok``/``sinal_infeccao``/
``nenhum``), aplicando o limiar de confiança. O mapeamento (:func:`mapear_evento`) é puro/testável.
"""

from __future__ import annotations

from app.common import get_logger, models_dir
from app.limiares import CONFIANCA_MINIMA
from app.schemas import evidencia_cicatriz

LOG = get_logger("cicatriz")

# Classe do dataset (Fase 1) -> evento do contrato.
_MAPA_CLASSE = {
    "ferida_ok": "ferida_ok",
    "ferida_alerta": "sinal_infeccao",
}


def mapear_evento(classe: str | None, confianca: float) -> str:
    """Mapeia a classe detectada + confiança para o ``evento`` do contrato (função pura).

    - ``ferida_alerta`` com confiança >= limiar -> ``sinal_infeccao``;
    - ``ferida_ok`` -> ``ferida_ok``;
    - sem detecção ou abaixo do limiar (para alerta) -> ``nenhum``.
    """
    if classe is None:
        return "nenhum"
    evento = _MAPA_CLASSE.get(str(classe).strip().lower(), "nenhum")
    if evento == "sinal_infeccao" and float(confianca) < CONFIANCA_MINIMA:
        return "nenhum"
    return evento


def detectar(imagem, modelo_path=None) -> dict:
    """Detecta sinal de infecção numa imagem de cicatriz → ``{evento, confianca}``."""
    from pathlib import Path

    if modelo_path is None:
        modelo_path = models_dir("cicatriz") / "best.pt"
    modelo_path = Path(modelo_path)
    if not modelo_path.exists():
        LOG.warning("Modelo de cicatriz ausente em %s; evento=nenhum.", modelo_path)
        return evidencia_cicatriz("nenhum", 0.0)

    from ultralytics import YOLO

    resultados = YOLO(str(modelo_path)).predict(imagem, verbose=False)
    melhor_classe, melhor_conf = None, 0.0
    for r in resultados:
        nomes = r.names
        for box in r.boxes:
            conf = float(box.conf[0])
            if conf >= melhor_conf:
                melhor_conf = conf
                melhor_classe = nomes.get(int(box.cls[0]), None)

    evento = mapear_evento(melhor_classe, melhor_conf)
    return evidencia_cicatriz(evento, melhor_conf if evento != "nenhum" else 0.0)
