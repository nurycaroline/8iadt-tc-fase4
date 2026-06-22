"""Testes do pipeline de inferência (Tarefa 3.3 / contrato §1 → §2).

As inferências das modalidades (Fase 2) são substituídas por dublês para tornar o pipeline
determinístico e independente de pesos/dados (que não vivem no repositório). Cobre: caso completo,
omissão de modalidade ausente/falha e validade da resposta no contrato §2.
"""

from __future__ import annotations

import json
from pathlib import Path

from app import pipeline
from app.schemas import (
    evidencia_audio,
    evidencia_cicatriz,
    evidencia_sinais_vitais,
    evidencia_texto,
)

CASOS = Path(__file__).resolve().parents[2] / "data" / "casos"

CONTRATO_RESPOSTA = {
    "timestamp",
    "case_id",
    "risco_detectado",
    "evidencias",
    "mensagem_alerta",
    "relatorio_url",
}


def _mockar_modalidades(monkeypatch, *, cicatriz, vitais, audio, texto):
    monkeypatch.setattr(
        pipeline.cicatriz_inf, "detectar", lambda fonte: evidencia_cicatriz(*cicatriz)
    )
    monkeypatch.setattr(pipeline, "_registro_vitais", lambda csv: {"SystolicBP": 150})
    monkeypatch.setattr(
        pipeline.vitais_inf, "prever", lambda registro: evidencia_sinais_vitais(*vitais)
    )
    monkeypatch.setattr(pipeline.audio_inf, "inferir", lambda fonte: evidencia_audio(*audio))
    monkeypatch.setattr(pipeline.texto_inf, "analisar", lambda texto_: evidencia_texto(*texto))


def test_caso_alto_completo(monkeypatch):
    caso = json.loads((CASOS / "caso_alto.json").read_text(encoding="utf-8"))
    _mockar_modalidades(
        monkeypatch,
        cicatriz=("sinal_infeccao", 0.9),
        vitais=("hipertensao", "152/98"),
        audio=("depressao_pos_parto", 0.8),
        texto=("sinal_infeccao", "febre e dor na cicatriz"),
    )
    resposta = pipeline.processar(caso)
    assert resposta["risco_detectado"] == "ALTO"
    assert set(resposta) == CONTRATO_RESPOSTA
    assert {"video_cicatriz", "sinais_vitais", "audio", "texto"} <= set(resposta["evidencias"])


def test_caso_baixo_completo(monkeypatch):
    caso = json.loads((CASOS / "caso_baixo.json").read_text(encoding="utf-8"))
    _mockar_modalidades(
        monkeypatch,
        cicatriz=("ferida_ok", 0.8),
        vitais=("normal", "110/70"),
        audio=("neutro", 0.5),
        texto=("neutro", ""),
    )
    resposta = pipeline.processar(caso)
    assert resposta["risco_detectado"] == "BAIXO"


def test_modalidade_ausente_ou_com_falha_e_omitida(monkeypatch):
    # Cicatriz presente no payload mas a inferência falha → evidência omitida (não derruba o caso).
    def _falha(_fonte):
        raise RuntimeError("pesos ausentes")

    monkeypatch.setattr(pipeline.cicatriz_inf, "detectar", _falha)
    monkeypatch.setattr(pipeline.texto_inf, "analisar", lambda t: evidencia_texto("neutro", ""))

    requisicao = {
        "case_id": "c1",
        "paciente": {"id": "p1"},
        "video_cicatriz_url": "data/inexistente.jpg",
        "texto_clinico": "evolução sem achados",
    }
    resposta = pipeline.processar(requisicao)
    assert "video_cicatriz" not in resposta["evidencias"]
    assert "texto" in resposta["evidencias"]
    assert resposta["risco_detectado"] == "BAIXO"


def test_resposta_valida_no_contrato(monkeypatch):
    # Sem mock: usa o NLP real (determinístico) sobre texto inline.
    requisicao = {
        "case_id": "abc-123",
        "paciente": {"id": "p1"},
        "texto_clinico": "Puérpera com febre e dor na cicatriz, secreção purulenta.",
    }
    resposta = pipeline.processar(requisicao)
    assert set(resposta) == CONTRATO_RESPOSTA
    assert resposta["case_id"] == "abc-123"
    assert resposta["risco_detectado"] in ("BAIXO", "MEDIO", "ALTO")
    assert resposta["evidencias"]["texto"]["achado"] == "sinal_infeccao"
