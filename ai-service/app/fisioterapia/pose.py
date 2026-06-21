"""Estimativa de keypoints com YOLOv8-pose (camada de IA, importação preguiçosa).

Extrai keypoints de imagens/frames. Quando o IntelliRehabDS já fornece esqueletos/keypoints
(metadados da Fase 1), prefira reaproveitá-los em vez de re-estimar (política do projeto).
"""

from __future__ import annotations

from app.common import get_logger

LOG = get_logger("fisioterapia")

MODELO_POSE = "yolov8n-pose.pt"


def estimar_keypoints(fonte, modelo: str = MODELO_POSE):
    """Roda o YOLOv8-pose sobre ``fonte`` (imagem/frame/vídeo) e devolve os keypoints (xy).

    Retorna uma lista de arrays (um por frame). Requer ``ultralytics`` instalado.
    """
    from ultralytics import YOLO

    modelo_pose = YOLO(modelo)
    resultados = modelo_pose.predict(fonte, verbose=False)
    keypoints = []
    for r in resultados:
        if r.keypoints is not None and len(r.keypoints) > 0:
            keypoints.append(r.keypoints.xy[0].cpu().numpy())
    return keypoints
