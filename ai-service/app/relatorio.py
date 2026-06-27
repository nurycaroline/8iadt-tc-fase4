"""Relatório clínico automático por caso (Tarefa 3.3c / docs/06).

Gera, a partir do JSON de fusão, um **relatório estruturado** em Markdown (template de docs/06 §3),
converte para HTML e — quando o ambiente suporta — para PDF (``weasyprint``). O documento é salvo
via adaptador de storage (Azure/local) e sua URL preenche ``relatorio_url`` no JSON de resposta.

Decisões (design DD7): a geração em **Markdown/HTML é sempre garantida**; o PDF é melhor-esforço e,
se a dependência de sistema faltar, o relatório fica em HTML sem quebrar o pipeline.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.common import data_dir, get_logger
from app.fusao import RECOMENDACAO

LOG = get_logger("relatorio")

# Rótulo amigável por gatilho (rastreabilidade no relatório).
GATILHO_LABEL = {
    "infeccao_puerperal": "Infecção puerperal (cicatriz + febre/dor ou vitais de risco)",
    "pre_eclampsia": "Pré-eclâmpsia (vitais de risco + cefaleia/proteinúria)",
    "violencia": "Violência doméstica — protocolo de proteção",
    "desconforto_psicologico": "Desconforto psicológico (depressão pós-parto/ansiedade)",
    "cicatriz_infeccao": "Sinal de infecção na cicatriz",
    "sinais_vitais_risco": "Sinais vitais alterados",
    "texto_complicacao": "Complicação relatada no texto clínico",
    "texto_infeccao": "Relato de febre/dor na evolução clínica",
    "fisioterapia_alterada": "Execução de fisioterapia alterada",
}

NIVEL_DISPLAY = {"ALTO": "ALTO", "MEDIO": "MÉDIO", "BAIXO": "BAIXO"}

# Encaminhamento especializado por tipo de risco (docs/06 §4): cada gatilho clínico mapeia para o
# conteúdo-chave/conduta do PDF. Reusa os gatilhos de ``app.fusao`` (rastreabilidade), sem duplicar
# a decisão de risco — sem gatilho especializado, cai na recomendação por nível.
ENCAMINHAMENTO_GATILHO = {
    "infeccao_puerperal": (
        "Risco de infecção da cesárea — reavaliar a ferida operatória e acionar avaliação médica "
        "para conduta (curativo/antibioticoterapia) com prioridade."
    ),
    "pre_eclampsia": (
        "Risco hipertensivo / pré-eclâmpsia — monitorar a pressão arterial e sinais de alarme; "
        "encaminhar para avaliação obstétrica urgente."
    ),
    "violencia": (
        "Protocolo de proteção à mulher — acionar a rede de apoio e os canais de proteção "
        "conforme o protocolo institucional."
    ),
    "desconforto_psicologico": (
        "Encaminhamento para avaliação/apoio psicológico (depressão pós-parto/ansiedade)."
    ),
}

DISCLAIMER = (
    "AVISO: Documento de apoio à decisão clínica gerado automaticamente. "
    "Não substitui a avaliação de profissionais de saúde."
)

# Rótulo dos artefatos para a seção de anexos (docs/06 §3/§5): "links Blob: frame, gráfico, áudio".
# A ordem segue as modalidades; a chave casa com o objeto de requisição do contrato (§1).
ROTULO_ARTEFATO = {
    "video_cicatriz_url": "Vídeo/imagem da cicatriz (frame de alerta)",
    "video_fisioterapia_url": "Vídeo da fisioterapia",
    "csv_url": "Sinais vitais (CSV/gráfico)",
    "audio_url": "Áudio da consulta/relato",
    "texto_clinico": "Texto/laudo clínico",
}


def _cabecalho_paciente(paciente: dict[str, Any]) -> str:
    nome = paciente.get("primeiro_nome", "—")
    idade = paciente.get("idade", "—")
    base = f"{nome}, {idade} anos"
    if paciente.get("gestante") and paciente.get("idade_gestacional_semanas") is not None:
        base += f" — gestante, {paciente['idade_gestacional_semanas']} sem"
    return base


def _fmt_sub(sub: Any) -> str | None:
    """Formata uma subevidência ML da Fase 8 (depressão/violência) como "rótulo (confiança)".

    Retorna ``None`` quando ausente ou ``neutro``, para não poluir o relatório com não-achados.
    """
    if not isinstance(sub, dict):
        return None
    rotulo = sub.get("rotulo")
    if not rotulo or rotulo == "neutro":
        return None
    conf = sub.get("confianca")
    return f"{rotulo} (confiança {conf})" if conf is not None else str(rotulo)


def _linha_evidencia(evidencias: dict[str, Any]) -> list[str]:
    linhas = []
    cic = evidencias.get("video_cicatriz")
    if cic:
        linhas.append(
            f"- Vídeo (cicatriz): {cic.get('evento')} (confiança {cic.get('confianca')})"
        )
    fis = evidencias.get("video_fisioterapia")
    if fis:
        amp = f", amplitude {fis['amplitude']}" if fis.get("amplitude") else ""
        linhas.append(f"- Vídeo (fisioterapia): {fis.get('execucao')}{amp}")
    vit = evidencias.get("sinais_vitais")
    if vit:
        linhas.append(f"- Sinais vitais: {vit.get('tipo')} (valor {vit.get('valor')})")
    aud = evidencias.get("audio")
    if aud:
        linhas.append(f"- Áudio: {aud.get('categoria')} (confiança {aud.get('confianca')})")
        # Fase 8: análise dupla — sinais acústico e da fala (transcrição) quando indicam risco.
        acustico = _fmt_sub(aud.get("acustico"))
        if acustico:
            linhas.append(f"  - Violência (acústico): {acustico}")
        fala = aud.get("texto") or {}
        if (dep := _fmt_sub(fala.get("depressao"))) is not None:
            linhas.append(f"  - Depressão (fala): {dep}")
        if (vio := _fmt_sub(fala.get("violencia"))) is not None:
            linhas.append(f"  - Violência (fala): {vio}")
    txt = evidencias.get("texto")
    if txt:
        trecho = txt.get("trecho") or ""
        sufixo = f' — "{trecho}"' if trecho else ""
        linhas.append(f"- Texto/laudo: {txt.get('achado')}{sufixo}")
        # Fase 8: sinais ML de depressão/violência no texto, quando indicam risco.
        if (dep := _fmt_sub(txt.get("depressao"))) is not None:
            linhas.append(f"  - Depressão: {dep}")
        if (vio := _fmt_sub(txt.get("violencia"))) is not None:
            linhas.append(f"  - Violência: {vio}")
    if not linhas:
        linhas.append("- Nenhuma modalidade avaliada para este caso.")
    return linhas


def gerar_markdown(
    *,
    case_id: str,
    paciente: dict[str, Any],
    fusao: dict[str, Any],
    evidencias: dict[str, Any],
    artefatos: dict[str, str] | None = None,
    timestamp: str | None = None,
) -> str:
    """Monta o relatório em Markdown (função pura) seguindo o template de docs/06 §3."""
    ts = timestamp or datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    risco = fusao.get("risco_detectado", "BAIXO")
    gatilhos = fusao.get("gatilhos", [])

    if gatilhos:
        secao_gatilhos = "\n".join(
            f"- {GATILHO_LABEL.get(g, g)}" for g in gatilhos
        )
    else:
        secao_gatilhos = "- Nenhum gatilho clínico acionado."

    secao_evidencias = "\n".join(_linha_evidencia(evidencias))

    return "\n".join(
        [
            f"# RELATÓRIO DE MONITORAMENTO MULTIMODAL — Caso {case_id}",
            "",
            f"**Paciente:** {_cabecalho_paciente(paciente)}  ",
            f"**Data/hora:** {ts}  ",
            f"**Nível de risco:** {NIVEL_DISPLAY.get(risco, risco)}",
            "",
            "## 1. Resumo executivo",
            "",
            fusao.get("mensagem_alerta", ""),
            "",
            "## 2. Evidências por modalidade",
            "",
            secao_evidencias,
            "",
            "## 3. Classificação e gatilhos acionados",
            "",
            secao_gatilhos,
            "",
            "## 4. Recomendação / encaminhamento",
            "",
            _secao_recomendacao(risco, gatilhos),
            "",
            "## 5. Anexos",
            "",
            _secao_anexos(evidencias, artefatos),
            "",
            "---",
            "",
            f"_{DISCLAIMER}_",
            "",
        ]
    )


def _secao_recomendacao(risco: str, gatilhos: list[str]) -> str:
    """Monta a seção 4: **ação geral por nível** + **encaminhamentos especializados** (docs/06 §4).

    Cada gatilho clínico acionado contribui com seu encaminhamento próprio (infecção puerperal,
    pré-eclâmpsia, violência, desconforto psicológico). Quando nenhum gatilho especializado é
    acionado, fica apenas a ação geral por nível (compatibilidade — sem regressão).
    """
    nivel = NIVEL_DISPLAY.get(risco, risco)
    linhas = [f"**Ação geral (risco {nivel}):** {RECOMENDACAO.get(risco, RECOMENDACAO['BAIXO'])}"]

    especificos = [
        ENCAMINHAMENTO_GATILHO[g] for g in gatilhos if g in ENCAMINHAMENTO_GATILHO
    ]
    if especificos:
        linhas.append("")
        linhas.append("**Encaminhamentos específicos:**")
        linhas.extend(f"- {texto}" for texto in especificos)
    return "\n".join(linhas)


def _parece_url(valor: Any) -> bool:
    return isinstance(valor, str) and valor.startswith(("http://", "https://"))


def _linha_anexo(rotulo: str, valor: str) -> str:
    """Referência navegável a um artefato (link http(s); caminho/identificador, caso contrário)."""
    if _parece_url(valor):
        return f"- {rotulo}: [{valor}]({valor})"
    return f"- {rotulo}: `{valor}`"


def _secao_anexos(
    evidencias: dict[str, Any], artefatos: dict[str, str] | None = None
) -> str:
    """Seção 5: links reais dos artefatos do caso (docs/06 §3/§5), omitindo modalidades ausentes.

    Com ``artefatos`` (URLs/caminhos do objeto de requisição do contrato), referencia o frame da
    cicatriz, o gráfico/CSV dos sinais vitais, o áudio/transcrição e o texto/laudo. Sem ele, mantém
    o comportamento legado (lista os nomes das modalidades avaliadas).
    """
    if artefatos:
        linhas = [
            _linha_anexo(rotulo, artefatos[chave])
            for chave, rotulo in ROTULO_ARTEFATO.items()
            if artefatos.get(chave)
        ]
        audio = evidencias.get("audio") or {}
        transcricao = audio.get("transcricao") or audio.get("trecho")
        if transcricao:
            linhas.append(f"  - Transcrição/trecho do áudio: “{transcricao}”")
        return "\n".join(linhas) if linhas else "- Sem anexos."

    presentes = [m for m in evidencias]
    if not presentes:
        return "- Sem anexos."
    return "\n".join(f"- {m}" for m in presentes)


def _artefatos_da_requisicao(requisicao: dict[str, Any]) -> dict[str, str]:
    """Extrai as URLs/caminhos dos artefatos do objeto de requisição (contrato §1) p/ os anexos."""
    artefatos: dict[str, str] = {}
    for chave in ("video_cicatriz_url", "video_fisioterapia_url", "audio_url"):
        if requisicao.get(chave):
            artefatos[chave] = requisicao[chave]
    dados_vitais = requisicao.get("dados_vitais") or {}
    if dados_vitais.get("csv_url"):
        artefatos["csv_url"] = dados_vitais["csv_url"]
    if requisicao.get("texto_clinico"):
        artefatos["texto_clinico"] = requisicao["texto_clinico"]
    return artefatos


def _markdown_para_html(md: str) -> str:
    import markdown as _md

    corpo = _md.markdown(md, extensions=["extra"])
    return (
        "<!DOCTYPE html>\n<html lang=\"pt-br\"><head><meta charset=\"utf-8\">"
        "<title>Relatório de monitoramento multimodal</title></head>"
        f"<body>{corpo}</body></html>"
    )


def _tentar_pdf(html: str) -> bytes | None:
    """Converte HTML→PDF se ``weasyprint`` (e libs de sistema) estiver disponível (DD7)."""
    try:
        from weasyprint import HTML  # type: ignore

        return HTML(string=html).write_pdf()
    except Exception as exc:  # pragma: no cover - depende de libs de sistema
        LOG.info("PDF indisponível (%s); mantendo HTML.", exc)
        return None


def salvar_relatorio(
    markdown_texto: str, case_id: str, *, storage: Any | None = None
) -> str:
    """Converte e salva o relatório; devolve a URL/caminho. PDF é melhor-esforço (fallback HTML)."""
    html = _markdown_para_html(markdown_texto)
    pdf = _tentar_pdf(html)

    if pdf is not None:
        conteudo, nome, tipo = pdf, f"{case_id}.pdf", "application/pdf"
    else:
        conteudo, nome, tipo = html.encode("utf-8"), f"{case_id}.html", "text/html"

    if storage is not None:
        return str(storage.salvar(conteudo, f"relatorios/{nome}", tipo=tipo))

    destino = data_dir("casos").parent / "_storage" / "relatorios" / nome
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(conteudo)
    LOG.info("Relatório salvo em %s", destino)
    return str(destino)


def gerar_e_salvar(
    *,
    requisicao: dict[str, Any],
    fusao: dict[str, Any],
    evidencias: dict[str, Any],
    storage: Any | None = None,
) -> str:
    """Atalho usado pelo pipeline: gera o Markdown e salva o relatório, devolvendo a URL."""
    case_id = requisicao.get("case_id", "caso")
    md = gerar_markdown(
        case_id=case_id,
        paciente=requisicao.get("paciente", {}),
        fusao=fusao,
        evidencias=evidencias,
        artefatos=_artefatos_da_requisicao(requisicao),
    )
    return salvar_relatorio(md, case_id, storage=storage)
