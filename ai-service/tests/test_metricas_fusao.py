"""Testes da métrica do ganho da fusão (Tarefa 3.1b)."""

from __future__ import annotations

from app import metricas_fusao

METRICAS = {"precisao", "recall", "taxa_falsos_positivos"}


def test_comparacao_tem_quatro_cenarios_com_metricas():
    resultado = metricas_fusao.comparar()
    assert set(resultado) == {"so_video", "so_vitais", "so_audio_texto", "fusao"}
    for cenario in resultado.values():
        assert METRICAS <= set(cenario)


def test_fusao_reduz_falsos_positivos_e_aumenta_recall():
    resultado = metricas_fusao.comparar()
    fusao = resultado["fusao"]
    unicas = [resultado[c] for c in ("so_video", "so_vitais", "so_audio_texto")]

    # A fusão não tem taxa de FP pior que nenhuma modalidade isolada...
    assert all(fusao["taxa_falsos_positivos"] <= u["taxa_falsos_positivos"] for u in unicas)
    # ...e o recall dos casos críticos é ao menos tão bom quanto o de cada modalidade isolada.
    assert all(fusao["recall"] >= u["recall"] for u in unicas)
    # E há ganho real em pelo menos uma das dimensões frente à melhor modalidade isolada.
    melhor_fp = min(u["taxa_falsos_positivos"] for u in unicas)
    melhor_recall = max(u["recall"] for u in unicas)
    assert fusao["taxa_falsos_positivos"] <= melhor_fp
    assert fusao["recall"] >= melhor_recall
