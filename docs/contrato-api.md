# Contrato de API (Node ↔ Python)

> Definir o **formato do JSON** antes de escrever código evita retrabalho. O front-end/log já sabe como exibir os dados.

## 1. Requisição — Node → Python

`POST /inferencia`

```json
{
  "case_id": "abc-123",
  "paciente": {
    "id": "pac-001",
    "primeiro_nome": "Maria",
    "idade": 31,
    "gestante": true,
    "idade_gestacional_semanas": 28
  },
  "video_cicatriz_url": "https://<conta>.blob.core.windows.net/videos/cicatriz01.jpg",
  "video_fisioterapia_url": "https://<conta>.blob.core.windows.net/videos/fisio01.mp4",
  "dados_vitais": {
    "csv_url": "https://<conta>.blob.core.windows.net/sinais/case01.csv"
  },
  "audio_url": "https://<conta>.blob.core.windows.net/audios/consulta01.wav",
  "texto_clinico": "Laudo/evolução/exame em texto ou URL do documento"
}
```

> O objeto `paciente` é o **contexto mínimo** (criado na "entrada do paciente") e alimenta o cabeçalho do relatório automático. Os dados são pseudonimizados — ver [privacidade/LGPD](07-privacidade-e-seguranca.md).

> Campos opcionais: enviar só as modalidades disponíveis para aquele caso.

## 2. Resposta — Python → Node (JSON de risco padronizado)

```json
{
  "timestamp": "2026-06-10T21:15:00Z",
  "case_id": "abc-123",
  "risco_detectado": "ALTO",
  "evidencias": {
    "video_cicatriz": { "evento": "sinal_infeccao", "confianca": 0.86 },
    "video_fisioterapia": { "execucao": "incorreta", "amplitude": "reduzida" },
    "sinais_vitais": { "tipo": "hipertensao", "valor": "150/95" },
    "audio": { "categoria": "depressao_pos_parto", "confianca": 0.74 },
    "texto": { "achado": "sinal_infeccao", "trecho": "relato de febre e dor na cicatriz" }
  },
  "mensagem_alerta": "Sinal de infecção na cicatriz com relato de febre/dor.",
  "relatorio_url": "https://<conta>.blob.core.windows.net/relatorios/abc-123.pdf"
}
```

## 3. Valores possíveis

| Campo | Valores |
|-------|---------|
| `risco_detectado` | `BAIXO`, `MEDIO`, `ALTO` |
| `evidencias.video_cicatriz.evento` | `ferida_ok`, `sinal_infeccao`, `nenhum` |
| `evidencias.video_fisioterapia.execucao` | `correta`, `incorreta`, `nao_avaliado` |
| `evidencias.sinais_vitais.tipo` | `normal`, `risco_medio`, `hipertensao`, `pre_eclampsia` |
| `evidencias.audio.categoria` | `neutro`, `ansiedade`, `depressao_pos_parto`, `violencia`, `fadiga` |
| `evidencias.texto.achado` | `complicacao`, `sinal_infeccao`, `neutro` |

## 4. Regra de derivação do risco (resumo)

| Vídeo (cicatriz) | Sinais vitais | Risco |
|------------------|---------------|-------|
| sinal de infecção | de risco | **ALTO** |
| sinal de infecção | normal | **MEDIO** |
| ok / nenhum | de risco | **MEDIO** |
| ok / nenhum | normal | **BAIXO** |

> O **áudio** e o **texto/NLP** entram como **contexto adicional** e podem elevar a prioridade de encaminhamento (ex.: violência → protocolo específico; laudo confirmando febre/proteinúria → reforça o risco de infecção/pré-eclâmpsia). Detalhes em [Fase 3](03-fase3-fusao-e-nuvem.md).

> O campo `relatorio_url` aponta para o **relatório automático** gerado por caso — ver [docs/06-relatorios-automaticos.md](06-relatorios-automaticos.md).
