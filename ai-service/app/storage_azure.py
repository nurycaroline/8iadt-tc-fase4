"""Adaptador de storage para **Azure Blob Storage** (modo nuvem da Tarefa 3.4).

Mesma interface de :class:`app.storage.LocalStorage` (``salvar``/``abrir``/``remover``), selecionada
por ``STORAGE_BACKEND=azure`` + ``AZURE_STORAGE_CONNECTION_STRING``. As URLs de leitura recebem um
**SAS com expiração** (docs/07: segredos fora do Git, acesso temporário e auditável).

Validado por smoke com credencial de teste (DD11); o caminho do *gate* continua sendo o storage
local. Sem credencial, :func:`app.storage.get_storage` cai automaticamente no fallback local.
"""

from __future__ import annotations

import os
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

from app.common import get_logger

LOG = get_logger("storage_azure")


class AzureBlobStorage:
    """Armazenamento em Azure Blob com URLs SAS de leitura (expiração configurável)."""

    def __init__(
        self,
        connection_string: str | None = None,
        container: str | None = None,
        sas_minutes: int | None = None,
    ) -> None:
        from azure.storage.blob import BlobServiceClient

        cs = connection_string or os.environ["AZURE_STORAGE_CONNECTION_STRING"]
        self.service = BlobServiceClient.from_connection_string(cs)
        self.container = container or os.environ.get("AZURE_STORAGE_CONTAINER", "monitoramento")
        self.sas_minutes = int(sas_minutes or os.environ.get("AZURE_SAS_EXPIRY_MINUTES", "60"))
        try:
            self.service.create_container(self.container)
        except Exception:  # pragma: no cover - container já existe
            pass

    def salvar(self, conteudo: bytes | str, nome: str, *, tipo: str | None = None) -> str:
        from azure.storage.blob import ContentSettings

        dados = conteudo.encode("utf-8") if isinstance(conteudo, str) else conteudo
        blob = self.service.get_blob_client(self.container, nome)
        ajustes = ContentSettings(content_type=tipo) if tipo else None
        blob.upload_blob(dados, overwrite=True, content_settings=ajustes)
        LOG.info("Artefato enviado ao Blob: %s/%s", self.container, nome)
        return self._url_com_sas(nome)

    def abrir(self, url: str) -> str:
        nome = self._blob_name(url)
        blob = self.service.get_blob_client(self.container, nome)
        destino = tempfile.NamedTemporaryFile(delete=False, suffix=Path(nome).suffix)
        destino.write(blob.download_blob().readall())
        destino.close()
        return destino.name

    def remover(self, url: str) -> None:
        nome = self._blob_name(url)
        try:
            self.service.get_blob_client(self.container, nome).delete_blob()
        except Exception as exc:  # pragma: no cover - blob ausente
            LOG.info("Falha ao remover blob %s (%s).", nome, exc)

    def _url_com_sas(self, nome: str) -> str:
        from azure.storage.blob import BlobSasPermissions, generate_blob_sas

        sas = generate_blob_sas(
            account_name=self.service.account_name,
            container_name=self.container,
            blob_name=nome,
            account_key=self.service.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(UTC) + timedelta(minutes=self.sas_minutes),
        )
        return f"{self.service.url}{self.container}/{nome}?{sas}"

    def _blob_name(self, url: str) -> str:
        # Aceita tanto o nome do blob direto quanto uma URL https completa (com/sem SAS).
        if not url.lower().startswith("http"):
            return url
        caminho = urlparse(url).path.lstrip("/")
        prefixo = f"{self.container}/"
        return caminho[len(prefixo):] if caminho.startswith(prefixo) else caminho
