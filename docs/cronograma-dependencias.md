# Cronograma por Dependências (Caminho Crítico)

> Em vez de datas, este documento mostra **o que bloqueia o quê**. Use para paralelizar o trabalho no grupo e não travar na integração.

## 1. Grafo de dependências

```
                    ┌─────────────────────────┐
                    │ M0. Setup repo + escopo  │
                    └────────────┬─────────────┘
            ┌────────────────────┼────────────────────┬───────────────┐
            ▼                    ▼                    ▼               ▼
   ┌────────────────┐  ┌──────────────────┐  ┌────────────┐  ┌────────────┐
   │ M1. Dados vídeo│  │ M2. Dados vitais │  │ M3. Áudio  │  │ M4. Texto  │
   │   + anotação   │  │  + limpeza       │  │ + transcr. │  │  laudos    │
   └───────┬────────┘  └────────┬─────────┘  └─────┬──────┘  └─────┬──────┘
           ▼                    ▼                  ▼               ▼
   ┌────────────────┐  ┌──────────────────┐  ┌────────────┐  ┌────────────┐
   │ M5. Modelo YOLO│  │ M6. Modelo vitais│  │ M7. Class. │  │ M8. NLP    │
   └───────┬────────┘  └────────┬─────────┘  │   áudio    │  │  texto     │
           │                    │            └─────┬──────┘  └─────┬──────┘
           └──────────┬─────────┴──────────────────┴───────────────┘
                      ▼
        ┌──────────────────────────────┐
        │ M9. CASO DE EXEMPLO SINTÉTICO ★│  (★ bloqueia a demo da fusão)
        └──────────────┬───────────────┘
                       ▼
        ┌──────────────────────────────┐
        │ M10. Motor de fusão + métricas│
        └──────────────┬───────────────┘
                       ▼
        ┌──────────────────────────────┐
        │ M11. API Python + Node + Azure│
        └──────────────┬───────────────┘
                       ▼
        ┌──────────────────────────────┐
        │ M12. Relatórios + tempo real  │
        └──────────────┬───────────────┘
                       ▼
        ┌──────────────────────────────┐
        │ M13. Repo + relatório + vídeo │
        └──────────────────────────────┘
```

## 2. Caminho crítico (o que NÃO pode atrasar)

`M0 → (M1+M9) → M5 → M10 → M11 → M12 → M13`

- O **caso de exemplo sintético (M9)** é o gargalo mais subestimado: sem ele (juntar amostras numa paciente fictícia), a **fusão (M10)** não tem como ser demonstrada. **Faça M9 cedo.**
- M5 (YOLO) costuma ser o item mais demorado (treino). Comece o quanto antes, em paralelo.

## 3. O que pode rodar em paralelo
- M1–M4 (coleta de dados das 4 modalidades) são independentes → dividir entre integrantes.
- M5–M8 (modelos) são independentes entre si, dependem só do seu dado correspondente.
- Backend Node + setup Azure (parte de M11) podem começar antes dos modelos ficarem prontos, usando um **mock da resposta de IA** (o contrato de API já está definido).

## 4. Marcos de validação (gates)
| Marco | Critério para avançar |
|-------|-----------------------|
| Fim da Fase 1 | mini-dataset (5 por modalidade) + caso de exemplo sintético pronto |
| Fim da Fase 2 | 4 modelos com métricas individuais |
| Fim da Fase 3 | pipeline ponta-a-ponta + métricas da fusão |
| Fim da Fase 4 | repo + relatório + vídeo publicados |

> Regra de ouro: só escale (mais dados, mais épocas) **depois** que o pipeline rodar inteiro com o mini-dataset.
