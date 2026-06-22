"""Autenticação por credencial de serviço do ``ai-service`` (Fase 7 — F7-01 / docs/07 §2).

O serviço de IA processa dados sensíveis e **não deve ficar acessível sem auth**. A credencial é
lida da variável de ambiente ``AI_SERVICE_API_KEY`` (segredo fora do Git):

- variável definida  → exige o header ``X-API-Key`` correto (``401`` caso contrário);
- variável ausente   → auth desabilitada (preserva os testes e a demo/fallback local — DD10).

Sem cadastro de usuários (fora de escopo); é uma credencial de serviço entre o backend e o
``ai-service``.
"""

from __future__ import annotations

import os

from fastapi import Header, HTTPException, status


def verificar_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Dependência do FastAPI: valida a credencial de serviço quando configurada."""
    esperado = os.environ.get("AI_SERVICE_API_KEY", "")
    if not esperado:
        return  # Auth desabilitada (dev/test/demo) — comportamento atual preservado.
    if x_api_key != esperado:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="credencial de serviço ausente ou inválida",
        )
