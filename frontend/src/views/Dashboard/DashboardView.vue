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

          <!-- Filters Section -->
          <div v-if="list.length > 0" class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
            <!-- Search -->
            <div class="relative">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Buscar por protocolo, solicitante..."
                class="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 text-slate-700 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
              />
              <span class="absolute left-3 top-3 text-slate-400 dark:text-slate-500">
                <svg class="h-4.5 w-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </span>
            </div>

            <!-- Date Filter -->
            <div class="relative">
              <input
                v-model="dateFilter"
                type="date"
                class="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 text-slate-700 dark:text-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all text-slate-450 dark:text-slate-400"
              />
            </div>

            <!-- Status Filter -->
            <div class="relative">
              <select
                v-model="statusFilter"
                class="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 text-slate-700 dark:text-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all appearance-none cursor-pointer"
              >
                <option value="todos">Todos os Status</option>
                <option value="aprovado">Aprovados</option>
                <option value="pendente">Pendentes</option>
                <option value="rejeitado">Rejeitados</option>
              </select>
              <span class="absolute right-3.5 top-3.5 pointer-events-none text-slate-400 dark:text-slate-500">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </span>
            </div>
          </div>

          <!-- Empty Database State -->
          <div v-if="list.length === 0" class="flex flex-col items-center justify-center py-16 text-slate-450 dark:text-slate-500">
            <svg class="h-16 w-16 mb-4 text-slate-350" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p class="text-base font-bold">Nenhum documento analisado ainda</p>
            <p class="text-sm mt-1 text-slate-400">Envie um documento na aba "Análise de Documento" para iniciar.</p>
          </div>

          <!-- Empty Search/Filter Result State -->
          <div v-else-if="filteredAnalyses.length === 0" class="flex flex-col items-center justify-center py-16 text-slate-450 dark:text-slate-500">
            <svg class="h-16 w-16 mb-4 text-slate-350" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <p class="text-base font-bold">Nenhuma análise correspondente</p>
            <p class="text-sm mt-1 text-slate-450 mb-4">Nenhum protocolo atendeu aos filtros informados.</p>
            <button
              @click="clearFilters"
              class="px-4 py-2 rounded-xl bg-blue-50 dark:bg-blue-950 text-blue-600 dark:text-blue-400 font-bold text-sm transition hover:bg-blue-100 cursor-pointer"
            >
              Limpar Filtros
            </button>
          </div>

          <!-- Data Table & Pagination -->
          <div v-else>
            <div class="overflow-x-auto">
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
                  <tr v-for="(analysis, index) in paginatedAnalyses" :key="index"
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

            <!-- Pagination Controls -->
            <div class="flex items-center justify-between mt-6 pt-4 border-t border-slate-100 dark:border-slate-800">
              <span class="text-xs font-semibold text-slate-400 dark:text-slate-500">
                Mostrando {{ (currentPage - 1) * itemsPerPage + 1 }} - {{ Math.min(currentPage * itemsPerPage, filteredAnalyses.length) }} de {{ filteredAnalyses.length }} análises
              </span>
              
              <div class="flex items-center gap-2">
                <button
                  @click="currentPage--"
                  :disabled="currentPage === 1"
                  class="p-2 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-50 dark:hover:bg-slate-800 transition-all cursor-pointer flex items-center justify-center"
                  title="Página Anterior"
                >
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                
                <span class="text-xs font-bold text-slate-700 dark:text-slate-300 px-2">
                  Página {{ currentPage }} de {{ totalPages }}
                </span>
                
                <button
                  @click="currentPage++"
                  :disabled="currentPage === totalPages"
                  class="p-2 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-50 dark:hover:bg-slate-800 transition-all cursor-pointer flex items-center justify-center"
                  title="Próxima Página"
                >
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            </div>
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
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const darkMode = ref(false);

// Local states for Search, Filters, and Pagination
const searchQuery = ref('');
const dateFilter = ref('');
const statusFilter = ref('todos');
const currentPage = ref(1);
const itemsPerPage = 10;

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

// Formats raw data to visual layout (similar to dashboard.ts but processes all items)
const formatAnalysis = (o: any) => {
  let statusLabel = 'Pendente'
  let statusClass = 'bg-amber-100 dark:bg-amber-950/30 text-amber-700 dark:text-amber-400'
  if (o.status === 'aprovado') {
    statusLabel = 'Aprovado'
    statusClass = 'bg-emerald-100 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-400'
  } else if (o.status === 'rejeitado') {
    statusLabel = 'Rejeitado'
    statusClass = 'bg-rose-100 dark:bg-rose-950/30 text-rose-700 dark:text-rose-400'
  }
  
  let displayDate = ''
  if (o.criado_em) {
    try {
      const d = new Date(o.criado_em)
      const day = String(d.getDate()).padStart(2, '0')
      const month = String(d.getMonth() + 1).padStart(2, '0')
      const year = d.getFullYear()
      const hour = String(d.getHours()).padStart(2, '0')
      const min = String(d.getMinutes()).padStart(2, '0')
      displayDate = `${day}/${month}/${year} ${hour}:${min}`
    } catch (err) {
      displayDate = o.criado_em
    }
  }
  
  return {
    id: o.protocolo,
    document: o.tipo_documento_nome || 'Documento',
    user: o.solicitante,
    status: statusLabel,
    statusClass: statusClass,
    date: displayDate,
    raw: o
  }
}

// Search and Filter computation
const filteredAnalyses = computed(() => {
  let result = list.value.map(formatAnalysis);
  
  // 1. Filter by Search Query (ID, requester name, or document type)
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim();
    result = result.filter(item => 
      item.id.toLowerCase().includes(query) ||
      item.user.toLowerCase().includes(query) ||
      item.document.toLowerCase().includes(query)
    );
  }
  
  // 2. Filter by Date (YYYY-MM-DD)
  if (dateFilter.value) {
    const filterDateStr = dateFilter.value;
    result = result.filter(item => {
      if (!item.raw.criado_em) return false;
      const itemDate = new Date(item.raw.criado_em);
      const year = itemDate.getFullYear();
      const month = String(itemDate.getMonth() + 1).padStart(2, '0');
      const day = String(itemDate.getDate()).padStart(2, '0');
      const formattedItemDate = `${year}-${month}-${day}`;
      return formattedItemDate === filterDateStr;
    });
  }
  
  // 3. Filter by Status
  if (statusFilter.value !== 'todos') {
    result = result.filter(item => {
      const rawStatus = item.raw.status;
      if (statusFilter.value === 'aprovado') return rawStatus === 'aprovado';
      if (statusFilter.value === 'rejeitado') return rawStatus === 'rejeitado';
      if (statusFilter.value === 'pendente') {
        return rawStatus !== 'aprovado' && rawStatus !== 'rejeitado';
      }
      return true;
    });
  }
  
  return result;
});

// Paginated view computation
const paginatedAnalyses = computed(() => {
  const startIndex = (currentPage.value - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  return filteredAnalyses.value.slice(startIndex, endIndex);
});

const totalPages = computed(() => {
  return Math.ceil(filteredAnalyses.value.length / itemsPerPage) || 1;
});

// Clear all filter fields
const clearFilters = () => {
  searchQuery.value = '';
  dateFilter.value = '';
  statusFilter.value = 'todos';
};

// Reset page pagination upon filter adjustment
watch([searchQuery, dateFilter, statusFilter], () => {
  currentPage.value = 1;
});
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
