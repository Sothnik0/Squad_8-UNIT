<template>
  <div class="p-8 bg-[#f8fafc] min-h-screen w-full text-slate-700">
    <header class="mb-10">
      <h1 class="text-2xl font-bold text-slate-800">Links Úteis</h1>
      <p class="text-slate-500 text-sm">Portais e ferramentas oficiais para validação de documentos e certificados</p>
    </header>

    <section class="mb-12">
      <div class="flex items-center gap-2 mb-6 text-blue-600">
        <span class="bg-blue-100 p-2 rounded-lg text-xl">🎓</span>
        <h2 class="text-lg font-bold text-slate-800">Validação de Certificados e Diplomas</h2>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <a href="https://sistec.mec.gov.br/validadocertificado/" target="_blank" class="group bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md hover:border-blue-200 transition-all">
          <div class="flex justify-between items-start mb-2">
            <h3 class="font-bold text-slate-800 group-hover:text-blue-600 transition-colors">SISTEC - Validação de Diplomas</h3>
            <span class="text-slate-300 text-sm">↗</span>
          </div>
          <p class="text-sm text-slate-500 mb-4">Validação nacional de diplomas e certificados de cursos técnicos registrados no MEC.</p>
          <div class="flex gap-2">
            <span class="bg-slate-100 text-slate-500 text-[10px] font-bold px-2 py-1 rounded">MEC</span>
            <span class="bg-slate-100 text-slate-500 text-[10px] font-bold px-2 py-1 rounded">Cursos Técnicos</span>
          </div>
        </a>

        <a href="https://emec.mec.gov.br/" target="_blank" class="group bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md hover:border-blue-200 transition-all">
          <div class="flex justify-between items-start mb-2">
            <h3 class="font-bold text-slate-800 group-hover:text-blue-600 transition-colors">e-MEC - Cadastro Nacional</h3>
            <span class="text-slate-300 text-sm">↗</span>
          </div>
          <p class="text-sm text-slate-500 mb-4">Consulta de instituições de ensino superior credenciadas e cursos autorizados pelo MEC.</p>
          <div class="flex gap-2">
            <span class="bg-slate-100 text-slate-500 text-[10px] font-bold px-2 py-1 rounded">MEC</span>
            <span class="bg-slate-100 text-slate-500 text-[10px] font-bold px-2 py-1 rounded">Ensino Superior</span>
          </div>
        </a>
      </div>
    </section>

    <section>
      <div class="flex items-center gap-2 mb-6 text-blue-600">
        <span class="bg-blue-100 p-2 rounded-lg text-xl">📄</span>
        <h2 class="text-lg font-bold text-slate-800">Validação de Documentos Oficiais</h2>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <a href="https://servicos.receita.fazenda.gov.br/servicos/cnpjreva/cnpjreva_solicitacao.asp" target="_blank" class="group bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md hover:border-blue-200 transition-all">
          <div class="flex justify-between items-start mb-2">
            <h3 class="font-bold text-slate-800 group-hover:text-blue-600 transition-colors">Receita Federal - Consulta CNPJ</h3>
            <span class="text-slate-300 text-sm">↗</span>
          </div>
          <p class="text-sm text-slate-500 mb-4">Verificação de CNPJ de instituições para confirmar existência e situação cadastral.</p>
          <div class="flex gap-2">
            <span class="bg-slate-100 text-slate-500 text-[10px] font-bold px-2 py-1 rounded">Receita Federal</span>
            <span class="bg-slate-100 text-slate-500 text-[10px] font-bold px-2 py-1 rounded">CNPJ</span>
          </div>
        </a>
      </div>
    </section>
  </div>
</template>