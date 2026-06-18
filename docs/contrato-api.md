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
  "video_url": "https://<conta>.blob.core.windows.net/videos/cirurgia01.mp4",
  "dados_vitais": {
    "csv_url": "https://<conta>.blob.core.windows.net/sinais/case01.csv"
  },
  "audio_url": "https://<conta>.blob.core.windows.net/audios/consulta01.wav",
  "texto_clinico": "Laudo/evolução/prescrição em texto ou URL do documento"
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
    "video": { "evento": "sangramento", "confianca": 0.89 },
    "sinais_vitais": { "tipo": "taquicardia", "valor": 125 },
    "audio": { "categoria": "ansiedade", "confianca": 0.74 },
    "texto": { "achado": "complicacao", "trecho": "sangramento aumentado no pós-operatório" }
  },
  "mensagem_alerta": "Sangramento detectado com instabilidade hemodinâmica.",
  "relatorio_url": "https://<conta>.blob.core.windows.net/relatorios/abc-123.pdf"
}
```

## 3. Valores possíveis

| Campo | Valores |
|-------|---------|
| `risco_detectado` | `BAIXO`, `MEDIO`, `ALTO` |
| `evidencias.video.evento` | `sangramento`, `instrumento`, `anatomia`, `nenhum` |
| `evidencias.sinais_vitais.tipo` | `normal`, `hipotensao`, `taquicardia`, `fhr_anomala` |
| `evidencias.audio.categoria` | `neutro`, `ansiedade`, `depressao_pos_parto`, `violencia`, `fadiga` |
| `evidencias.texto.achado` | `complicacao`, `prescricao_risco`, `neutro` |

## 4. Regra de derivação do risco (resumo)

| Vídeo | Sinais vitais | Risco |
|-------|---------------|-------|
| sangramento | anômalo | **ALTO** |
| sangramento | normal | **MEDIO** |
| nenhum | anômalo | **MEDIO** |
| nenhum | normal | **BAIXO** |

> O **áudio** e o **texto/NLP** entram como **contexto adicional** e podem elevar a prioridade de encaminhamento (ex.: violência → protocolo específico; laudo confirmando complicação → reforça o risco). Detalhes em [Fase 3](03-fase3-fusao-e-nuvem.md).

> O campo `relatorio_url` aponta para o **relatório automático** gerado por caso — ver [docs/06-relatorios-automaticos.md](06-relatorios-automaticos.md).
