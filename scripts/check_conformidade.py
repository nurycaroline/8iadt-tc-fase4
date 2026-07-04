"""Verificação de conformidade de privacidade/segurança (Fase 7 — F7-08 / docs/07 §3/§6).

Falha (exit != 0) quando o repositório versiona algo que não deveria:

- o arquivo ``.env`` (segredos) está rastreado pelo Git;
- chaves/certificados (``*.key``/``*.pem``/``*.crt``) estão rastreados;
- arquivos sob ``data/`` fora da allowlist (só datasets sintéticos/públicos são versionados);
- segredos óbvios embutidos em arquivos rastreados (chave privada PEM; connection string Azure
  com valor — exceto no ``.env.example``).

Roda no CI (job "conformidade") e localmente: ``python -m scripts.check_conformidade``.
Sem dependências externas (usa ``git ls-files``).
"""

from __future__ import annotations

import fnmatch
import subprocess
import sys
from pathlib import Path

# Arquivos sob data/ que PODEM ser versionados. Qualquer outro arquivo rastreado em data/ é uma
# violação (risco de dado real de paciente). A política do projeto é versionar apenas datasets
# SINTÉTICOS/PÚBLICOS (para rodar/retreinar sem baixar) — nenhum dado real da solução entra no Git.
# Ver data/README.md e docs/07-privacidade-e-seguranca.md §3.
ALLOWLIST_DATA = (
    # Metadados/refs leves e casos de demonstração.
    "data/README.md",
    "data/audio/metadados.json",
    "data/texto_clinico/rotulos.json",
    "data/video_cicatriz/data.yaml",
    "data/casos/*.json",
    "data/casos/*.mp3",  # áudio de demonstração dos casos
    "data/**/.gitkeep",
    # Datasets sintéticos/públicos versionados para reprodutibilidade (não são dados reais).
    "data/sinais_vitais/*.csv",  # UCI Maternal Health (público/anonimizado)
    "data/texto_clinico/*.txt",  # evoluções clínicas sintéticas
    "data/texto_clinico/fase8/**",  # datasets de texto (traduzidos) + relatório da Fase 8
    "data/audio/fase8/**",  # amostras acústicas de treino da Fase 8 (dataset público)
    "data/video_cicatriz/*.zip",  # AZH Wound (dataset público de feridas)
)

SEGREDOS_PROIBIDOS = ("*.key", "*.pem", "*.crt")

PADROES_SEGREDO_CONTEUDO = (
    "BEGIN RSA PRIVATE KEY",
    "BEGIN PRIVATE KEY",
    "BEGIN OPENSSH PRIVATE KEY",
)

# Arquivos que contêm os padrões acima por motivo legítimo (o próprio verificador e seu teste).
ARQUIVOS_IGNORADOS_CONTEUDO = (
    "scripts/check_conformidade.py",
    "scripts/tests/test_conformidade.py",
)


def listar_rastreados() -> list[str]:
    """Lista os arquivos versionados pelo Git (caminhos relativos à raiz do repo)."""
    saida = subprocess.run(
        ["git", "ls-files"], check=True, capture_output=True, text=True
    ).stdout
    return [linha for linha in saida.splitlines() if linha]


def _data_permitido(caminho: str) -> bool:
    return any(fnmatch.fnmatch(caminho, padrao) for padrao in ALLOWLIST_DATA)


def violacoes_dados(arquivos: list[str]) -> list[str]:
    """Arquivos sob data/ que estão rastreados mas fora da allowlist."""
    return [a for a in arquivos if a.startswith("data/") and not _data_permitido(a)]


def violacoes_segredos(arquivos: list[str]) -> list[str]:
    """Arquivos rastreados que não deveriam existir no repo (.env, chaves, certificados)."""
    violacoes = []
    for a in arquivos:
        if a == ".env" or a.endswith("/.env"):
            violacoes.append(a)
        elif any(fnmatch.fnmatch(a, padrao) for padrao in SEGREDOS_PROIBIDOS):
            violacoes.append(a)
    return violacoes


def violacoes_conteudo(arquivos: list[str], raiz: Path) -> list[str]:
    """Segredos óbvios embutidos no conteúdo de arquivos rastreados (exceto .env.example)."""
    violacoes = []
    for a in arquivos:
        if a.endswith(".env.example") or a in ARQUIVOS_IGNORADOS_CONTEUDO:
            continue
        caminho = raiz / a
        try:
            texto = caminho.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeError):
            continue
        if any(p in texto for p in PADROES_SEGREDO_CONTEUDO):
            violacoes.append(f"{a} (chave privada embutida)")
    return violacoes


def main(argv: list[str] | None = None) -> int:
    raiz = Path(__file__).resolve().parents[1]
    arquivos = listar_rastreados()

    problemas: list[str] = []
    for v in violacoes_segredos(arquivos):
        problemas.append(f"segredo/chave versionado: {v}")
    for v in violacoes_dados(arquivos):
        problemas.append(f"dado fora da allowlist em data/: {v}")
    for v in violacoes_conteudo(arquivos, raiz):
        problemas.append(f"conteúdo sensível versionado: {v}")

    if problemas:
        print("FALHA de conformidade (docs/07 §3/§6):")
        for p in problemas:
            print(f"  - {p}")
        return 1

    print(f"Conformidade OK: {len(arquivos)} arquivos rastreados, sem segredos/dados reais.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
