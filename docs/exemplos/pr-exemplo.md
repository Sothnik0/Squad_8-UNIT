# Exemplo de Pull Request preenchido

Este exemplo usa a issue #12 como referência para demonstrar o padrão de Pull Requests do Verify.

## Resumo
Cria o template padrão de Pull Request do projeto Verify, a documentação de uso e um exemplo preenchido para orientar o squad.

## Issue relacionada
Closes #12

## Branch utilizada
`docs/pr-template`

## Alterações realizadas
- Criado o arquivo `.github/pull_request_template.md`
- Criado o arquivo `docs/pr-template.md`
- Criado o arquivo `docs/exemplos/pr-exemplo.md`
- Documentado como preencher cada campo do template de PR
- Incluído checklist de organização
- Incluído checklist antes de solicitar review

## Justificativa / argumentos
- Antes, o projeto não possuía um modelo formal para Pull Requests.
- Isso permitia PRs sem issue relacionada, sem validação, sem justificativa e sem metadados de organização.
- O novo template melhora a rastreabilidade entre issue, branch e PR.
- O checklist ajuda a lembrar assignee, labels e milestone.
- O campo de validação/evidência ajuda o squad a comprovar que a alteração foi testada ou revisada.
- O exemplo preenchido ajuda novos PRs a seguirem o padrão.

## Fora do escopo
- Não altera backend.
- Não altera frontend.
- Não altera prompts.
- Não altera banco de dados.
- Não altera o template de issue criado na #11.
- Não altera o documento de padrão de branches criado na #13.
- Não fecha a issue #10 diretamente.

## Validação / evidência
- Revisão manual dos arquivos criados.
- Verificação se o template solicita:
  - resumo;
  - issue relacionada;
  - branch utilizada;
  - alterações realizadas;
  - justificativa / argumentos;
  - fora do escopo;
  - validação / evidência;
  - riscos ou pontos de atenção;
  - checklist de organização;
  - checklist antes de solicitar review.
- Comparação com o estado anterior:
  - Antes: PRs podiam ser abertos sem modelo formal.
  - Depois: o projeto passa a ter um template oficial para abertura de Pull Requests.

## Riscos ou pontos de atenção
- Este PR cria apenas documentação e template.
- A adoção pelo squad depende de comunicação e das regras mínimas de contribuição da #14.
- Ainda não há CI configurado para validação automática dos PRs.

## Checklist de organização
- [x] PR referencia uma issue
- [x] Branch segue o padrão definido em `docs/padrao-branches.md`
- [x] PR possui responsável definido
- [x] PR possui labels coerentes
- [x] PR está vinculado à milestone correta
- [x] Mudanças estão dentro do escopo da issue
- [x] Mudanças fora do escopo foram justificadas, se existirem

## Checklist antes de solicitar review
- [x] Revisei meu próprio diff
- [x] Removi arquivos temporários ou desnecessários
- [x] Não expus chaves, tokens ou dados sensíveis
- [x] Descrevi a validação/evidência
- [x] Atualizei documentação quando necessário
- [x] O PR está pronto para revisão

## Observações
Este exemplo é baseado na criação do próprio template de PR do Verify.
