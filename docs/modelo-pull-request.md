# Modelo de Pull Request

Este documento registra o modelo padrão de Pull Request usado no projeto Verify.

O arquivo automático usado pelo GitHub fica em:

`.github/pull_request_template.md`

## Modelo

```markdown
## Resumo
Uma linha explicando o que o PR entrega.

## Issue relacionada
- Resolvido completamente: `Closes #`
- Resolvido parcialmente: `#` + explicar pendência

## O que mudou
- Arquivo x: o que foi feito
- Arquivo y: o que foi feito

## Por que mudou
Antes → depois → por que é melhor.

## Como validou
Como testou, print, comando, Swagger, comparação antes/depois.
```
