# Modelo padrão de Pull Requests do Verify

Este documento explica como preencher o template de Pull Request do projeto Verify.

O objetivo é garantir que todo PR seja claro, rastreável e validável, permitindo que o squad entenda o que foi alterado, por que foi alterado, como foi validado e se está dentro do escopo da issue relacionada.

## Resumo

O resumo deve explicar rapidamente o que o PR entrega.

Exemplo:

`Cria o template padrão de Pull Request do projeto Verify.`

## Issue relacionada

Todo PR deve estar relacionado a uma issue.

Use `Closes #...` quando o PR resolver completamente a issue. Assim, quando o PR for mergeado, o GitHub fecha a issue automaticamente.

Exemplo:

`Closes #12`

Se o PR resolver apenas parte da issue, use:

`Relacionada à #12`

## Branch utilizada

Informe a branch usada no PR.

A branch deve seguir o padrão definido em `docs/padrao-branches.md`.

Exemplo:

`docs/pr-template`

## Alterações realizadas

Liste o que foi criado, alterado ou removido.

Esse campo deve ser objetivo e factual.

Exemplo:

- Criado o arquivo `.github/pull_request_template.md`
- Criado o documento `docs/pr-template.md`
- Criado o exemplo `docs/exemplos/pr-exemplo.md`

## Justificativa / argumentos

Explique por que a mudança faz sentido e por que ela melhora o estado anterior.

Esse campo evita PRs com justificativas vagas como "melhorei" ou "corrigi algumas coisas" sem explicar o motivo.

Sempre que possível, compare:

- Antes
- Depois
- Por que é melhor

## Fora do escopo

Liste o que o PR não altera.

Esse campo ajuda a evitar mudanças não combinadas e facilita a revisão.

Exemplo:

- Não altera backend.
- Não altera frontend.
- Não altera prompts.
- Não altera banco de dados.

## Validação / evidência

Explique como a mudança foi validada.

Para documentação, a validação pode ser revisão manual e conferência dos arquivos criados.

Para código, inclua testes executados, comandos usados, prints, comportamento no navegador, Swagger ou terminal.

Para IA, OCR ou prompt, sempre que possível, inclua comparação antes/depois, output validado, JSON gerado ou evidência de melhoria.

## Riscos ou pontos de atenção

Informe limitações, dúvidas ou cuidados que o revisor precisa saber.

Exemplo:

- Este PR cria apenas documentação; a adoção pelo squad depende das regras de contribuição.
- A validação foi manual porque ainda não existe CI configurado.
- A mudança não foi testada em ambiente hospedado.

## Checklist de organização

Antes de solicitar review, confirme:

- PR referencia uma issue.
- Branch segue o padrão definido.
- PR possui responsável.
- PR possui labels coerentes.
- PR está vinculado à milestone correta.
- Mudanças estão dentro do escopo da issue.

## Checklist antes de solicitar review

Antes de marcar o PR como pronto para revisão, confirme:

- O diff foi revisado.
- Arquivos temporários foram removidos.
- Nenhum token, chave ou dado sensível foi exposto.
- A validação foi descrita.
- A documentação foi atualizada quando necessário.

## Boas práticas

- Não misture várias tarefas não relacionadas no mesmo PR.
- Não altere arquivos fora do escopo sem justificar.
- Evite PRs com descrições genéricas.
- Sempre explique o que mudou e por que mudou.
- Sempre registre como validou a alteração.
- Se o PR depende de outro, informe nos riscos ou observações.
