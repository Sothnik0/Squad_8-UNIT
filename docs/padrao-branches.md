# Padrão de branches do Verify

Este documento define o padrão de nomenclatura de branches do projeto Verify.

O objetivo é melhorar a organização do repositório, facilitar a rastreabilidade entre issue, branch e Pull Request, evitar nomes genéricos e ajudar o squad a entender rapidamente o escopo de cada alteração.

## Formato padrão

Toda branch criada para uma tarefa deve seguir o formato:

`tipo/resumo-curto`

Exemplos:

- `docs/issue-template`
- `docs/padrao-branches`
- `docs/pr-template`
- `backend/conectar-supabase`
- `frontend/tela-upload-documento`
- `database/modelo-postgresql`
- `ai/arquitetura-uso-ia`
- `prompt/rastreabilidade-prompts`
- `qa/documentos-teste`
- `fix/corrigir-upload-pdf`
- `refactor/organizar-servicos-backend`
- `chore/organizar-github`

## Regras gerais

- Criar a branch sempre a partir da `master` atualizada.
- Usar letras minúsculas.
- Não usar acentos.
- Não usar espaços.
- Usar hífen entre palavras no resumo da branch.
- Evitar nomes genéricos como `teste`, `ajustes`, `final`, `nova-branch` ou `mutter`.
- Sempre que houver mudança relevante, a branch deve estar associada a uma issue.
- O nome da branch deve deixar claro o tipo e o objetivo da alteração.

## Branch não é pasta do projeto

O prefixo da branch serve para organizar visualmente o trabalho no GitHub, mas não significa que será criada uma pasta com aquele nome no projeto.

Exemplo:

Branch:

`backend/conectar-supabase`

Isso não significa que será criada uma pasta chamada `backend/conectar-supabase`.

Da mesma forma:

Branch:

`docs/padrao-branches`

Isso não significa que será criada uma pasta chamada `docs/padrao-branches`.

A branch é apenas uma linha de trabalho no Git. Os arquivos alterados devem respeitar a estrutura real do projeto.

## Diferença entre branch e arquivo

Branches devem usar hífen entre palavras por legibilidade:

`backend/conectar-supabase`

Arquivos Python devem continuar usando `snake_case`, seguindo o padrão da linguagem:

`document_analysis.py`

`ocr_service.py`

`auth_service.py`

Ou seja:

- Branches: usar hífen.
- Arquivos Markdown/documentação: podem usar hífen.
- Arquivos Python: usar `snake_case`.

## Prefixos permitidos

### `docs/`

Use para documentação, README, guias, templates e registros do projeto.

Exemplos:

- `docs/issue-template`
- `docs/pr-template`
- `docs/padrao-branches`
- `docs/regras-contribuicao`

### `backend/`

Use para alterações na API, endpoints, regras de negócio e integrações do backend.

Exemplos:

- `backend/conectar-supabase`
- `backend/criar-endpoint-analise`
- `backend/validar-documento`

### `frontend/`

Use para alterações em telas, componentes, estilos e experiência do usuário.

Exemplos:

- `frontend/tela-upload-documento`
- `frontend/exibir-resultado-analise`
- `frontend/ajustar-layout-dashboard`

### `database/`

Use para banco de dados, Supabase, migrations, tabelas, entidades e persistência.

Exemplos:

- `database/modelo-postgresql`
- `database/configurar-supabase`
- `database/criar-tabela-documentos`

### `ai/`

Use para arquitetura, integração ou uso de inteligência artificial no sistema.

Exemplos:

- `ai/arquitetura-uso-ia`
- `ai/classificacao-risco`
- `ai/gerar-justificativa`

### `prompt/`

Use para criação, ajuste, versionamento ou validação de prompts.

Exemplos:

- `prompt/rastreabilidade-prompts`
- `prompt/revisar-prompt-base`
- `prompt/json-estruturado`

### `qa/`

Use para testes, validações, qualidade, documentos de teste e evidências.

Exemplos:

- `qa/documentos-teste`
- `qa/validar-output-ia`
- `qa/comparar-prompt-antigo-novo`

### `fix/`

Use para correções de bugs ou comportamentos inesperados.

Exemplos:

- `fix/corrigir-upload-pdf`
- `fix/erro-validacao-cpf`
- `fix/falha-ocr-pdf`

### `refactor/`

Use para refatorações internas que não mudam o comportamento esperado do sistema.

Exemplos:

- `refactor/organizar-servicos-backend`
- `refactor/separar-validacoes`
- `refactor/melhorar-estrutura-pastas`

### `chore/`

Use para manutenção, organização ou configuração geral que não seja funcionalidade, bug ou documentação principal.

Exemplos:

- `chore/organizar-github`
- `chore/atualizar-gitignore`
- `chore/configurar-ambiente`

## Como criar uma branch

Antes de criar uma branch, atualize a `master` local:

```bash
git checkout master
git pull origin master
```

Depois crie a branch seguindo o padrão:

```bash
git checkout -b tipo/resumo-curto
```

Exemplo:

```bash
git checkout -b docs/padrao-branches
```

## Relação com issues e PRs

Toda branch criada para uma mudança relevante deve estar associada a uma issue.

Fluxo esperado:

1. Criar ou assumir uma issue.
2. Criar uma branch a partir da `master`.
3. Trabalhar apenas no escopo da issue.
4. Abrir Pull Request.
5. Referenciar a issue no PR.
6. Solicitar revisão.
7. Fazer merge apenas após validação.

Exemplo:

Issue:

`#13 [GESTÃO] Definir padrão de branches`

Branch:

`docs/padrao-branches`

Pull Request:

`[DOCS] Definir padrão de branches`

## Boas práticas

- Use nomes curtos, mas claros.
- Evite branch com nome de pessoa.
- Evite branch com nome genérico.
- Não misture várias tarefas não relacionadas na mesma branch.
- Não use a mesma branch para resolver issues diferentes sem relação.
- Se a tarefa crescer demais, considere dividir em mais de uma issue.
- Se precisar alterar algo fora do escopo, registre no PR e justifique.

## Exemplos bons e ruins

### Bons exemplos

- `docs/issue-template`
- `backend/conectar-supabase`
- `frontend/tela-upload-documento`
- `database/modelo-postgresql`
- `prompt/revisar-prompt-base`
- `qa/documentos-teste`
- `fix/corrigir-upload-pdf`

### Exemplos ruins

- `teste`
- `ajustes`
- `final`
- `nova-branch`
- `mutter`
- `correcoes`
- `alteracoes`

Esses nomes são ruins porque não deixam claro o objetivo da branch nem a issue relacionada.
