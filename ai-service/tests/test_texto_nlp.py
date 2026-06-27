"""Testes do módulo de texto/NLP (T10 + Fase 8: depressão/violência ML + keywords)."""

from __future__ import annotations

from app.texto import nlp
from app.texto.nlp import analisar


def test_sinal_infeccao_por_febre_e_dor():
    evid = analisar("Queixa de febre (38,5°C) e dor na cicatriz, com secreção purulenta.")
    assert evid["achado"] == "sinal_infeccao"
    assert "febre" in evid["trecho"].lower()


def test_complicacao_por_proteinuria_e_cefaleia():
    evid = analisar("PA 152/98 mmHg, proteinúria, cefaleia e escotomas. Hipótese: pré-eclâmpsia.")
    assert evid["achado"] == "complicacao"


def test_depressao_no_sinal_dedicado_nao_em_complicacao():
    # Fase 8: depressão saiu de `complicacao` (keyword) e vive no sinal ML/keywords `depressao`.
    evid = analisar("Relata tristeza persistente e anedonia, compatível com depressão pós-parto.")
    assert evid["achado"] != "complicacao"
    assert evid["depressao"]["rotulo"] == "depressao"
    assert evid["depressao"]["confianca"] > 0.0


def test_violencia_no_sinal_dedicado():
    evid = analisar("Tenho medo dele, ontem ele me bateu e me ameaçou de novo.")
    assert evid["violencia"]["rotulo"] == "violencia"
    assert evid["violencia"]["confianca"] > 0.0


def test_texto_neutro():
    evid = analisar("Puérpera bem, amamentando. Cicatriz limpa e seca. Conduta de rotina.")
    assert evid["achado"] == "neutro"
    assert evid["trecho"] == ""
    assert evid["depressao"]["rotulo"] == "neutro"
    assert evid["violencia"]["rotulo"] == "neutro"


def test_infeccao_tem_precedencia_sobre_complicacao():
    texto = "Febre e dor na cicatriz; também refere cefaleia leve."
    assert analisar(texto)["achado"] == "sinal_infeccao"


def test_depressao_via_modelo_ml(monkeypatch):
    """Quando o classificador ML está presente, a depressão vem dele (não das keywords)."""

    class _PipeFake:
        classes_ = [0, 1]

        def predict_proba(self, textos):
            return [[0.1, 0.9]]

    def _carregar(modalidade, nome):
        return {"pipeline": _PipeFake()} if nome == "depressao" else None

    monkeypatch.setattr(nlp, "carregar_modelo", _carregar)
    # Texto sem palavras-chave de depressão, mas o ML prevê positivo com alta confiança.
    evid = analisar("não sei explicar, só não estou legal ultimamente")
    assert evid["depressao"]["rotulo"] == "depressao"
    assert evid["depressao"]["confianca"] >= 0.8
