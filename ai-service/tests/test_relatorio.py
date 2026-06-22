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


def test_recomendacao_especializada_por_gatilho():
    # docs/06 §4: cada gatilho clínico tem encaminhamento próprio.
    md = relatorio.gerar_markdown(
        case_id="c-mix",
        paciente=PACIENTE,
        fusao={
            "risco_detectado": "ALTO",
            "mensagem_alerta": "Vários sinais.",
            "gatilhos": ["infeccao_puerperal", "violencia", "desconforto_psicologico"],
        },
        evidencias=EVIDENCIAS,
    )
    assert "Ação geral (risco ALTO)" in md
    assert "Encaminhamentos específicos" in md
    assert "infecção da cesárea" in md
    assert "protocolo de proteção" in md
    assert "apoio psicológico" in md


def test_recomendacao_cai_no_nivel_sem_gatilho_especializado():
    # Sem gatilho especializado, mantém só a ação geral por nível (sem regressão).
    md = relatorio.gerar_markdown(
        case_id="c-baixo",
        paciente=PACIENTE,
        fusao={"risco_detectado": "BAIXO", "mensagem_alerta": "", "gatilhos": []},
        evidencias={},
    )
    assert "Ação geral (risco BAIXO)" in md
    assert "Encaminhamentos específicos" not in md


def test_anexos_com_links_reais():
    # docs/06 §3/§5: anexos referenciam os artefatos do caso (link http(s) ou identificador).
    artefatos = {
        "video_cicatriz_url": "https://conta.blob.core.windows.net/videos/cic01.jpg",
        "csv_url": "data/sinais_vitais/case01.csv",
        "audio_url": "https://conta.blob.core.windows.net/audios/a01.wav",
    }
    md = relatorio.gerar_markdown(
        case_id="c-anexos",
        paciente=PACIENTE,
        fusao=FUSAO_ALTO,
        evidencias=EVIDENCIAS,
        artefatos=artefatos,
    )
    # Link navegável para artefato em URL http(s).
    assert "[https://conta.blob.core.windows.net/videos/cic01.jpg]" in md
    # Caminho local vira identificador (sem link), não modalidade ausente.
    assert "`data/sinais_vitais/case01.csv`" in md
    # Modalidade sem artefato é omitida.
    assert "Vídeo da fisioterapia" not in md


def test_anexos_sem_artefatos_mantem_legado():
    md = relatorio.gerar_markdown(
        case_id="c-legado", paciente=PACIENTE, fusao=FUSAO_ALTO, evidencias=EVIDENCIAS
    )
    # Sem artefatos, mantém o comportamento legado (lista nomes de modalidade).
    assert "- video_cicatriz" in md


def test_gerar_e_salvar_extrai_artefatos(monkeypatch):
    monkeypatch.setattr(relatorio, "_tentar_pdf", lambda html: None)
    capturado = {}

    class StorageFake:
        def salvar(self, conteudo, nome, *, tipo="application/octet-stream"):
            capturado["conteudo"] = conteudo
            return f"memory://{nome}"

    requisicao = {
        "case_id": "c-req",
        "paciente": PACIENTE,
        "video_cicatriz_url": "https://x/cic.jpg",
        "dados_vitais": {"csv_url": "https://x/v.csv"},
    }
    relatorio.gerar_e_salvar(
        requisicao=requisicao, fusao=FUSAO_ALTO, evidencias=EVIDENCIAS, storage=StorageFake()
    )
    html = capturado["conteudo"].decode("utf-8")
    assert "https://x/cic.jpg" in html
    assert "https://x/v.csv" in html


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
