"""Modelos Pydantic v2 do contrato de API (docs/contrato-api.md §1 e §2).

Validam o payload de entrada (``RequisicaoInferencia``) e tipam a resposta (``RespostaRisco``). Os
domínios das evidências são garantidos pelos construtores de :mod:`app.schemas` no pipeline; aqui
validamos o cabeçalho da requisição e o nível de risco da resposta.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class Paciente(BaseModel):
    """Contexto mínimo da paciente (pseudonimizado) — alimenta o cabeçalho do relatório."""

    id: str
    primeiro_nome: str | None = None
    idade: int | None = Field(default=None, ge=0, le=120)
    gestante: bool = False
    idade_gestacional_semanas: int | None = Field(default=None, ge=0, le=45)


class DadosVitais(BaseModel):
    csv_url: str


class RequisicaoInferencia(BaseModel):
    """Objeto de requisição Node → Python (contrato §1). Modalidades são opcionais."""

    case_id: str
    paciente: Paciente
    video_cicatriz_url: str | None = None
    dados_vitais: DadosVitais | None = None
    audio_url: str | None = None
    texto_clinico: str | None = None


class RespostaRisco(BaseModel):
    """JSON de risco padronizado Python → Node (contrato §2)."""

    timestamp: str
    case_id: str
    risco_detectado: Literal["BAIXO", "MEDIO", "ALTO"]
    evidencias: dict[str, Any] = Field(default_factory=dict)
    mensagem_alerta: str
    relatorio_url: str | None = None
