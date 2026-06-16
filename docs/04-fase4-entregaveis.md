# Fase 4 — Empacotamento e Entregáveis

> Objetivo: empacotar a solução com **padrão de engenharia de software** e produzir os 3 entregáveis avaliados: **Repositório Git**, **Relatório técnico** e **Vídeo**.

## Resultado esperado (Definition of Done)
- [ ] Repositório organizado, com `README.md` e `requirements.txt`/`package.json`.
- [ ] Relatório técnico completo.
- [ ] Vídeo de até 15 min publicado (YouTube/Vimeo, público ou não listado).

---

## Tarefa 4.1 — Repositório Git
- Estrutura em pastas (ver seção 6 do [plano mestre](../PLANO_DE_DESENVOLVIMENTO.md)): `/ai-service`, `/backend`, `/docs`, `/scripts`.
- `requirements.txt` (Python) e `package.json` (Node) com versões fixadas.
- `README.md` com **instruções de execução** claras (como instalar, configurar `.env`, rodar cada serviço).
- `.gitignore` cobrindo `data/`, `.env`, pesos grandes (ou usar **Git LFS**).

## Tarefa 4.2 — Relatório técnico
Deve conter (conforme o PDF):
1. **Descrição do fluxo multimodal** (diagrama de arquitetura).
2. **Modelos aplicados em cada tipo de dado** (vídeo, áudio, sinais vitais) e justificativa das escolhas (por que YOLOv8, por que Random Forest/Isolation Forest).
3. **Lógica de fusão** (motor de regras).
4. **Resultados obtidos e exemplos de anomalias detectadas** (métricas, prints, matriz de confusão, mAP).

> Sugestão: escrever o relatório dentro de `docs/relatorio-tecnico.md` e exportar para PDF.

## Tarefa 4.3 — Vídeo de demonstração (máx. 15 min)
Roteiro sugerido:
1. Apresentar o problema e a arquitetura (diagrama).
2. Mostrar o **vídeo cirúrgico** rodando com a detecção do YOLO.
3. Mostrar os **gráficos de sinais vitais** oscilando ao lado.
4. Mostrar o **áudio** sendo transcrito/classificado.
5. **O momento da fusão:** sangue detectado **+** queda de PA → **alerta vermelho** unificado para a equipe.
6. Mostrar a **integração Azure** (upload no Blob, serviço na nuvem).
7. Encerrar com o **fluxo do alerta** chegando ao dashboard.
- Publicar como **"Não listado"** no YouTube/Vimeo e colocar o link no README.

---

## Sugestão de divisão de tarefas no grupo
| Frente | Responsável sugerido |
|--------|----------------------|
| Vídeo / YOLO | 1 pessoa |
| Sinais vitais + fusão | 1 pessoa |
| Áudio | 1 pessoa |
| Backend Node + Azure | 1 pessoa |
| Relatório + vídeo | rodízio / todos |

> Ajuste conforme o tamanho do grupo. Integração e relatório são responsabilidade coletiva.
