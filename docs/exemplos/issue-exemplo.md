# Exemplo de issue preenchida

Este exemplo usa a issue #11 como referência para demonstrar o padrão de descrição de issues do Verify.

## Natureza da issue

- [ ] Issue independente
- [ ] Issue guarda-chuva
- [x] Sub-issue de: #10

## Branch de trabalho

Crie uma branch a partir da `master` com o nome:

`docs/issue-template`

## Arquivos ou áreas afetadas

- `.github/ISSUE_TEMPLATE/tarefa.md`
- `docs/issue-template.md`
- `docs/exemplos/issue-exemplo.md`

## Alteração proposta

Criar um template geral de issue para o GitHub, uma documentação explicando como preencher o modelo e um exemplo preenchido para orientar o squad.

## Descrição

Criar um modelo padrão de issue para orientar o squad na abertura de novas tarefas do projeto Verify.

## Contexto / problema atual

Atualmente o projeto não possui um modelo formal para criação de issues. Isso permite que tarefas sejam criadas sem escopo claro, sem branch definida, sem arquivos afetados indicados, sem critérios de aceite objetivos e sem evidência de validação.

Além disso, algumas alterações podem ser descritas como melhorias sem comparação clara com o estado anterior, dificultando avaliar se a nova versão realmente ficou melhor.

## Objetivo

Padronizar a criação de issues no projeto Verify, garantindo que toda tarefa tenha contexto, escopo, branch de trabalho, arquivos ou áreas afetadas, justificativa da melhoria, critérios de aceite e validação.

## Justificativa da melhoria

Esse modelo melhora o estado atual porque:

- reduz issues vagas;
- facilita a revisão das tarefas;
- melhora a rastreabilidade entre issue, branch e PR;
- evita alterações fora do escopo;
- orienta o squad a explicar o que existia antes, o que será alterado e por que a mudança é melhor;
- exige evidência de validação para comprovar a entrega;
- ajuda a manter o projeto organizado até a entrega final.

## Fora do escopo

- Não criar template de Pull Request nesta issue.
- Não definir oficialmente todos os padrões de branch nesta issue.
- Não alterar código do backend.
- Não alterar código do frontend.
- Não alterar prompts ou regras de IA.
- Não modificar banco de dados.
- Não fechar a issue #10.

## Tarefas

- [ ] Criar arquivo `.github/ISSUE_TEMPLATE/tarefa.md`
- [ ] Criar arquivo `docs/issue-template.md`
- [ ] Criar arquivo `docs/exemplos/issue-exemplo.md`
- [ ] Incluir campo de natureza da issue
- [ ] Incluir campo de branch de trabalho
- [ ] Incluir campo de arquivos ou áreas afetadas
- [ ] Incluir campo de alteração proposta
- [ ] Incluir campo de descrição
- [ ] Incluir campo de contexto/problema atual
- [ ] Incluir campo de objetivo
- [ ] Incluir campo de justificativa da melhoria
- [ ] Incluir campo de fora do escopo
- [ ] Incluir campo de tarefas
- [ ] Incluir campo de critérios de aceite
- [ ] Incluir campo de validação/evidência
- [ ] Incluir campo de dependências
- [ ] Incluir campo de observações

## Critérios de aceite

A issue só pode ser considerada concluída se:

- [ ] O template geral de issue estiver criado no repositório.
- [ ] O documento explicando o uso do template estiver criado em `docs/issue-template.md`.
- [ ] O exemplo preenchido estiver criado em `docs/exemplos/issue-exemplo.md`.
- [ ] O template orientar o uso de branch de trabalho.
- [ ] O template orientar a definição de arquivos ou áreas afetadas.
- [ ] O template orientar a comparação com o estado anterior sempre que houver melhoria.
- [ ] O template orientar a validação por evidência.
- [ ] O template deixar claro o que está fora do escopo da tarefa.
- [ ] O template puder ser usado por qualquer membro do squad ao criar uma nova issue.

## Validação / evidência

A validação será feita por revisão manual do Pull Request que implementar esta issue.

Comparação com o estado anterior:

- Antes: issues podiam ser criadas sem padrão formal.
- Depois: o projeto terá um template oficial para orientar a criação de issues.

Evidências esperadas:

- Link do PR criado.
- Arquivo `.github/ISSUE_TEMPLATE/tarefa.md` presente.
- Arquivo `docs/issue-template.md` presente.
- Arquivo `docs/exemplos/issue-exemplo.md` presente.
- Conteúdo revisado manualmente.

## Dependências

- Depende de: #10, porque esta issue faz parte da organização geral do fluxo de desenvolvimento.
- Bloqueia: #12, porque o modelo de issue ajuda a orientar o modelo de Pull Request.
- Bloqueia parcialmente: #14, porque as regras mínimas de contribuição devem considerar o modelo de issue criado aqui.

## Observações

Esta issue é a primeira aplicação prática do novo padrão de descrição de issues.

O template de Pull Request ainda não existe, então o PR desta tarefa deve usar um modelo provisório, descrevendo resumo, issue relacionada, branch utilizada, alterações realizadas, fora do escopo, validação/evidência e observações.
