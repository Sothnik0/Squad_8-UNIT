# Modelo padrão de issues do Verify

Este documento descreve o modelo padrão de issues do projeto Verify. O objetivo é ajudar o squad a criar tarefas claras, rastreáveis e bem delimitadas, reduzindo retrabalho e evitando mudanças fora do escopo combinado.

Novas issues devem explicar o problema, o objetivo, a alteração proposta, os arquivos ou áreas afetadas, os critérios de aceite e a forma de validação. Quando houver alteração no repositório, a issue também deve indicar uma branch de trabalho criada a partir da `master`.

## Natureza da issue

Use este campo para indicar se a issue é independente, guarda-chuva ou sub-issue de uma tarefa maior.

- Issue independente: resolve uma tarefa isolada.
- Issue guarda-chuva: agrupa tarefas relacionadas e depende de outras issues.
- Sub-issue: representa uma parte direta de uma issue maior.

Quando for sub-issue, informe o número da issue principal.

## Branch de trabalho

Este campo deve indicar a branch usada para implementar a tarefa quando houver alteração no repositório.

A branch deve ser criada a partir da `master` atualizada e seguir o padrão definido pelo projeto, como:

`tipo/resumo-curto`

Exemplo:

`docs/issue-template`

Se a issue não exigir alteração no repositório, escreva `Não se aplica`.

## Arquivos ou áreas afetadas

Este campo ajuda a deixar claro onde a tarefa deve mexer. Ele reduz o risco de alterações fora do escopo e facilita a revisão do Pull Request.

Informe arquivos, pastas ou áreas como:

- `.github/ISSUE_TEMPLATE/...`
- `docs/...`
- `backend/...`
- `frontend/...`
- `prompts/...`
- banco de dados
- regras de IA/OCR

Se ainda não for possível saber exatamente, escreva `A definir durante a execução` e detalhe melhor no PR.

## Alteração proposta

Explique objetivamente o que será criado, alterado, removido ou documentado. Este campo deve descrever a mudança prática que será feita nos arquivos ou áreas afetadas.

## Descrição

Resuma a tarefa em linguagem direta. A descrição deve permitir que qualquer pessoa do squad entenda o que precisa ser feito sem depender de conversas externas.

## Contexto / problema atual

Explique o cenário atual, o problema percebido ou a necessidade que motivou a issue.

Este campo deve responder perguntas como:

- O que acontece hoje?
- Qual problema isso causa?
- Por que essa tarefa passou a ser necessária?

## Objetivo

Explique o resultado esperado ao concluir a issue. O objetivo deve ser específico o suficiente para orientar a implementação e a revisão.

## Justificativa da melhoria

Este campo deve explicar por que a mudança proposta melhora o estado atual.

Sempre que a issue representar uma melhoria, compare com o cenário anterior. Evite dizer apenas que algo "melhorou"; explique o motivo.

Exemplos de justificativa:

- reduz retrabalho;
- melhora rastreabilidade;
- reduz erros;
- melhora clareza;
- facilita manutenção;
- melhora a organização do projeto;
- melhora a validação dos resultados;
- reduz risco de alterações fora do escopo.

## Fora do escopo

Liste explicitamente o que não deve ser feito nesta issue.

Este campo ajuda a evitar mudanças oportunistas, refatorações não combinadas e alterações em partes não relacionadas.

Exemplos:

- Não alterar backend.
- Não alterar frontend.
- Não alterar prompts.
- Não modificar banco de dados.
- Não fechar issue guarda-chuva relacionada.

## Tarefas

Liste os passos necessários para concluir a issue. Use checkboxes para facilitar acompanhamento.

Cada tarefa deve ser objetiva e verificável.

## Critérios de aceite

Defina como saber que a issue foi concluída corretamente.

Os critérios de aceite devem ser observáveis. Evite critérios vagos como "ficar melhor" sem explicar como isso será avaliado.

## Validação / evidência

Este campo deve provar que a entrega funcionou e que a mudança ficou melhor do que o estado anterior.

Quando houver mudança em IA, OCR, prompt, código, banco, frontend ou backend, compare antes e depois sempre que possível.

Exemplos de evidência:

- link do PR;
- arquivo criado;
- teste executado;
- print da tela;
- comparação antes/depois;
- exemplo de output anterior e novo;
- resposta JSON validada;
- comportamento funcionando no Swagger, navegador ou terminal.

Para tarefas apenas documentais, a validação pode ser feita por revisão manual do conteúdo e conferência dos arquivos criados.

## Dependências

Informe se a issue depende de outra tarefa ou bloqueia outra issue.

Exemplos:

- Depende de: #10, porque faz parte da organização geral do fluxo.
- Bloqueia: #12, porque o template de PR depende deste padrão.

Se não houver dependência, escreva:

- Depende de: não se aplica
- Bloqueia: não se aplica

## Observações

Use este campo para registrar dúvidas, decisões tomadas, pontos de atenção ou limitações conhecidas.

## Boas práticas

- Abra issues com escopo claro.
- Indique branch de trabalho quando houver alteração no repositório.
- Informe arquivos ou áreas afetadas.
- Explique o estado atual antes de propor melhoria.
- Registre o que está fora do escopo.
- Defina critérios de aceite verificáveis.
- Inclua evidência de validação ao finalizar a tarefa.
