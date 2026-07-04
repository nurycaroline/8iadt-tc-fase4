"""Pipeline de inferência multimodal (Tarefa 3.3 / contrato §1 → §2).

Recebe o **objeto de requisição** do contrato (URLs/dados das modalidades de um caso), roda as
inferências da Fase 2 para as modalidades **presentes**, monta o dicionário de **evidências** e
chama o motor de fusão (:func:`app.fusao.avaliar_fusao`), devolvendo o **JSON de risco padronizado**
do contrato §2.

Princípios:

- **Degrada sem quebrar** (DD10): modalidade ausente ou que falha internamente é **omitida** (campo
  opcional do contrato) e registrada no log — nunca derruba o caso.
- **Reusa** as funções da Fase 2 via atributo de módulo (``detectar``/``prever``/``inferir``/
  ``analisar``), o que mantém o pipeline testável (basta substituir o atributo).
- O relatório automático (Tarefa 3.3c) é gerado de forma **best-effort**: se o módulo/dependências
  estiverem indisponíveis, ``relatorio_url`` fica ``None`` sem quebrar o pipeline.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.audio import classificacao as audio_inf
from app.cicatriz import inferencia as cicatriz_inf
from app.common import get_logger, project_root
from app.fusao import avaliar_fusao
from app.sinais_vitais import inferencia as vitais_inf
from app.texto import nlp as texto_inf


def _timestamp() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _resolver(url: str, storage: Any | None) -> str:
    """Resolve uma URL/caminho do contrato para um caminho local utilizável.

    Com ``storage`` (adaptador Azure/local), delega a ``storage.abrir``. Sem storage, tenta resolver
    como caminho local (relativo à raiz do projeto) e, se não existir, devolve o valor original.
    """
    if storage is not None:
        return str(storage.abrir(url))
    caminho = Path(url)
    if not caminho.is_absolute():
        candidato = project_root() / url
        if candidato.exists():
            return str(candidato)
    return url


def _texto_para_analise(valor: str, storage: Any | None) -> str:
    """Texto clínico pode chegar **inline** ou como caminho/URL de documento."""
    local = _resolver(valor, storage)
    caminho = Path(local)
    if caminho.exists() and caminho.is_file():
        return caminho.read_text(encoding="utf-8")
    return valor


def _registro_vitais(csv_path: str) -> dict[str, Any]:
    """Lê o CSV de sinais vitais e escolhe a linha de **pior caso** (maior PA sistólica)."""
    import pandas as pd

    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError("CSV de sinais vitais vazio.")
    if "SystolicBP" in df.columns:
        linha = df.loc[df["SystolicBP"].idxmax()]
    else:
        linha = df.iloc[0]
    return {col: linha[col] for col in df.columns}


def processar(requisicao: dict[str, Any], *, storage: Any | None = None) -> dict[str, Any]:
    """Orquestra as inferências de um caso e devolve o JSON de risco do contrato §2."""
    case_id = requisicao.get("case_id", "-")
    log = get_logger("pipeline", case_id)
    evidencias: dict[str, Any] = {}

    if requisicao.get("video_cicatriz_url"):
        try:
            fonte = _resolver(requisicao["video_cicatriz_url"], storage)
            evidencias["video_cicatriz"] = cicatriz_inf.detectar(fonte)
        except Exception as exc:
            log.warning("Cicatriz omitida (%s).", exc)

    dados_vitais = requisicao.get("dados_vitais") or {}
    if dados_vitais.get("csv_url"):
        try:
            csv_path = _resolver(dados_vitais["csv_url"], storage)
            evidencias["sinais_vitais"] = vitais_inf.prever(_registro_vitais(csv_path))
        except Exception as exc:
            log.warning("Sinais vitais omitidos (%s).", exc)

    if requisicao.get("audio_url"):
        try:
            fonte = _resolver(requisicao["audio_url"], storage)
            evidencias["audio"] = audio_inf.inferir(fonte)
        except Exception as exc:
            log.warning("Áudio omitido (%s).", exc)

    if requisicao.get("texto_clinico"):
        try:
            texto = _texto_para_analise(requisicao["texto_clinico"], storage)
            evidencias["texto"] = texto_inf.analisar(texto)
        except Exception as exc:
            log.warning("Texto omitido (%s).", exc)

    fusao = avaliar_fusao(evidencias)
    log.info(
        "Fusão concluída: risco=%s gatilhos=%s",
        fusao["risco_detectado"],
        ",".join(fusao["gatilhos"]) or "-",
    )

    resposta: dict[str, Any] = {
        "timestamp": _timestamp(),
        "case_id": case_id,
        "risco_detectado": fusao["risco_detectado"],
        "evidencias": evidencias,
        "mensagem_alerta": fusao["mensagem_alerta"],
        "relatorio_url": _gerar_relatorio(requisicao, fusao, evidencias, storage, log),
    }
    return resposta


def _gerar_relatorio(
    requisicao: dict[str, Any],
    fusao: dict[str, Any],
    evidencias: dict[str, Any],
    storage: Any | None,
    log: Any,
) -> str | None:
    """Gera e salva o relatório clínico (best-effort). Sem o módulo/deps, devolve ``None``."""
    try:
        from app import relatorio
    except Exception:  # pragma: no cover - relatório é opcional para o pipeline
        return None
    try:
        return relatorio.gerar_e_salvar(
            requisicao=requisicao, fusao=fusao, evidencias=evidencias, storage=storage
        )
    except Exception as exc:  # pragma: no cover - degrada sem quebrar
        log.warning("Relatório não gerado (%s).", exc)
        return None
