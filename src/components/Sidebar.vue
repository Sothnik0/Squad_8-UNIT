<template>
  <aside class="w-64 bg-slate-900 min-h-screen text-slate-300 flex flex-col p-4 shadow-xl">
    <div class="flex items-center gap-3 px-2 mb-10 mt-4">
      <div
        class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold"
      >
        D
      </div>
      <span class="text-xl font-bold text-white tracking-tight text-[18px]">DocSecurity</span>
    </div>

    <nav class="flex-1 space-y-2">
      <RouterLink
        to="/"
        class="flex items-center gap-3 px-4 py-3 rounded-lg transition-colors hover:bg-slate-800 hover:text-white"
        active-class="bg-blue-600 !text-white"
      >
        <span>📊</span>Análise de Documento
      </RouterLink>

      <RouterLink
        to="/analise"
        class="flex items-center gap-3 px-4 py-3 rounded-lg transition-colors hover:bg-slate-800 hover:text-white"
        active-class="bg-blue-600 !text-white"
      >
        <span>🛡️</span> Dashboard
      </RouterLink>

      <RouterLink
        to="/ordens"
        class="flex items-center gap-3 px-4 py-3 rounded-lg transition-colors hover:bg-slate-800 hover:text-white"
        active-class="bg-blue-600 !text-white"
      >
        <span>📋</span> Ordens de Serviço
      </RouterLink>
    </nav>

    <div class="pt-4 border-t border-slate-800">
      <button
        class="flex items-center gap-3 px-4 py-3 text-sm hover:text-red-400 transition-colors"
      >
        Sair
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>
