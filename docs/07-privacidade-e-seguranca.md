# Privacidade e Segurança (LGPD)

> O PDF exige "os mais altos padrões de privacidade e segurança para dados sensíveis". Dados de saúde são **dados sensíveis** pela LGPD (Lei 13.709/2018). Esta seção precisa aparecer no relatório técnico.

## 1. Princípios adotados
- **Minimização:** coletar/usar apenas o necessário para o caso.
- **Anonimização/pseudonimização:** remover identificadores diretos (nome, CPF, prontuário) antes do processamento; usar `case_id` opaco.
- **Finalidade:** dados usados só para o monitoramento clínico.
- **Apoio à decisão, não diagnóstico:** a solução assiste a equipe; a decisão é humana.

## 2. Controles técnicos

| Camada | Controle |
|--------|----------|
| Em trânsito | HTTPS/TLS em todas as chamadas (Node ↔ Python ↔ Azure) |
| Em repouso | Criptografia do Azure Blob (server-side encryption) |
| Segredos | **Azure Key Vault** ou `.env` (nunca no Git); `.gitignore` cobrindo credenciais |
| Acesso | **RBAC** no Azure; SAS tokens com expiração para o Blob |
| Rede | Restringir origem das chamadas ao serviço Python (não expor publicamente sem auth) |
| Auditoria | Log de quem acessou qual caso e quando |
| Retenção | Política de expiração/limpeza de dados após o uso |

## 3. Dados no repositório Git
- **Nunca** versionar dados reais de pacientes.
- `data/` e `.env` no `.gitignore`.
- Usar apenas **dados sintéticos/abertos** no repositório de demonstração.
- Pesos de modelo grandes via **Git LFS** (não dados clínicos).

## 4. Dados sintéticos como estratégia de privacidade
Usar dados sintéticos (PA sincronizada, áudios em TTS) **resolve dois problemas de uma vez**: viabiliza a demonstração e elimina o risco de expor paciente real. Cite isso como decisão de privacidade no relatório.

## 5. Disclaimer ético (incluir no README e no relatório)
> Esta é uma solução acadêmica de **apoio à decisão clínica**. Não realiza diagnóstico nem substitui a avaliação de profissionais de saúde. Não deve ser usada em ambiente real sem validação clínica e regulatória adequada.

## 6. Checklist de conformidade
- [ ] Nenhum dado real de paciente no repositório
- [ ] Credenciais fora do código (Key Vault / `.env`)
- [ ] HTTPS/TLS nas integrações
- [ ] Blob com criptografia + SAS token com expiração
- [ ] Disclaimer ético visível
- [ ] Seção de privacidade/LGPD no relatório técnico
