# Regras Mínimas de Contribuição

## Objetivo

Este documento define o fluxo mínimo para qualquer contribuição no projeto Verify, com foco em organização, rastreabilidade, revisão e controle de escopo.

O objetivo é ajudar o squad a trabalhar com um processo comum, simples e verificável, evitando alterações soltas no repositório e facilitando a relação entre issue, branch, commit, Pull Request, review e merge.

## Fluxo geral

O fluxo mínimo de contribuição do Verify é:

`Issue → Branch → Commit → Pull Request → Review → Merge`

Toda alteração relevante deve passar por esse fluxo, salvo casos pequenos ou ajustes combinados previamente pelo squad.

Esse fluxo ajuda a responder:

- qual problema motivou a alteração;
- qual branch foi usada;
- quais commits foram feitos;
- qual Pull Request entregou a mudança;
- como a alteração foi validada;
- quem revisou;
- quando a mudança foi integrada à `master`.

## 1. Antes de começar uma tarefa

Antes de alterar arquivos, o membro do squad deve:

- verificar se já existe uma issue relacionada;
- criar uma issue se a tarefa ainda não existir;
- usar o modelo padrão de issue quando aplicável;
- entender o escopo antes de alterar arquivos;
- evitar começar mudanças grandes sem alinhamento.

Se a necessidade for maior do que parecia inicialmente, a tarefa deve ser discutida e, se necessário, dividida em sub-issues.

## 2. Issues

Toda mudança relevante deve estar vinculada a uma issue.

A issue deve ter:

- tipo da issue: independente, guarda-chuva ou sub-issue;
- branch sugerida para a tarefa;
- arquivos previstos, quando o escopo já for conhecido;
- contexto ou problema atual;
- objetivo da issue;
- critérios observáveis de conclusão.

Se precisar alterar algum arquivo fora dos previstos, registre a justificativa no PR.

Sub-issues devem ser usadas quando uma tarefa fizer parte direta de uma issue maior. Issues guarda-chuva devem agrupar objetivos maiores e acompanhar a conclusão das tarefas relacionadas.

O título de issues deve seguir o padrão visual usado no projeto, quando aplicável:

- `[DOCS] ...`
- `[GESTÃO] ...`
- `[IA] ...`
- `[BACKEND] ...`
- `[FRONTEND] ...`
- `[QA] ...`

Esse prefixo visual indica a área principal da issue e ajuda o squad a identificar rapidamente o tipo de trabalho.

## 3. Branches

Toda alteração relevante deve ser feita em branch própria.

A branch deve:

- ser criada a partir da `master` atualizada;
- seguir o padrão `tipo/resumo-curto`;
- usar letras minúsculas;
- usar hífen entre palavras;
- não usar espaços;
- não usar acentos;
- não usar nomes genéricos.

Exemplos:

- `docs/regras-contribuicao`
- `backend/cadastro-documentos`
- `frontend/tela-upload`
- `ai/classificacao-risco`
- `prompt/revisar-validacao-atestado`
- `fix/corrigir-login`

O prefixo da branch não significa obrigatoriamente uma pasta do projeto. Por exemplo, a branch `backend/cadastro-documentos` não exige a criação de uma pasta chamada `backend/cadastro-documentos`; ela apenas indica a linha de trabalho no Git.

Antes de criar branch, consulte o padrão de branches definido no projeto.

## 4. Commits

O projeto usa uma versão simplificada baseada em Conventional Commits.

Formato:

`tipo: descrição curta da alteração`

Exemplos:

- `docs: adicionar regras mínimas de contribuição`
- `backend: criar endpoint de documentos`
- `frontend: ajustar tela de upload`
- `ai: documentar critérios de análise`
- `prompt: revisar prompt de validação`
- `fix: corrigir erro na configuração`
- `chore: remover arquivos desnecessários`

Commits não precisam fechar issues diretamente.

O fechamento da issue deve acontecer preferencialmente no Pull Request usando:

`Closes #número-da-issue`

Exemplo:

`Closes #14`

Os commits devem permanecer dentro do escopo da issue e da branch em desenvolvimento.

## 5. Pull Requests

Todo Pull Request deve usar o template padrão do projeto.

O PR deve:

- resumo do que foi entregue;
- issue relacionada, usando `Closes #` quando resolver tudo ou apenas `#` quando for parcial;
- lista do que mudou por arquivo;
- justificativa da mudança, explicando antes → depois → por que é melhor;
- descrição de como a mudança foi validada.

Quando o PR resolver completamente uma issue, use:

`Closes #número-da-issue`

O título do PR deve seguir o padrão visual usado no projeto, como:

`[GESTÃO] Definir regras mínimas de contribuição`

Quando o projeto estiver usando títulos com colchetes, não use o padrão de commit como título do PR. O padrão de commit deve ficar nas mensagens de commit.

## 6. Assignee, labels e milestone

Issues e PRs devem ser organizados com:

- assignee responsável;
- labels coerentes;
- milestone correta, quando aplicável.

Antes de finalizar a criação de uma issue ou PR, confira se assignee, labels e milestone foram definidos corretamente.

Esses metadados ajudam a identificar responsabilidade, prioridade, área da tarefa e relação com a entrega ou reunião planejada.

## 7. Validação e evidência

Toda alteração deve informar como foi validada.

Exemplos de evidência:

- print;
- log;
- teste executado;
- caminho do arquivo criado;
- comparação antes/depois;
- revisão manual;
- confirmação de que apenas arquivos dentro do escopo foram alterados.

Para mudanças apenas documentais, a validação pode ser feita por revisão manual e conferência dos arquivos criados.

Para mudanças em código, frontend, backend, banco, IA, OCR ou prompt, a validação deve explicar o comportamento testado e, sempre que possível, comparar antes e depois.

## 8. Review

Antes do merge, o reviewer deve conferir:

- se o PR resolve a issue relacionada;
- se a branch segue o padrão definido;
- se o título do PR segue o padrão visual do projeto;
- se os commits seguem o padrão definido;
- se as alterações estão dentro do escopo;
- se a validação/evidência é suficiente;
- se não há arquivos sensíveis ou alterações indevidas;
- se o PR pode ser aprovado ou mergeado.

O checklist do reviewer deve ser preenchido por quem revisa, não pelo autor.

O autor pode preencher os checklists de organização e preparação do PR, mas o reviewer deve conferir se os itens realmente foram cumpridos.

## 9. Merge

O merge só deve acontecer quando:

- o PR estiver pronto para review;
- o PR tiver sido revisado;
- não houver conflitos;
- a issue relacionada estiver clara;
- a validação estiver descrita;
- não houver alteração fora do escopo sem justificativa.

Issues devem ser fechadas preferencialmente pelo `Closes #...` no PR, e não por commits individuais.

Não faça merge se ainda houver dúvida sobre escopo, validação ou impacto da alteração.

## 10. Controle de escopo

Não misture tarefas diferentes no mesmo PR.

Evite alterar backend, frontend, banco, IA, prompt e documentação ao mesmo tempo sem necessidade clara.

Se surgir uma nova necessidade durante a tarefa, crie uma nova issue em vez de aumentar o escopo silenciosamente.

Alterações fora do escopo precisam ser justificadas no PR. Se forem grandes, devem virar outra issue e outro PR.

## 11. Cuidados com IA/OCR/prompt

Alterações em IA, OCR ou prompts exigem cuidado extra.

Sempre que possível, devem ter:

- problema anterior;
- justificativa da mudança;
- comparação antes/depois;
- exemplos de entrada e saída;
- evidência de validação;
- riscos conhecidos;
- limitações.

Mudanças em IA/OCR/prompt devem considerar a issue #15, porque esse tipo de alteração pode afetar qualidade, custo, consistência do output e confiança nos resultados do Verify.

## 12. Checklist rápido antes de abrir PR

- [ ] A tarefa tem issue relacionada
- [ ] A branch segue o padrão definido
- [ ] Os commits seguem o padrão definido
- [ ] O PR referencia a issue com `Closes #`, quando aplicável
- [ ] O que mudou está listado por arquivo
- [ ] A validação foi descrita
- [ ] As alterações estão dentro dos arquivos previstos na issue
- [ ] Não há arquivos sensíveis ou desnecessários

## Padrões relacionados

Antes de criar issue, branch, commit ou PR, consulte os padrões existentes do projeto:

- #11 — Modelo padrão de issue
- #12 — Modelo padrão de Pull Request
- #13 — Padrão de branches
- #20 — Padrão de commits
- #15 — Critérios para alterações em IA/OCR/prompt, quando aplicável

Esses padrões se complementam. Este documento funciona como guia consolidado do fluxo mínimo de contribuição.
