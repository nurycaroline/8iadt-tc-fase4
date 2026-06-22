"""App FastAPI do serviço de IA (Tarefa 3.2).

Expõe ``POST /inferencia`` (wrapper fino sobre :func:`app.pipeline.processar`) e ``GET /health``.
A validação do corpo é declarativa (Pydantic v2 → ``422`` automático). Falha de uma modalidade é
tratada dentro do pipeline (evidência omitida), portanto **não** vira ``500``.

Servir localmente::

    uvicorn app.api.main:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

from fastapi import FastAPI

from app.api.modelos import RequisicaoInferencia, RespostaRisco
from app.common import get_logger
from app.pipeline import processar

LOG = get_logger("api")

app = FastAPI(
    title="Serviço de IA — Saúde da Mulher (Fase 3)",
    description="Fusão multimodal: recebe o caso (contrato §1) e devolve o JSON de risco (§2).",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    """Readiness probe simples."""
    return {"status": "ok"}


@app.post("/inferencia", response_model=RespostaRisco)
def inferencia(requisicao: RequisicaoInferencia) -> dict:
    """Roda o pipeline multimodal e devolve o JSON de risco padronizado."""
    payload = requisicao.model_dump(exclude_none=True)
    LOG.info("Recebida inferência para case_id=%s", payload.get("case_id"))
    return processar(payload)
