<template>
  <div class="p-10 min-h-screen w-full font-sans bg-slate-50 dark:bg-slate-950 text-slate-700 dark:text-slate-200 transition-colors duration-300">
    <div class="mx-auto max-w-7xl">
      <!-- Header Section -->
      <header class="mb-10 flex justify-between items-start">
        <div class="text-left">
          <h1 class="text-4xl font-extrabold tracking-tight text-slate-800 dark:text-slate-100">
            Dashboard
          </h1>
          <p class="text-base mt-2 font-medium text-slate-500 dark:text-slate-400">
            Visão geral em tempo real das análises de segurança documental
          </p>
        </div>

        <div class="flex items-center gap-4">
          <!-- Refresh Button -->
          <button
            @click="fetchAnalyses"
            :disabled="isLoading"
            class="px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-100 font-semibold transition-all hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-50 cursor-pointer flex items-center gap-2"
          >
            <svg class="h-4 w-4" :class="{ 'animate-spin': isLoading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 1121.253 8H18" />
            </svg>
            Atualizar
          </button>

          <!-- Toggle Dark Mode -->
          <button
            @click="toggleDarkMode"
            class="px-4 py-2 rounded-xl bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-100 font-semibold transition-all hover:scale-105 cursor-pointer"
          >
            {{ darkMode ? '☀️ Light' : '🌙 Dark' }}
          </button>
        </div>
      </header>

      <!-- Error / Loading indicators -->
      <div v-if="hasError" class="mb-8 rounded-xl border border-red-200 bg-red-50 dark:bg-red-950/20 dark:border-red-900 p-5 text-left text-red-700 dark:text-red-300">
        <p class="font-bold flex items-center gap-2">
          <span>⚠️</span> Falha ao conectar ao banco de dados Neon.
        </p>
        <p class="text-sm mt-1">Verifique sua conexão e se as chaves no backend/.env estão corretas.</p>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading && list.length === 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8 mb-10">
        <div v-for="i in 4" :key="i" class="dashboard-card animate-pulse bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-850 h-32 rounded-2xl"></div>
      </div>

      <!-- Statistics Grid -->
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8 mb-10">
        <div v-for="(stat, index) in stats" :key="index"
             class="dashboard-card group relative overflow-hidden transition-all duration-300 hover:shadow-xl hover:shadow-blue-500/5 hover:-translate-y-1">
          <div class="flex justify-between items-center">
            <div class="text-left">
              <p class="text-slate-400 dark:text-slate-500 text-[11px] font-bold uppercase tracking-widest mb-1">{{ stat.label }}</p>
              <p class="text-4xl font-black text-slate-800 dark:text-slate-100">{{ stat.value }}</p>
            </div>
            <div :class="['stat-icon', stat.iconBg, stat.iconColor]" class="p-4 rounded-xl text-2xl flex items-center justify-center">
              {{ stat.icon }}
            </div>
          </div>
          <div class="mt-4 flex items-center text-[11px] font-medium text-slate-400">
            <span class="text-emerald-500 flex items-center mr-1">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 15l7-7 7 7" />
              </svg>
              100%
            </span>
            ativos no Neon DB
          </div>
        </div>
      </div>

      <!-- Main Section -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-10">
        
        <!-- Table Card -->
        <div class="dashboard-card lg:col-span-2 transition-all duration-300 hover:shadow-xl hover:shadow-blue-500/5">
          <div class="flex justify-between items-center mb-6">
            <h3 class="font-bold text-slate-800 dark:text-slate-100 text-xl text-left">
              Últimas Análises do Banco
            </h3>
            <span class="text-xs font-semibold px-2 py-1 rounded bg-blue-50 dark:bg-blue-950 text-blue-600 dark:text-blue-400">
              Banco Conectado
            </span>
          </div>

          <div v-if="recentAnalyses.length === 0" class="flex flex-col items-center justify-center py-16 text-slate-450 dark:text-slate-500">
            <svg class="h-16 w-16 mb-4 text-slate-350" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p class="text-base font-bold">Nenhum documento analisado ainda</p>
            <p class="text-sm mt-1 text-slate-400">Envie um documento na aba "Análise de Documento" para iniciar.</p>
          </div>

          <div v-else class="overflow-x-auto">
            <table class="w-full text-left text-base">
              <thead>
                <tr class="text-slate-400 dark:text-slate-500 text-[11px] uppercase tracking-wider border-b border-slate-100 dark:border-slate-800">
                  <th class="pb-4 font-bold">Protocolo / Documento</th>
                  <th class="pb-4 font-bold">Solicitante / Departamento</th>
                  <th class="pb-4 font-bold">Status</th>
                  <th class="pb-4 font-bold text-right">Criado em</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100/50 dark:divide-slate-800/40">
                <tr v-for="(analysis, index) in recentAnalyses" :key="index"
                    @click="viewAnalysisDetails(analysis)"
                    class="group cursor-pointer transition-all duration-300 hover:bg-slate-50/70 dark:hover:bg-slate-850/50">
                  <td class="py-4">
                    <div class="font-bold text-slate-700 dark:text-slate-200 group-hover:text-blue-500 transition-colors">{{ analysis.id }}</div>
                    <div class="text-[12px] text-slate-400 dark:text-slate-500 font-semibold">{{ analysis.document }}</div>
                  </td>
                  <td class="py-4">
                    <div class="font-semibold text-slate-600 dark:text-slate-300 text-sm">{{ analysis.user }}</div>
                    <div class="text-[11px] text-slate-400 dark:text-slate-500 font-medium">{{ analysis.raw.departamento || 'Sem dpto.' }}</div>
                  </td>
                  <td class="py-4">
                    <span :class="['status-badge', analysis.statusClass]">
                      {{ analysis.status }}
                    </span>
                  </td>
                  <td class="py-4 text-right text-xs text-slate-400 dark:text-slate-500 font-semibold">{{ analysis.date }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Donut Chart Card -->
        <div class="dashboard-card flex flex-col items-center transition-all duration-300 hover:shadow-xl hover:shadow-blue-500/5">
          <h3 class="font-bold text-slate-800 dark:text-slate-100 text-xl self-start mb-8 text-left">
            Distribuição por Status
          </h3>

          <!-- Dynamic SVG Donut Chart -->
          <div class="relative w-56 h-56 flex items-center justify-center animate-scale-in">
            <svg viewBox="0 0 36 36" class="w-full h-full transform -rotate-90">
              <!-- Background grey circle -->
              <circle cx="18" cy="18" r="15.915" fill="none" stroke="currentColor" class="text-slate-100 dark:text-slate-800" stroke-width="3.6" />
              
              <!-- Segment 1: Approved (Green) -->
              <circle
                cx="18" cy="18" r="15.915"
                fill="none"
                stroke="#10b981"
                stroke-width="3.8"
                stroke-linecap="round"
                :stroke-dasharray="`${aprovadoPct} 100`"
                stroke-dashoffset="0"
                class="transition-all duration-1000 ease-out"
              />
              
              <!-- Segment 2: Pending (Amber) -->
              <circle
                cx="18" cy="18" r="15.915"
                fill="none"
                stroke="#f59e0b"
                stroke-width="3.8"
                stroke-linecap="round"
                :stroke-dasharray="`${pendentePct} 100`"
                :stroke-dashoffset="`-${aprovadoPct}`"
                class="transition-all duration-1000 ease-out"
              />
              
              <!-- Segment 3: Rejected (Rose) -->
              <circle
                cx="18" cy="18" r="15.915"
                fill="none"
                stroke="#f43f5e"
                stroke-width="3.8"
                stroke-linecap="round"
                :stroke-dasharray="`${rejeitadoPct} 100`"
                :stroke-dashoffset="`-${aprovadoPct + pendentePct}`"
                class="transition-all duration-1000 ease-out"
              />
            </svg>
            <div class="absolute flex flex-col items-center">
              <span class="text-4xl font-black text-slate-800 dark:text-slate-100">{{ list.length }}</span>
              <span class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">Total</span>
            </div>
          </div>

          <!-- Donut Legend -->
          <div class="mt-8 grid grid-cols-1 w-full gap-2.5">
            <div v-for="item in distribution" :key="item.label"
                 class="flex items-center justify-between p-2.5 rounded-xl cursor-default hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
              <div class="flex items-center gap-2.5">
                <span :class="['w-3.5 h-3.5 rounded-full', item.color]">&nbsp;</span>
                <span class="text-[12px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">{{ item.label }}</span>
              </div>
              <div class="text-right">
                <span class="text-sm font-black text-slate-700 dark:text-slate-200 mr-2">{{ item.value }}</span>
                <span class="text-xs text-slate-400 font-semibold">({{ item.pct }}%)</span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import './dashboard.css';
import { list, stats, recentAnalyses, distribution, fetchAnalyses, isLoading, hasError } from './dashboard';
import { loadAnalysisIntoView } from '../AnaliseIa/analysis';
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const darkMode = ref(false);

onMounted(() => {
  // Toggle Theme
  darkMode.value = localStorage.getItem('theme') === 'dark';
  if (darkMode.value) {
    document.documentElement.classList.add('dark');
  }
  
  // Load data from live Neon Database
  fetchAnalyses();
});

const toggleDarkMode = () => {
  darkMode.value = !darkMode.value;
  if (darkMode.value) {
    document.documentElement.classList.add('dark');
    localStorage.setItem('theme', 'dark');
  } else {
    document.documentElement.classList.remove('dark');
    localStorage.setItem('theme', 'light');
  }
};

// SVG Donut calculation helpers
const aprovadoPct = computed(() => {
  const item = distribution.value.find(d => d.label === 'Aprovado');
  return item ? item.pct : 0;
});

const pendentePct = computed(() => {
  const item = distribution.value.find(d => d.label === 'Pendente');
  return item ? item.pct : 0;
});

const rejeitadoPct = computed(() => {
  const item = distribution.value.find(d => d.label === 'Rejeitado');
  return item ? item.pct : 0;
});

// View Details function
const viewAnalysisDetails = (item: any) => {
  loadAnalysisIntoView(item.raw);
  router.push('/analise');
};
</script>

<style scoped>
@reference "../../assets/main.css";

.dashboard-card {
  @apply bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-2xl p-6 shadow-sm;
}
.stat-icon {
  @apply h-12 w-12 rounded-xl text-2xl flex items-center justify-center transition-transform duration-300;
}
.status-badge {
  @apply px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-transform duration-300 inline-block;
}
</style>
