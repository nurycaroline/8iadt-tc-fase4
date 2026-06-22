"""Testes do relatório clínico automático (Tarefa 3.3c / docs/06)."""

from __future__ import annotations

from app import relatorio

PACIENTE = {
    "id": "pac-001",
    "primeiro_nome": "Maria",
    "idade": 31,
    "gestante": False,
    "idade_gestacional_semanas": None,
}

FUSAO_ALTO = {
    "risco_detectado": "ALTO",
    "mensagem_alerta": "Suspeita de infecção puerperal.",
    "gatilhos": ["infeccao_puerperal"],
}

EVIDENCIAS = {
    "video_cicatriz": {"evento": "sinal_infeccao", "confianca": 0.86},
    "sinais_vitais": {"tipo": "hipertensao", "valor": "150/95"},
    "texto": {"achado": "sinal_infeccao", "trecho": "febre e dor na cicatriz"},
}


def test_markdown_contem_secoes_do_template():
    md = relatorio.gerar_markdown(
        case_id="abc-123", paciente=PACIENTE, fusao=FUSAO_ALTO, evidencias=EVIDENCIAS
    )
    assert "RELATÓRIO DE MONITORAMENTO MULTIMODAL — Caso abc-123" in md
    assert "## 1. Resumo executivo" in md
    assert "## 2. Evidências por modalidade" in md
    assert "## 3. Classificação e gatilhos acionados" in md
    assert "## 4. Recomendação / encaminhamento" in md
    assert "## 5. Anexos" in md
    assert "apoio à decisão clínica" in md
    assert "Maria, 31 anos" in md
    assert "Nível de risco:** ALTO" in md


def test_markdown_reflete_o_gatilho():
    md = relatorio.gerar_markdown(
        case_id="c1", paciente=PACIENTE, fusao=FUSAO_ALTO, evidencias=EVIDENCIAS
    )
    assert "Infecção puerperal" in md
    # As evidências por modalidade aparecem no corpo.
    assert "Sinais vitais: hipertensao" in md
    assert "sinal_infeccao" in md


def test_salvar_relatorio_fallback_sem_pdf(tmp_path, monkeypatch):
    # Sem weasyprint disponível, o relatório é salvo em HTML (fallback garantido).
    monkeypatch.setattr(relatorio, "_tentar_pdf", lambda html: None)

    salvos = {}

    class StorageFake:
        def salvar(self, conteudo, nome, *, tipo="application/octet-stream"):
            salvos[nome] = (conteudo, tipo)
            return f"memory://{nome}"

    md = relatorio.gerar_markdown(
        case_id="c2", paciente=PACIENTE, fusao=FUSAO_ALTO, evidencias=EVIDENCIAS
    )
    url = relatorio.salvar_relatorio(md, "c2", storage=StorageFake())
    assert url == "memory://relatorios/c2.html"
    conteudo, tipo = salvos["relatorios/c2.html"]
    assert tipo == "text/html"
    assert b"<html" in conteudo


def test_gerar_e_salvar_local(tmp_path, monkeypatch):
    monkeypatch.setattr(relatorio, "_tentar_pdf", lambda html: None)
    requisicao = {"case_id": "local-1", "paciente": PACIENTE}
    url = relatorio.gerar_e_salvar(requisicao=requisicao, fusao=FUSAO_ALTO, evidencias=EVIDENCIAS)
    assert url.endswith("local-1.html")
    from pathlib import Path

    assert Path(url).exists()
