# Fase 4 — Empacotamento e Entregáveis

> Objetivo: empacotar a solução com **padrão de engenharia de software** e produzir os 3 entregáveis avaliados: **Repositório Git**, **Relatório técnico** e **Vídeo**.

## Resultado esperado (Definition of Done)
- [x] Repositório organizado, com `README.md` e `requirements.txt`/`package.json`. (auditado — T1/T7; gate verde)
- [x] Relatório técnico completo. ([`docs/relatorio-tecnico.md`](relatorio-tecnico.md), 6 seções — T4; PDF/HTML via [`scripts/exportar_relatorio.py`](../scripts/exportar_relatorio.py) — T5)
- [ ] Vídeo de até 15 min publicado (YouTube/Vimeo, público ou não listado). — **ação humana**; roteiro pronto em [`docs/roteiro-video.md`](roteiro-video.md) (T6) e placeholder de link no [`README.md`](../README.md) (T7)

> **Estado da Fase 4 (planejamento em [`.specs/features/fase4-entregaveis/`](../.specs/features/fase4-entregaveis/)):**
> tarefas T1–T9 implementadas. Os 2 entregáveis do agente (repositório auditado + relatório técnico) estão
> prontos; o 3º (vídeo) depende de gravação/publicação humana, com **roteiro** e **placeholder de link**
> entregues. Evidências reais consolidadas em [`docs/relatorio/`](relatorio/) (métricas, exemplo de
> relatório automático, log E2E). Nenhuma métrica foi inventada (`AGENTS.md`).

---

## Tarefa 4.1 — Repositório Git
- Estrutura em pastas (ver seção 6 do [plano mestre](../PLANO_DE_DESENVOLVIMENTO.md)): `/ai-service`, `/backend`, `/docs`, `/scripts`.
- `requirements.txt` (Python) e `package.json` (Node) com versões fixadas.
- `README.md` com **instruções de execução** claras (como instalar, configurar `.env`, rodar cada serviço, ou `docker compose up`).
- `.gitignore` cobrindo `data/`, `.env`, pesos grandes (ou usar **Git LFS**).
- **Docker/docker-compose**, **testes** e **CI** configurados — ver [qualidade-testes-ci.md](qualidade-testes-ci.md).

## Tarefa 4.2 — Relatório técnico
Deve conter (conforme o PDF):
1. **Descrição do fluxo multimodal** (diagrama de arquitetura).
2. **Modelos aplicados em cada tipo de dado** (vídeo — cicatriz/fisioterapia, áudio, sinais vitais, texto) e justificativa das escolhas (por que YOLOv8/YOLOv8-pose, por que Random Forest/Isolation Forest).
3. **Lógica de fusão** (motor de regras) **e a métrica do ganho da fusão** vs. modalidade única.
4. **Resultados obtidos e exemplos de anomalias detectadas** (métricas, prints, matriz de confusão, mAP).
5. **Seção de privacidade e segurança (LGPD)** — ver [07-privacidade-e-seguranca.md](07-privacidade-e-seguranca.md).
6. **Exemplo de relatório automático** gerado — ver [06-relatorios-automaticos.md](06-relatorios-automaticos.md).

> Sugestão: escrever o relatório dentro de `docs/relatorio-tecnico.md` e exportar para PDF.

## Tarefa 4.3 — Vídeo de demonstração (máx. 15 min)
Roteiro sugerido:
1. Apresentar o problema (acompanhamento no pós-parto) e a arquitetura (diagrama).
2. Mostrar a **análise do vídeo** rodando com o YOLO: detecção na **cicatriz da cesárea** e **pose** no exercício de fisioterapia.
3. Mostrar os **sinais vitais** (PA, FC, glicemia) sendo classificados pelo modelo.
4. Mostrar o **áudio** sendo transcrito/classificado e o **texto/laudo** sendo analisado.
5. **O momento da fusão:** ex.: cicatriz com sinal de infecção **+** PA alta/relato de febre → **alerta vermelho** em tempo real para a equipe.
6. Mostrar o **relatório automático** gerado para o caso.
7. Mostrar a **integração Azure** (upload no Blob, serviço na nuvem).
8. Encerrar com o **fluxo do alerta** chegando ao dashboard.
- Publicar como **"Não listado"** no YouTube/Vimeo e colocar o link no README.

---

## Sugestão de divisão de tarefas no grupo
| Frente | Responsável sugerido |
|--------|----------------------|
| Vídeo / YOLO (cicatriz + fisioterapia/pose) | 1 pessoa |
| Sinais vitais + fusão + métricas | 1 pessoa |
| Áudio + texto/NLP | 1 pessoa |
| Backend Node + Azure + tempo real + relatórios | 1 pessoa |
| Privacidade/LGPD + relatório técnico + vídeo | rodízio / todos |

> Ajuste conforme o tamanho do grupo. Integração e relatório são responsabilidade coletiva.
