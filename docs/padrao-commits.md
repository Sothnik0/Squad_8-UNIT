# Padrão de Commits

## Objetivo

O projeto Verify utiliza uma versão simplificada baseada em Conventional Commits para manter o histórico do repositório mais claro, rastreável e fácil de revisar.

Esse padrão ajuda o squad a entender rapidamente o que cada commit alterou, reduz mensagens genéricas e melhora a relação entre issue, branch, commit e Pull Request.

## Formato recomendado

Use o formato:

`tipo: descrição curta da alteração`

Nesse formato:

- o tipo indica a área ou natureza da alteração;
- a descrição deve ser curta e objetiva;
- a descrição deve indicar claramente o que foi feito;
- deve-se evitar ponto final;
- deve-se evitar mensagens genéricas.

## Tipos recomendados

- `docs`: alterações em documentação
- `backend`: alterações no backend
- `frontend`: alterações no frontend
- `database`: alterações relacionadas ao banco de dados
- `ai`: alterações relacionadas à IA, OCR, classificação ou validação inteligente
- `prompt`: alterações em prompts ou engenharia de prompt
- `qa`: testes, validações ou qualidade
- `fix`: correções de erro
- `refactor`: reorganização de código sem alterar comportamento
- `chore`: tarefas de manutenção, limpeza ou configuração

## Exemplos recomendados

- `docs: adicionar padrão de commits`
- `docs: criar modelo padrão de pull request`
- `backend: ajustar estrutura inicial da api`
- `frontend: organizar estrutura inicial do projeto`
- `database: documentar configuração do supabase`
- `ai: documentar critérios para análise de risco`
- `prompt: revisar prompt de validação de atestado`
- `qa: adicionar checklist de validação manual`
- `fix: corrigir erro na configuração do ambiente`
- `refactor: reorganizar estrutura de serviços`
- `chore: remover arquivos desnecessários`

## Exemplos que devem ser evitados

- `teste`
- `update`
- `ajustes`
- `final`
- `alterações`
- `commit`
- `arrumando coisas`
- `mudanças`

Essas mensagens devem ser evitadas porque não explicam claramente o que foi feito nem ajudam a relacionar o commit com a tarefa em andamento.

## Relação com issues e Pull Requests

Commits não precisam fechar issues diretamente.

O fechamento da issue deve acontecer preferencialmente no Pull Request, usando:

`Closes #número-da-issue`

Exemplo:

`Closes #20`

Os commits devem estar relacionados ao escopo da issue e da branch em desenvolvimento. Se uma branch foi criada para resolver uma issue específica, os commits dessa branch devem tratar apenas do que faz sentido para aquela tarefa.

Quando surgir uma necessidade fora do escopo, o ideal é criar uma nova issue em vez de misturar assuntos diferentes no mesmo commit ou Pull Request.

## Boas práticas

- Fazer commits relacionados à tarefa em andamento.
- Evitar misturar assuntos diferentes no mesmo commit.
- Evitar mensagens genéricas.
- Manter os commits dentro do escopo da issue.
- Criar nova issue quando surgir uma necessidade fora do escopo.
- Preferir mensagens curtas, claras e rastreáveis.
