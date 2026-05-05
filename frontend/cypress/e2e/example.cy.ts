// https://on.cypress.io/api

describe('Fluxo de Análise de Documentos', () => {
  it('Deve carregar a página inicial e exibir o título correto', () => {
    // Visita a URL raiz do app
    cy.visit('/')

    // Verifica se o título principal da sua nova interface está presente
    cy.contains('h1', 'Análise de Documento')
    
    // Verifica se o subtítulo descritivo aparece
    cy.contains('p', 'Solicite a análise técnica')
  })

  it('Deve validar campos obrigatórios ao tentar analisar sem dados', () => {
    cy.visit('/')
    
    // Clica no botão de analisar sem preencher nada
    cy.get('button').contains('Analisar Documento').click()

    // Verifica se as mensagens de erro do objeto 'erros' aparecem na tela
    cy.contains('Campo obrigatório').should('be.visible')
    cy.contains('Selecione o tipo').should('be.visible')
  })
})
