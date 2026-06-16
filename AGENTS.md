# AGENTS.md

Este documento define as diretrizes e boas práticas que **todo agente de IA** deve
seguir ao trabalhar neste repositório. O objetivo é garantir trabalho previsível,
seguro e de alta qualidade.

> Observação: o nome de arquivo `AGENTS.md` é a convenção reconhecida por ferramentas
> de agentes (Cursor, entre outras). Mantenha este arquivo na raiz do projeto.

---

## Princípios Fundamentais

### 1. Em caso de dúvida, pergunte. Nunca presuma.

- Se houver **qualquer ambiguidade** sobre requisitos, escopo, comportamento esperado
  ou decisões de arquitetura, **pergunte antes de prosseguir**.
- **Nunca invente** comportamentos, APIs, valores, nomes de arquivos ou dependências
  que não estejam confirmados. Não "preencha lacunas" com suposições.
- Prefira fazer uma pergunta objetiva a entregar algo errado.
- Se uma instrução conflitar com o código existente ou com este documento, **sinalize
  o conflito** em vez de escolher silenciosamente um dos lados.

### 2. Delegue tarefas a subagentes para manter o contexto limpo.

- Sempre que possível, **delegue tarefas isoláveis a subagentes** (ex.: exploração
  ampla do código, buscas extensas, pesquisas independentes), para **não poluir o
  contexto principal**.
- Use subagentes para trabalho paralelizável e de exploração; reserve o contexto
  principal para decisões, planejamento e integração dos resultados.
- Cada subagente deve receber uma instrução **autocontida e detalhada**, pois não tem
  acesso ao histórico da conversa principal.
- Peça aos subagentes apenas o **resultado essencial** de volta, evitando trazer
  ruído desnecessário ao contexto.

### 3. Sempre use versões atualizadas.

- Ao adicionar dependências, use a **versão estável mais recente** disponível através
  do gerenciador de pacotes (npm, pip, etc.). **Não invente** números de versão.
- Consulte a documentação **atual** das bibliotecas e frameworks antes de usá-los;
  o conhecimento prévio pode estar desatualizado.
- Evite APIs e padrões depreciados. Prefira as abordagens recomendadas na versão atual.
- Mantenha as ferramentas de build, runtime e CI em versões suportadas.

### 4. Siga boas práticas de desenvolvimento.

- **Respeite as convenções existentes** do projeto (estilo, estrutura, nomenclatura,
  padrões de arquitetura). Leia o código vizinho antes de editar.
- Escreva código **claro e legível**. Evite comentários que apenas narram o óbvio;
  comente apenas intenção, restrições ou trade-offs não evidentes.
- Faça **mudanças pequenas e coesas**. Um commit por mudança lógica, com mensagens
  descritivas.
- **Não faça** `force push` nem `amend` de commits, a menos que explicitamente solicitado.
- Garanta que **lint e testes passem** antes de considerar a tarefa concluída.
- Trate erros adequadamente e não deixe código morto ou artefatos temporários.
- Não exponha segredos. Nunca faça commit de credenciais; use variáveis de ambiente.
- Prefira soluções simples e diretas; evite complexidade e abstrações prematuras.

### 5. Atualize a documentação quando necessário.

- Ao alterar comportamento, APIs, configuração ou fluxos de uso, **atualize a
  documentação correspondente** (README, comentários relevantes, docs do projeto).
- Mantenha exemplos e instruções de setup **sincronizados** com o estado real do código.
- Documente decisões importantes e mudanças que afetem outros desenvolvedores/agentes.
- Não crie documentação desnecessária; documente o que agrega valor real.

---

## Fluxo de Trabalho Recomendado

1. **Entenda** a tarefa e o contexto. Em caso de dúvida, **pergunte** (Princípio 1).
2. **Explore** o código necessário, delegando buscas amplas a subagentes (Princípio 2).
3. **Planeje** as mudanças em passos pequenos e verificáveis.
4. **Implemente** seguindo as convenções e boas práticas (Princípio 4), usando versões
   atualizadas (Princípio 3).
5. **Valide** com lint e testes.
6. **Documente** o que mudou (Princípio 5).
7. **Comite e envie** com mensagens claras, um commit por mudança lógica.

---

## Checklist Antes de Concluir

- [ ] Todas as dúvidas relevantes foram esclarecidas (nada foi presumido).
- [ ] Tarefas isoláveis foram delegadas a subagentes quando fazia sentido.
- [ ] Dependências e ferramentas estão em versões atualizadas e suportadas.
- [ ] O código segue as convenções e boas práticas do projeto.
- [ ] Lint e testes passam.
- [ ] A documentação afetada foi atualizada.
- [ ] As mudanças foram commitadas e enviadas com mensagens descritivas.
