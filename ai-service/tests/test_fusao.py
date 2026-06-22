"""Testes do motor de fusão clínica (Tarefa 3.1) — núcleo de valor da Fase 3.

Cobre a matriz base (contrato §4), cada regra de elevação, o contexto isolado com teto ``MEDIO`` e
o caso "vermelhidão leve sem febre/PA" que **não** dispara o alerta vermelho.
"""

from __future__ import annotations

from app.fusao import avaliar_fusao


def _cicatriz(evento, conf=0.9):
    return {"evento": evento, "confianca": conf}


def _vitais(tipo, valor="150/95"):
    return {"tipo": tipo, "valor": valor}


def _audio(categoria, conf=0.8):
    return {"categoria": categoria, "confianca": conf}


def _texto(achado, trecho=""):
    return {"achado": achado, "trecho": trecho}


# ── Matriz base (contrato §4) ──────────────────────────────────────────────


def test_base_infeccao_mais_vitais_risco_alto():
    r = avaliar_fusao(
        {"video_cicatriz": _cicatriz("sinal_infeccao"), "sinais_vitais": _vitais("hipertensao")}
    )
    assert r["risco_detectado"] == "ALTO"
    assert "infeccao_puerperal" in r["gatilhos"]


def test_base_infeccao_mais_vitais_normal_medio():
    r = avaliar_fusao(
        {
            "video_cicatriz": _cicatriz("sinal_infeccao"),
            "sinais_vitais": _vitais("normal", "118/76"),
        }
    )
    assert r["risco_detectado"] == "MEDIO"
    assert "cicatriz_infeccao" in r["gatilhos"]


def test_base_ok_mais_vitais_risco_medio():
    r = avaliar_fusao(
        {
            "video_cicatriz": _cicatriz("ferida_ok"),
            "sinais_vitais": _vitais("risco_medio", "130/85"),
        }
    )
    assert r["risco_detectado"] == "MEDIO"
    assert "sinais_vitais_risco" in r["gatilhos"]


def test_base_ok_mais_vitais_normal_baixo():
    r = avaliar_fusao(
        {"video_cicatriz": _cicatriz("ferida_ok"), "sinais_vitais": _vitais("normal", "110/70")}
    )
    assert r["risco_detectado"] == "BAIXO"
    assert r["gatilhos"] == []


# ── Regras de elevação ─────────────────────────────────────────────────────


def test_infeccao_puerperal_por_relato_de_febre_dor():
    r = avaliar_fusao(
        {
            "video_cicatriz": _cicatriz("sinal_infeccao"),
            "texto": _texto("sinal_infeccao", "febre e dor na cicatriz"),
        }
    )
    assert r["risco_detectado"] == "ALTO"
    assert "infeccao_puerperal" in r["gatilhos"]


def test_pre_eclampsia_vitais_mais_texto_complicacao():
    r = avaliar_fusao(
        {
            "sinais_vitais": _vitais("hipertensao", "152/98"),
            "texto": _texto("complicacao", "cefaleia"),
        }
    )
    assert r["risco_detectado"] == "ALTO"
    assert "pre_eclampsia" in r["gatilhos"]


def test_violencia_no_audio_dispara_alto():
    r = avaliar_fusao({"audio": _audio("violencia", 0.9)})
    assert r["risco_detectado"] == "ALTO"
    assert "violencia" in r["gatilhos"]


def test_violencia_fraca_nao_dispara_alto():
    r = avaliar_fusao({"audio": _audio("violencia", 0.5)})
    assert r["risco_detectado"] == "BAIXO"
    assert "violencia" not in r["gatilhos"]


def test_depressao_pos_parto_eleva_para_medio():
    r = avaliar_fusao({"audio": _audio("depressao_pos_parto", 0.8)})
    assert r["risco_detectado"] == "MEDIO"
    assert "desconforto_psicologico" in r["gatilhos"]


# ── Contexto isolado e falsos positivos ────────────────────────────────────


def test_texto_isolado_tem_teto_medio():
    r = avaliar_fusao({"texto": _texto("complicacao", "proteinuria")})
    assert r["risco_detectado"] == "MEDIO"
    assert "texto_complicacao" in r["gatilhos"]


def test_vermelhidao_leve_sem_febre_ou_pa_nao_e_alto():
    # Sinal de infecção isolado, sem vitais de risco nem relato de febre/dor → MEDIO, nunca ALTO.
    r = avaliar_fusao({"video_cicatriz": _cicatriz("sinal_infeccao")})
    assert r["risco_detectado"] == "MEDIO"
    assert "infeccao_puerperal" not in r["gatilhos"]


def test_modalidade_ausente_nao_quebra():
    r = avaliar_fusao({})
    assert r["risco_detectado"] == "BAIXO"
    assert r["gatilhos"] == []
    assert "Sem evidências" in r["mensagem_alerta"]


def test_mensagem_concatena_gatilhos_multiplos():
    r = avaliar_fusao(
        {
            "video_cicatriz": _cicatriz("sinal_infeccao"),
            "sinais_vitais": _vitais("hipertensao", "150/95"),
            "audio": _audio("violencia", 0.9),
        }
    )
    assert r["risco_detectado"] == "ALTO"
    assert "infeccao_puerperal" in r["gatilhos"]
    assert "violencia" in r["gatilhos"]
    # A mensagem reúne as explicações dos gatilhos acionados.
    assert "infecção puerperal" in r["mensagem_alerta"]
    assert "protocolo de proteção" in r["mensagem_alerta"]


def test_fisioterapia_nao_eleva_risco_sozinha():
    r = avaliar_fusao({"video_fisioterapia": {"execucao": "incorreta", "amplitude": "reduzida"}})
    assert r["risco_detectado"] == "BAIXO"
    assert "fisioterapia_alterada" in r["gatilhos"]
