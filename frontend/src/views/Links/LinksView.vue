<template>
  <div class="p-8 bg-[#f8fafc] dark:bg-slate-900 min-h-screen w-full text-slate-700 dark:text-slate-200 transition-colors duration-300">
    <header class="mb-10 flex items-start justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-slate-100">
          Links Úteis
        </h1>

        <p class="text-slate-500 dark:text-slate-400 text-sm">
          Portais e ferramentas oficiais para validação de documentos e certificados
        </p>
      </div>

      <button
        @click="toggleDarkMode"
        class="px-4 py-2 rounded-xl bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-100 font-semibold transition-all hover:scale-105"
      >
        {{ darkMode ? '☀️ Light' : '🌙 Dark' }}
      </button>
    </header>

    <section class="mb-12">
      <div class="flex items-center gap-2 mb-6 text-blue-600">
        <span class="bg-blue-100 p-2 rounded-lg text-xl">🎓</span>
        <h2 class="text-lg font-bold text-slate-800 dark:text-slate-100">Validação de Certificados e Diplomas</h2>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <a href="https://sistec.mec.gov.br/validadocertificado/" target="_blank" class="group bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm hover:shadow-md hover:border-blue-200 dark:hover:border-blue-700 transition-all">
          <div class="flex justify-between items-start mb-2">
            <h3 class="font-bold text-slate-800 dark:text-slate-100 group-hover:text-blue-600 transition-colors">SISTEC - Validação de Diplomas</h3>
            <span class="text-slate-300 text-sm">↗</span>
          </div>
          <p class="text-sm text-slate-500 dark:text-slate-400 mb-4">Validação nacional de diplomas e certificados de cursos técnicos registrados no MEC.</p>
          <div class="flex gap-2">
            <span class="bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-300 text-[10px] font-bold px-2 py-1 rounded">MEC</span>
            <span class="bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-300 text-[10px] font-bold px-2 py-1 rounded">Cursos Técnicos</span>
          </div>
        </a>

        <a href="https://emec.mec.gov.br/" target="_blank" class="group bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm hover:shadow-md hover:border-blue-200 dark:hover:border-blue-700 transition-all">
          <div class="flex justify-between items-start mb-2">
            <h3 class="font-bold text-slate-800 dark:text-slate-100 group-hover:text-blue-600 transition-colors">e-MEC - Cadastro Nacional</h3>
            <span class="text-slate-300 text-sm">↗</span>
          </div>
          <p class="text-sm text-slate-500 dark:text-slate-400 mb-4">Consulta de instituições de ensino superior credenciadas e cursos autorizados pelo MEC.</p>
          <div class="flex gap-2">
            <span class="bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-300 text-[10px] font-bold px-2 py-1 rounded">MEC</span>
            <span class="bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-300 text-[10px] font-bold px-2 py-1 rounded">Ensino Superior</span>
          </div>
        </a>
      </div>
    </section>

    <section>
      <div class="flex items-center gap-2 mb-6 text-blue-600">
        <span class="bg-blue-100 dark:bg-blue-900/40 p-2 rounded-lg text-xl">📄</span>
        <h2 class="text-lg font-bold text-slate-800">Validação de Documentos Oficiais</h2>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <a href="https://servicos.receita.fazenda.gov.br/servicos/cnpjreva/cnpjreva_solicitacao.asp" target="_blank" class="group bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm hover:shadow-md hover:border-blue-200 dark:hover:border-blue-700 transition-all">
          <div class="flex justify-between items-start mb-2">
            <h3 class="font-bold text-slate-800 dark:text-slate-100 group-hover:text-blue-600 transition-colors">Receita Federal - Consulta CNPJ</h3>
            <span class="text-slate-300 text-sm">↗</span>
          </div>
          <p class="text-sm text-slate-500 dark:text-slate-400 mb-4">Verificação de CNPJ de instituições para confirmar existência e situação cadastral.</p>
          <div class="flex gap-2">
            <span class="bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-300 text-[10px] font-bold px-2 py-1 rounded">Receita Federal</span>
            <span class="bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-300 text-[10px] font-bold px-2 py-1 rounded">CNPJ</span>
          </div>
        </a>
      </div>
    </section>
  </div>
</template>
  <script setup lang="ts">
    import { ref, onMounted } from 'vue'

    const darkMode = ref(false)

    onMounted(() => {
      darkMode.value = localStorage.getItem('theme') === 'dark'

      if (darkMode.value) {
        document.documentElement.classList.add('dark')
      }
    })

    const toggleDarkMode = () => {
      darkMode.value = !darkMode.value

      if (darkMode.value) {
        document.documentElement.classList.add('dark')
        localStorage.setItem('theme', 'dark')
      } else {
        document.documentElement.classList.remove('dark')
        localStorage.setItem('theme', 'light')
      }
    }
  </script>
