"""Testes do classificador de áudio (T11 + Fase 8: análise dupla)."""

from __future__ import annotations

from app.audio import classificacao
from app.audio.classificacao import classificar, classificar_acustico, inferir


def test_violencia():
    evid = classificar("Tenho medo dele, ontem ele me bateu de novo.")
    assert evid["categoria"] == "violencia"
    assert evid["confianca"] >= 0.7


def test_depressao_pos_parto():
    evid = classificar("Tristeza enorme, não sinto prazer em nada e só tenho vontade de chorar.")
    assert evid["categoria"] == "depressao_pos_parto"


def test_ansiedade():
    evid = classificar("Ando muito ansiosa, o coração acelerado e uma angústia constante.")
    assert evid["categoria"] == "ansiedade"


def test_fadiga():
    evid = classificar("Estou exausta, sem energia, não durmo direito desde o parto.")
    assert evid["categoria"] == "fadiga"


def test_neutro_baixa_confianca():
    evid = classificar("Tudo bem, a consulta foi tranquila e estou me sentindo ok.")
    assert evid["categoria"] == "neutro"
    assert evid["confianca"] < 0.7


def test_violencia_tem_prioridade():
    evid = classificar("Estou cansada e ansiosa, e ele me agrediu ontem.")
    assert evid["categoria"] == "violencia"


# ── Fase 8: trilha acústica + análise dupla ────────────────────────────────


def test_acustico_fallback_neutro_sem_modelo(monkeypatch):
    # Sem modelo treinado, a trilha acústica degrada para neutro (DD10) — não quebra.
    monkeypatch.setattr(classificacao, "carregar_modelo", lambda *a, **k: None)
    rotulo, conf = classificar_acustico("inexistente.wav")
    assert rotulo == "neutro"
    assert 0.0 <= conf <= 1.0


def test_inferir_analise_dupla(monkeypatch):
    # Mocka a transcrição e força acústico neutro: a violência vem da trilha de texto.
    monkeypatch.setattr(classificacao, "_transcrever_seguro", lambda c: "ele me bateu e me ameaçou")
    monkeypatch.setattr(classificacao, "classificar_acustico", lambda c: ("neutro", 0.5))
    evid = inferir("qualquer.wav")
    assert evid["acustico"]["rotulo"] == "neutro"
    assert evid["transcricao"] == "ele me bateu e me ameaçou"
    assert evid["texto"]["violencia"]["rotulo"] == "violencia"
    # Categoria legada derivada deve refletir a violência detectada no texto.
    assert evid["categoria"] == "violencia"


def test_inferir_acustico_violencia(monkeypatch):
    monkeypatch.setattr(classificacao, "_transcrever_seguro", lambda c: "consulta tranquila")
    monkeypatch.setattr(classificacao, "classificar_acustico", lambda c: ("violencia", 0.82))
    evid = inferir("qualquer.wav")
    assert evid["acustico"] == {"rotulo": "violencia", "confianca": 0.82}
    assert evid["categoria"] == "violencia"
