"""Utilidades compartilhadas pelos scripts de preparação de dados da Fase 1.

Mantém os scripts de cada modalidade pequenos e idempotentes:
- resolução de caminhos sob ``data/``;
- download seguro (arquivo temporário + rename, evitando arquivos parciais);
- escrita idempotente de JSON/CSV;
- logging estruturado (JSON) com ``case_id``.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

MODALIDADES = (
    "sinais_vitais",
    "video_cicatriz",
    "audio",
    "texto_clinico",
    "casos",
)


class DownloadError(RuntimeError):
    """Erro de download com instrução de obtenção manual."""


def project_root() -> Path:
    """Raiz do repositório (dois níveis acima deste arquivo: scripts/data_prep/)."""
    return Path(__file__).resolve().parents[2]


def data_dir(modalidade: str | None = None) -> Path:
    """Resolve (e cria) o caminho sob ``data/``.

    Sem argumento retorna a raiz de ``data/``. Valida a modalidade quando informada.
    """
    base = project_root() / "data"
    if modalidade is None:
        base.mkdir(parents=True, exist_ok=True)
        return base
    if modalidade not in MODALIDADES:
        raise ValueError(
            f"Modalidade desconhecida: {modalidade!r}. Use uma de {MODALIDADES}."
        )
    path = base / modalidade
    path.mkdir(parents=True, exist_ok=True)
    return path


def download(
    url: str, dest: str | os.PathLike[str], *, overwrite: bool = False, timeout: int = 120
) -> Path:
    """Baixa ``url`` para ``dest`` de forma segura e idempotente (usa a stdlib ``urllib``).

    Grava primeiro num arquivo temporário e só então renomeia para ``dest`` (atômico),
    evitando arquivos parciais corrompidos. Se já existir e ``overwrite`` for falso, retorna o
    arquivo existente. Em falha, levanta :class:`DownloadError` com instrução de obtenção manual.
    """
    import shutil as _shutil
    import urllib.request

    dest = Path(dest)
    if dest.exists() and not overwrite:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)

    tmp_fd, tmp_name = tempfile.mkstemp(dir=str(dest.parent), suffix=".part")
    tmp_path = Path(tmp_name)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "tc-fase4-dataprep"})
        with urllib.request.urlopen(req, timeout=timeout) as resp, os.fdopen(tmp_fd, "wb") as fh:
            _shutil.copyfileobj(resp, fh)
        tmp_path.replace(dest)
        return dest
    except Exception as exc:
        tmp_path.unlink(missing_ok=True)
        raise DownloadError(
            f"Falha ao baixar {url!r}. Baixe a amostra manualmente e salve em {dest}. "
            f"Veja data/README.md para origem/licença. Causa: {exc}"
        ) from exc


def write_json(path: str | os.PathLike[str], obj: Any) -> Path:
    """Escreve ``obj`` como JSON (UTF-8, indentado) de forma idempotente."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    return path


def write_csv(df: Any, path: str | os.PathLike[str]) -> Path:
    """Escreve um DataFrame pandas como CSV (sem índice), criando diretórios."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


class _CaseIdFilter(logging.Filter):
    def __init__(self, case_id: str | None) -> None:
        super().__init__()
        self.case_id = case_id or "-"

    def filter(self, record: logging.LogRecord) -> bool:
        record.case_id = getattr(record, "case_id", self.case_id)
        return True


def get_logger(name: str = "data_prep", case_id: str | None = None) -> logging.Logger:
    """Logger com saída JSON simples incluindo ``case_id`` (observabilidade da stack)."""
    logger = logging.getLogger(f"{name}:{case_id or '-'}")
    if logger.handlers:
        return logger
    handler = logging.StreamHandler()
    fmt = (
        '{"level":"%(levelname)s","logger":"%(name)s",'
        '"case_id":"%(case_id)s","msg":"%(message)s"}'
    )
    handler.setFormatter(logging.Formatter(fmt))
    handler.addFilter(_CaseIdFilter(case_id))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def ffmpeg_disponivel() -> bool:
    """True se o ``ffmpeg`` estiver no PATH (usado para extrair frames/áudio)."""
    return shutil.which("ffmpeg") is not None
