"""Limiares clínicos (gatilhos) — Tarefa 2.7 de docs/02-fase2-modelos.md.

Centraliza os disparadores matemáticos do alerta usados pelos modelos individuais e, na Fase 3,
pelo motor de fusão. Mantê-los num só lugar evita divergência entre modalidades e facilita o ajuste
clínico e a documentação no relatório técnico.

| Sinal                         | Condição de alerta                                  |
|-------------------------------|-----------------------------------------------------|
| PA sistólica / diastólica     | >= 140/90 mmHg (hipertensão / pré-eclâmpsia)        |
| Modelo de sinais vitais       | classe `high` (alto risco)                          |
| Detecção visual na cicatriz   | `ferida_alerta` com confiança >= 0.7                |
| Violência acústica (áudio)    | classificador de violência no som com conf. >= 0.7  |
| Violência/depressão no texto  | classificador ML com confiança >= 0.6               |
| Achado no texto clínico       | termo/categoria de risco identificado               |
"""

from __future__ import annotations

# Pressão arterial (mmHg) — limiar de hipertensão/pré-eclâmpsia.
PA_SISTOLICA_ALERTA = 140
PA_DIASTOLICA_ALERTA = 90

# Confiança mínima para considerar uma detecção/classificação de risco (cicatriz, áudio acústico).
CONFIANCA_MINIMA = 0.7

# Confiança mínima dos classificadores ML de **texto** (depressão/violência) — Fase 8. Mais baixa
# que o limiar acústico/visual: o texto entra como contexto e os datasets são de domínio diferente.
CONFIANCA_TEXTO = 0.6

# Classe do modelo de sinais vitais considerada de alto risco.
CLASSE_RISCO_ALTO = "high"


def pa_em_alerta(sistolica: float | None, diastolica: float | None) -> bool:
    """True se a PA sistólica **ou** diastólica atingir o limiar de alerta."""
    if sistolica is not None and float(sistolica) >= PA_SISTOLICA_ALERTA:
        return True
    if diastolica is not None and float(diastolica) >= PA_DIASTOLICA_ALERTA:
        return True
    return False


def confianca_suficiente(confianca: float) -> bool:
    """True se a confiança atinge o limiar mínimo para contar como sinal de risco."""
    return float(confianca) >= CONFIANCA_MINIMA


def confianca_texto_suficiente(confianca: float) -> bool:
    """True se a confiança do classificador ML de texto atinge o limiar (Fase 8)."""
    return float(confianca) >= CONFIANCA_TEXTO


def risco_alto_sinais_vitais(
    classe: str | None,
    sistolica: float | None = None,
    diastolica: float | None = None,
) -> bool:
    """True se a classe é de alto risco **ou** a PA está em faixa de alerta."""
    if classe is not None and str(classe).strip().lower() == CLASSE_RISCO_ALTO:
        return True
    return pa_em_alerta(sistolica, diastolica)
