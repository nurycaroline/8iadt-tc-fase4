"""Testes da API FastAPI (Tarefa 3.2) via TestClient (httpx)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)

CONTRATO_RESPOSTA = {
    "timestamp",
    "case_id",
    "risco_detectado",
    "evidencias",
    "mensagem_alerta",
    "relatorio_url",
}


def test_health_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_inferencia_payload_valido_retorna_contrato():
    payload = {
        "case_id": "abc-123",
        "paciente": {"id": "p1", "primeiro_nome": "Maria", "idade": 31},
        "texto_clinico": "Puérpera com febre e dor na cicatriz, secreção purulenta.",
    }
    resp = client.post("/inferencia", json=payload)
    assert resp.status_code == 200
    corpo = resp.json()
    assert set(corpo) == CONTRATO_RESPOSTA
    assert corpo["case_id"] == "abc-123"
    assert corpo["risco_detectado"] in ("BAIXO", "MEDIO", "ALTO")
    assert corpo["evidencias"]["texto"]["achado"] == "sinal_infeccao"


def test_inferencia_corpo_invalido_retorna_422():
    # Falta o campo obrigatório `paciente`.
    resp = client.post("/inferencia", json={"case_id": "x"})
    assert resp.status_code == 422


def test_inferencia_modalidade_ausente_nao_quebra():
    payload = {"case_id": "vazio", "paciente": {"id": "p2"}}
    resp = client.post("/inferencia", json=payload)
    assert resp.status_code == 200
    assert resp.json()["risco_detectado"] == "BAIXO"
