"""Teste ponta-a-ponta da Fase 3 (Tarefa 3.5) — processa um caso e mostra o alerta.

Exercita o caminho **upload (storage local) → inferência → JSON de risco → alerta**, coletando
evidências (logs/prints) para o relatório técnico e o vídeo. Roda **em processo** (sem exigir
Docker), usando o pipeline do serviço de IA com o adaptador de storage local — o mesmo motor servido
por ``POST /inferencia`` e orquestrado pelo backend Node em ``POST /analisar``.

Observações de ambiente: sem os pesos do YOLO (cicatriz/fisioterapia) e sem transcrição de áudio,
essas modalidades **degradam** (evidência omitida, DD10); o alerta é demonstrado pelas modalidades
disponíveis (sinais vitais + texto). Com os pesos treinados, a fusão escala para ``ALTO``.

Uso (a partir da raiz do repositório)::

    python -m scripts.e2e_demo                # processa data/casos/caso_alto.json
    python -m scripts.e2e_demo --caso caso_medio
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ai-service"))

from app.common import get_logger  # noqa: E402
from app.fusao import avaliar_fusao  # noqa: E402
from app.pipeline import processar  # noqa: E402
from app.storage import LocalStorage  # noqa: E402

LOG = get_logger("e2e_demo")

NIVEIS_ALERTA = {"MEDIO", "ALTO"}


def _seed_sinais_vitais() -> None:
    """Cria um CSV sintético de sinais vitais (com PA de alerta) se ainda não existir."""
    csv = RAIZ / "data" / "sinais_vitais" / "maternal_amostras.csv"
    if csv.exists():
        return
    csv.parent.mkdir(parents=True, exist_ok=True)
    csv.write_text(
        "Age,SystolicBP,DiastolicBP,BS,BodyTemp,HeartRate,RiskLevel\n"
        "31,150,95,7.0,98,88,high\n"
        "29,118,76,6.5,98,76,low\n",
        encoding="utf-8",
    )
    LOG.info("CSV sintético de sinais vitais criado em %s", csv)


def _seed_texto() -> None:
    """Garante os documentos de texto clínico (gera offline se faltarem)."""
    if (RAIZ / "data" / "texto_clinico" / "evolucao_02.txt").exists():
        return
    from scripts.data_prep.texto_clinico import main as gerar_texto

    gerar_texto()


def executar_caso(caso: dict) -> dict:
    """Roda o pipeline (storage local) sobre um caso e devolve o JSON de risco do contrato §2."""
    return processar(caso, storage=LocalStorage())


def _imprimir_evidencias(resposta: dict) -> None:
    print("\nEvidências por modalidade:")
    evid = resposta["evidencias"]
    for modalidade in ("video_cicatriz", "video_fisioterapia", "sinais_vitais", "audio", "texto"):
        if modalidade in evid:
            print(f"  - {modalidade}: {evid[modalidade]}")
        else:
            print(f"  - {modalidade}: (ausente/degradada neste ambiente)")


def _simular_alerta(resposta: dict, paciente: dict) -> None:
    """Imprime o alerta que o backend Node empurraria via socket.io (MEDIO/ALTO)."""
    if resposta["risco_detectado"] in NIVEIS_ALERTA:
        alerta = {
            "case_id": resposta["case_id"],
            "risco_detectado": resposta["risco_detectado"],
            "mensagem_alerta": resposta["mensagem_alerta"],
            "paciente": {"id": paciente.get("id"), "primeiro_nome": paciente.get("primeiro_nome")},
        }
        print("\n>>> ALERTA EM TEMPO REAL (socket.io 'alerta') <<<")
        print(json.dumps(alerta, ensure_ascii=False, indent=2))
        LOG.info("Alerta emitido (%s) para o caso %s", alerta["risco_detectado"], alerta["case_id"])
    else:
        print("\n(Sem alerta de risco — risco BAIXO.)")


def _showcase_alto() -> None:
    """Demonstra a fusão escalando para ALTO com evidência multimodal corroborada."""
    fusao = avaliar_fusao(
        {
            "video_cicatriz": {"evento": "sinal_infeccao", "confianca": 0.88},
            "sinais_vitais": {"tipo": "hipertensao", "valor": "150/95"},
            "texto": {"achado": "sinal_infeccao", "trecho": "febre e dor na cicatriz"},
        }
    )
    print("\n=== Cenário de referência ALTO (cicatriz com pesos treinados) ===")
    print(f"  risco: {fusao['risco_detectado']} | gatilhos: {', '.join(fusao['gatilhos'])}")
    print(f"  mensagem: {fusao['mensagem_alerta']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Demo ponta-a-ponta da fusão multimodal (Fase 3).")
    parser.add_argument("--caso", default="caso_alto", help="nome do caso em data/casos/")
    args = parser.parse_args(argv)

    _seed_sinais_vitais()
    _seed_texto()

    caso_path = RAIZ / "data" / "casos" / f"{args.caso}.json"
    if not caso_path.exists():
        LOG.error("Caso não encontrado: %s", caso_path)
        return 1
    caso = json.loads(caso_path.read_text(encoding="utf-8"))

    LOG.info("Processando %s (case_id=%s) ponta-a-ponta…", args.caso, caso.get("case_id"))
    resposta = executar_caso(caso)

    print("\n=== JSON de risco (contrato §2) ===")
    print(json.dumps(resposta, ensure_ascii=False, indent=2))
    _imprimir_evidencias(resposta)
    _simular_alerta(resposta, caso.get("paciente", {}))
    print(f"\nRelatório gerado em: {resposta.get('relatorio_url')}")
    _showcase_alto()
    return 0


if __name__ == "__main__":
    sys.exit(main())
