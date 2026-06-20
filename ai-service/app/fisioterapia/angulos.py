"""Geometria de movimento a partir de keypoints (funções puras, testáveis).

Calcula ângulos articulares, amplitude de movimento (ROM) ao longo de uma série e classifica a
execução do exercício como ``correta``/``incorreta``. Sem dependência de IA/vídeo.
"""

from __future__ import annotations

from collections.abc import Sequence

# Amplitude mínima (graus) para considerar a execução correta (ajustável por exercício).
AMPLITUDE_MINIMA = 30.0

Ponto = Sequence[float]


def angulo(a: Ponto, b: Ponto, c: Ponto) -> float:
    """Ângulo (graus) no vértice ``b`` formado pelos segmentos ``b->a`` e ``b->c``."""
    import numpy as np

    a_, b_, c_ = (np.asarray(p, dtype=float) for p in (a, b, c))
    ba = a_ - b_
    bc = c_ - b_
    norma = np.linalg.norm(ba) * np.linalg.norm(bc)
    if norma == 0:
        return 0.0
    cos = float(np.clip(np.dot(ba, bc) / norma, -1.0, 1.0))
    return float(np.degrees(np.arccos(cos)))


def amplitude(serie_angulos: Sequence[float]) -> float:
    """Amplitude de movimento (ROM): diferença entre o maior e o menor ângulo da série."""
    valores = [float(x) for x in serie_angulos]
    if not valores:
        return 0.0
    return max(valores) - min(valores)


def classificar_execucao(amplitude_valor: float, minimo: float = AMPLITUDE_MINIMA) -> str:
    """Classifica a execução: ``correta`` se a amplitude atinge o mínimo, senão ``incorreta``."""
    return "correta" if float(amplitude_valor) >= float(minimo) else "incorreta"


def rotular_amplitude(amplitude_valor: float, minimo: float = AMPLITUDE_MINIMA) -> str:
    """Rótulo textual da amplitude para a evidência (``adequada``/``reduzida``)."""
    return "adequada" if float(amplitude_valor) >= float(minimo) else "reduzida"
