"""Smoke do pipeline ponta-a-ponta (Tarefa 3.5) — caso inline, sem depender de pesos/dados."""

from __future__ import annotations

from scripts.e2e_demo import executar_caso

CONTRATO = {
    "timestamp",
    "case_id",
    "risco_detectado",
    "evidencias",
    "mensagem_alerta",
    "relatorio_url",
}


def test_e2e_caso_inline_produz_resposta_valida():
    caso = {
        "case_id": "e2e-smoke",
        "paciente": {"id": "p1", "primeiro_nome": "Maria", "idade": 31},
        "texto_clinico": "Puérpera com febre e dor na cicatriz, secreção purulenta.",
    }
    resposta = executar_caso(caso)
    assert set(resposta) == CONTRATO
    assert resposta["case_id"] == "e2e-smoke"
    assert resposta["risco_detectado"] in ("BAIXO", "MEDIO", "ALTO")
    # O texto clínico inline foi analisado (achado de infecção) e o relatório foi gerado.
    assert resposta["evidencias"]["texto"]["achado"] == "sinal_infeccao"
    assert resposta["relatorio_url"]
