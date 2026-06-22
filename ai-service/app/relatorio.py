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

DISCLAIMER = (
    "AVISO: Documento de apoio à decisão clínica gerado automaticamente. "
    "Não substitui a avaliação de profissionais de saúde."
)


def _cabecalho_paciente(paciente: dict[str, Any]) -> str:
    nome = paciente.get("primeiro_nome", "—")
    idade = paciente.get("idade", "—")
    base = f"{nome}, {idade} anos"
    if paciente.get("gestante") and paciente.get("idade_gestacional_semanas") is not None:
        base += f" — gestante, {paciente['idade_gestacional_semanas']} sem"
    return base


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
    txt = evidencias.get("texto")
    if txt:
        trecho = txt.get("trecho") or ""
        sufixo = f' — "{trecho}"' if trecho else ""
        linhas.append(f"- Texto/laudo: {txt.get('achado')}{sufixo}")
    if not linhas:
        linhas.append("- Nenhuma modalidade avaliada para este caso.")
    return linhas


def gerar_markdown(
    *,
    case_id: str,
    paciente: dict[str, Any],
    fusao: dict[str, Any],
    evidencias: dict[str, Any],
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
            RECOMENDACAO.get(risco, RECOMENDACAO["BAIXO"]),
            "",
            "## 5. Anexos",
            "",
            _secao_anexos(evidencias),
            "",
            "---",
            "",
            f"_{DISCLAIMER}_",
            "",
        ]
    )


def _secao_anexos(evidencias: dict[str, Any]) -> str:
    # As URLs dos artefatos pertencem ao payload de requisição; aqui referenciamos as modalidades.
    presentes = [m for m in evidencias]
    if not presentes:
        return "- Sem anexos."
    return "\n".join(f"- {m}" for m in presentes)


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
    )
    return salvar_relatorio(md, case_id, storage=storage)
