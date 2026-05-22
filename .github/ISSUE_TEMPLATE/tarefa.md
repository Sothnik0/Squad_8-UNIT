---
name: Tarefa geral
about: Modelo padrão para criação de issues no projeto Verify
title: "[TIPO] Título objetivo da tarefa"
labels: ""
assignees: ""
---

## Natureza da issue
Que tipo de issue é?

- [ ] Issue independente
- [ ] Issue guarda-chuva
- [ ] Sub-issue de: #...

## Branch de trabalho
Onde vai trabalhar?

Crie uma branch a partir da `master` com o nome:

`tipo/resumo-curto`

Exemplo:
`docs/issue-template`

Caso esta issue não exija alteração no repositório, escreva:
Não se aplica.

## Arquivos ou áreas afetadas
Onde vai mexer?

Liste os arquivos, pastas ou áreas que devem ser alteradas.

- `backend/...`
- `frontend/...`
- `docs/...`
- `prompts/...`

Caso ainda não saiba exatamente:
A definir durante a execução.

## Alteração proposta
O que você vai mexer, criar, alterar, remover ou documentar?

Explique objetivamente quais mudanças serão feitas nos arquivos ou áreas afetadas.

## Descrição
O que vai fazer?

Explique de forma objetiva a tarefa desta issue.

## Contexto / problema atual
O que está acontecendo agora?

Explique o cenário atual, o problema percebido ou a necessidade que motivou esta issue.

## Objetivo
Onde você quer chegar?

Explique o resultado esperado ao concluir esta issue.

## Justificativa da melhoria
Por que essa mudança é melhor que o estado atual?

Explique o que torna a nova abordagem melhor do que a versão anterior.

Exemplos:
- reduz retrabalho;
- melhora rastreabilidade;
- reduz erros;
- melhora clareza;
- reduz custo;
- melhora consistência do output;
- facilita manutenção;
- melhora a organização do projeto;
- melhora a validação dos resultados;
- reduz risco de alterações fora do escopo.

## Fora do escopo
No que você não deve mexer?

Liste o que NÃO deve ser feito nesta issue.

- Não alterar partes não relacionadas
- Não modificar arquivos fora do escopo sem justificativa
- Não refatorar código sem necessidade
- Não alterar comportamento já funcional sem explicar o motivo

## Tarefas
Quais passos precisam ser feitos?

- [ ] Tarefa 1
- [ ] Tarefa 2
- [ ] Tarefa 3

## Critérios de aceite
Como saber que a issue terminou?

A issue só pode ser considerada concluída se:

- [ ] Critério 1
- [ ] Critério 2
- [ ] Critério 3

## Validação / evidência
Como provar que funcionou e que ficou melhor?

Sempre que houver mudança em código, IA, OCR, prompt, banco, frontend ou backend, registre uma evidência de validação.

A validação deve comparar, sempre que possível, o comportamento anterior com o comportamento novo.

Exemplos:
- teste executado;
- print da tela;
- link do PR;
- documento criado;
- comparação antes/depois;
- exemplo de output anterior e novo;
- resposta JSON validada;
- redução de erro;
- melhoria de clareza;
- redução de tokens/custo;
- comportamento funcionando no Swagger, navegador ou terminal.

## Dependências
Esta issue depende de algo ou bloqueia outra tarefa?

Exemplo:
- Depende de: #13, porque o padrão de branches precisa estar definido antes de criar templates.
- Bloqueia: #12, porque o template de PR depende das regras de contribuição.

Caso não se aplique:
- Depende de: não se aplica
- Bloqueia: não se aplica

## Observações
Adicione dúvidas, decisões tomadas ou pontos de atenção.
