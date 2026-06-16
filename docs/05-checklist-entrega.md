# Checklist de Entrega

Use este checklist antes de submeter. Cada item corresponde a algo avaliado.

## Pré-requisitos de ferramentas
- [ ] Python: `fastapi`, `uvicorn`, `ultralytics`, `pandas`, `scikit-learn`, `opencv-python`, `joblib`, `pytest`
- [ ] Node.js: `express`, `axios`, `dotenv`, `socket.io` (tempo real), SDK do Azure Storage, `jest`
- [ ] Conta Azure ativa + Blob Storage testado (upload via código funciona)
- [ ] (Áudio) Whisper ou Azure Speech configurado
- [ ] (Texto) Azure Text Analytics ou classificador de NLP configurado
- [ ] Docker + docker-compose instalados

## Escopo (requisitos do PDF)
- [ ] Pelo menos **2 funcionalidades** implementadas
- [ ] Pelo menos **3 objetivos** atendidos
- [ ] **Análise de vídeo** com YOLOv8 customizado ✅ obrigatório
- [ ] **Análise de áudio** especializada ✅ obrigatório
- [ ] **Relatórios automáticos especializados** ✅ obrigatório
- [ ] Modalidade **texto** (laudos/prescrições/evolução) contemplada
- [ ] Detecção de anomalias em **tempo real**
- [ ] Integração com **nuvem (Azure)**

## Técnico
- [ ] 4 modelos funcionando individualmente com **métricas**
- [ ] **Motor de fusão** retornando o JSON padronizado
- [ ] **Métrica do ganho da fusão** vs. modalidade única
- [ ] **Alerta em tempo real** (WebSocket/SSE) no dashboard
- [ ] **Relatório automático** gerado por caso
- [ ] Pipeline **ponta-a-ponta** (upload → IA → alerta) testado
- [ ] Tratamento de **privacidade/LGPD** (sem dados reais no Git, `.env`/Key Vault)

## Qualidade de engenharia
- [ ] `docker compose up` sobe a stack
- [ ] Testes do **motor de fusão** passando (`pytest`)
- [ ] **CI** (GitHub Actions) verde no PR
- [ ] Logging com `case_id` rastreável

## Repositório Git
- [ ] Estrutura em pastas (`/ai-service`, `/backend`, `/docs`, `/scripts`)
- [ ] `requirements.txt` e `package.json` com versões
- [ ] `README.md` com instruções de execução
- [ ] `.gitignore` (data, .env, pesos grandes ou Git LFS)
- [ ] **Disclaimer ético** visível

## Relatório técnico
- [ ] Descrição do fluxo multimodal (diagrama)
- [ ] Modelos por tipo de dado + justificativas
- [ ] Lógica de fusão explicada + **métrica do ganho**
- [ ] Resultados/métricas + exemplos de anomalias detectadas
- [ ] Seção de **privacidade/LGPD**

## Vídeo (máx. 15 min)
- [ ] Demonstra análise de áudio **e** vídeo (e texto)
- [ ] Mostra detecção e resposta a anomalias em tempo real
- [ ] Mostra o **relatório automático** gerado
- [ ] Mostra integração Azure
- [ ] Mostra o fluxo final do alerta à equipe médica
- [ ] Publicado no YouTube/Vimeo (público ou **não listado**)
- [ ] Link do vídeo no README

## Antes de submeter
- [ ] Rodar o pipeline limpo do zero seguindo só o README
- [ ] Conferir que tudo está commitado e no repositório
- [ ] Revisar nome dos integrantes e créditos
