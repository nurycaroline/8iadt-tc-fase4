# Relatórios Automáticos Especializados

> Requisito explícito do PDF ("Relatórios automáticos especializados"). Cada caso analisado deve gerar um **relatório clínico estruturado**, derivado do JSON de fusão, pronto para a equipe médica.

> ✅ **Implementado** em [`ai-service/app/relatorio.py`](../ai-service/app/relatorio.py) (gerado pelo pipeline da Fase 3) e **especializado na Fase 6**: encaminhamento por tipo de risco (§4), anexos com links reais dos artefatos (§5), PDF com fallback HTML (§5) e pré-visualização no dashboard. Detalhes em [`docs/09-fase6-relatorios-automaticos.md`](09-fase6-relatorios-automaticos.md).

## 1. Por que é um componente próprio
O enunciado lista relatórios automáticos como entrega técnica, com 4 tipos de conteúdo:
- Desvios em procedimentos/acompanhamento obstétrico;
- Sinais de complicações no puerpério (ex.: infecção da cicatriz, pré-eclâmpsia);
- Indicadores de desconforto psicológico (depressão pós-parto/ansiedade);
- Alertas para possíveis casos de violência doméstica.

Por isso, não é só "logar o resultado": é gerar um **documento legível** por caso.

## 2. Entrada e saída
- **Entrada:** o JSON de risco produzido pela fusão (ver [contrato-api.md](contrato-api.md)).
- **Saída:** relatório em **Markdown → PDF** (e/ou HTML no dashboard), salvo no Azure Blob junto com os frames de alerta.

## 3. Estrutura do relatório (template)

```
RELATÓRIO DE MONITORAMENTO MULTIMODAL — Caso {case_id}
Paciente: {primeiro_nome}, {idade} anos {— gestante, {idade_gestacional} sem (se aplicável)}
Data/hora: {timestamp}
Nível de risco: {BAIXO | MÉDIO | ALTO}

1. RESUMO EXECUTIVO
   {mensagem_alerta}

2. EVIDÊNCIAS POR MODALIDADE
   - Vídeo (cicatriz):  {evento} (confiança {x}) — imagem anexa
   - Sinais vitais:     {tipo} (valor {y}) — gráfico anexo
   - Áudio:             {categoria} (confiança {z}) — trecho/transcrição
   - Texto/laudo:       {achados de NLP}

3. CLASSIFICAÇÃO E GATILHOS ACIONADOS
   {quais limiares foram cruzados — ex.: PA≥140/90, cicatriz com sinal de infecção}

4. RECOMENDAÇÃO / ENCAMINHAMENTO
   {ação sugerida conforme o nível de risco}

5. ANEXOS
   {links Blob: frame, gráfico, áudio}

AVISO: Documento de apoio à decisão clínica. Não substitui avaliação médica.
```

## 4. Geração por tipo de risco
| Tipo de relatório | Disparado quando | Conteúdo-chave |
|-------------------|------------------|----------------|
| Infecção puerperal | cicatriz com sinal de infecção + febre/dor relatada | risco de infecção da cesárea |
| Risco materno / pré-eclâmpsia | sinais vitais de risco (PA alta) + cefaleia/proteinúria | risco hipertensivo |
| Desconforto psicológico | áudio=ansiedade/depressão pós-parto | encaminhamento psicológico |
| Violência doméstica | áudio/texto=violência | protocolo de proteção |

## 5. Implementação sugerida
- Função `gerar_relatorio(json_fusao) -> markdown` no serviço Python.
- Conversão Markdown→PDF (ex.: `weasyprint`, `markdown-pdf`).
- Salvar no Azure Blob e referenciar a URL no JSON de resposta.
- Exibir no dashboard com botão "baixar PDF".

> Demonstre a geração desse relatório no **vídeo final** — é uma evidência direta de um requisito atendido.
