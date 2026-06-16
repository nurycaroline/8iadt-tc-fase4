# Checklist de Entrega

Use este checklist antes de submeter. Cada item corresponde a algo avaliado.

## Pré-requisitos de ferramentas
- [ ] Python: `fastapi`, `uvicorn`, `ultralytics`, `pandas`, `scikit-learn`, `opencv-python`, `joblib`
- [ ] Node.js: `express`, `axios`, `dotenv`, SDK do Azure Storage
- [ ] Conta Azure ativa + Blob Storage testado (upload via código funciona)
- [ ] (Áudio) Whisper ou Azure Speech configurado

## Escopo (requisitos do PDF)
- [ ] Pelo menos **2 funcionalidades** implementadas
- [ ] Pelo menos **3 objetivos** atendidos
- [ ] **Análise de vídeo** com YOLOv8 customizado ✅ obrigatório
- [ ] **Análise de áudio** especializada ✅ obrigatório
- [ ] Detecção de anomalias em **tempo real**
- [ ] Integração com **nuvem (Azure)**

## Técnico
- [ ] 3 modelos funcionando individualmente com **métricas**
- [ ] **Motor de fusão** retornando o JSON padronizado
- [ ] Pipeline **ponta-a-ponta** (upload → IA → alerta) testado
- [ ] Tratamento de **privacidade** (sem dados reais de paciente no Git, `.env`)

## Repositório Git
- [ ] Estrutura em pastas (`/ai-service`, `/backend`, `/docs`, `/scripts`)
- [ ] `requirements.txt` e `package.json` com versões
- [ ] `README.md` com instruções de execução
- [ ] `.gitignore` (data, .env, pesos grandes ou Git LFS)

## Relatório técnico
- [ ] Descrição do fluxo multimodal (diagrama)
- [ ] Modelos por tipo de dado + justificativas
- [ ] Lógica de fusão explicada
- [ ] Resultados/métricas + exemplos de anomalias detectadas

## Vídeo (máx. 15 min)
- [ ] Demonstra análise de áudio **e** vídeo
- [ ] Mostra detecção e resposta a anomalias
- [ ] Mostra integração Azure
- [ ] Mostra o fluxo final do alerta à equipe médica
- [ ] Publicado no YouTube/Vimeo (público ou **não listado**)
- [ ] Link do vídeo no README

## Antes de submeter
- [ ] Rodar o pipeline limpo do zero seguindo só o README
- [ ] Conferir que tudo está commitado e no repositório
- [ ] Revisar nome dos integrantes e créditos
