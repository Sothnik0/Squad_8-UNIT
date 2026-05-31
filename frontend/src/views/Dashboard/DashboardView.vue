<template>
  <div class="p-10 bg-slate-50/50 min-h-screen w-full font-sans">
    
    <header class="mb-10 animate-fade-in">
      <h1 class="text-4xl font-extrabold text-slate-800 tracking-tighter">Dashboard</h1>
      <p class="text-slate-500 text-base mt-2 font-medium">Visão geral das análises de segurança documental</p>
    </header>

    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8 mb-10">
      <div v-for="(stat, index) in stats" :key="index"
           class="dashboard-card group animate-scale-in cursor-pointer transition-all duration-500 hover:animate-none hover:shadow-xl hover:shadow-blue-500/10 hover:-translate-y-1.5"
           :class="`delay-${(index + 1) * 100}`">
        <div class="flex justify-between items-center">
          <div>
            <p class="text-slate-500 text-[11px] font-bold uppercase tracking-widest mb-1">{{ stat.label }}</p>
            <p class="text-4xl font-black text-slate-800">{{ stat.value }}</p>
          </div>
          <div :class="['stat-icon', stat.iconBg, stat.iconColor]" class="p-4 rounded-xl text-2xl">
            {{ stat.icon }}
          </div>
        </div>
        <div class="mt-4 flex items-center text-[11px] font-medium text-slate-400">
          <span class="text-emerald-500 flex items-center mr-1">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 15l7-7 7 7" />
            </svg>
            12%
          </span>
          vs. mês anterior
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-10">
      
      <div class="dashboard-card lg:col-span-2 animate-fade-in delay-500 cursor-pointer transition-all duration-500 hover:animate-none hover:shadow-xl hover:shadow-blue-500/10 hover:-translate-y-1.5">
        <div class="flex justify-between items-center mb-6">
          <h3 class="font-bold text-slate-800 text-xl">Últimas Análises</h3>
          <button class="text-blue-600 text-sm font-bold hover:underline cursor-pointer">Ver todas</button>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-base">
            <thead>
              <tr class="text-slate-400 text-[11px] uppercase tracking-wider border-b border-slate-50">
                <th class="pb-5 font-bold">Protocolo / Documento</th>
                <th class="pb-5 font-bold">Status</th>
                <th class="pb-5 font-bold text-right">Data</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(analysis, index) in recentAnalyses" :key="index"
                  class="border-b border-slate-50 last:border-0 table-row-hover group cursor-pointer transition-all duration-300 hover:bg-slate-50/80">
                <td class="py-5">
                  <div class="font-bold text-slate-700 group-hover:text-blue-600 transition-colors">{{ analysis.id }}</div>
                  <div class="text-[12px] text-slate-400 font-semibold">{{ analysis.document }} · {{ analysis.user }}</div>
                </td>
                <td class="py-5">
                  <span :class="['status-badge', analysis.statusClass]" class="hover:scale-105 transition-transform duration-300">
                    {{ analysis.status }}
                  </span>
                </td>
                <td class="py-5 text-right text-slate-400 font-medium">{{ analysis.date }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="dashboard-card flex flex-col items-center animate-fade-in delay-500 cursor-pointer transition-all duration-500 hover:animate-none hover:shadow-xl hover:shadow-blue-500/10 hover:-translate-y-1.5">
        <h3 class="font-bold text-slate-800 text-xl self-start mb-8">Distribuição por Status</h3>

        <div class="relative w-56 h-56 flex items-center justify-center">
          <svg viewBox="0 0 36 36" class="w-full h-full transform -rotate-90">
            <path class="text-emerald-500" stroke-dasharray="40, 100" stroke-width="3.8" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
            <path class="text-rose-400" stroke-dasharray="40, 100" stroke-dashoffset="-40" stroke-width="3.8" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
            <path class="text-amber-400" stroke-dasharray="20, 100" stroke-dashoffset="-80" stroke-width="3.8" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
          </svg>
          <div class="absolute flex flex-col items-center">
            <span class="text-3xl font-black text-slate-800">5</span>
            <span class="text-[11px] font-bold text-slate-400 uppercase">Total</span>
          </div>
        </div>

        <div class="mt-10 grid grid-cols-1 w-full gap-3">
          <div v-for="item in distribution" :key="item.label"
               class="flex items-center justify-between p-2 rounded-xl cursor-pointer hover:bg-slate-50 transition-colors">
            <div class="flex items-center gap-2">
              <span :class="['w-3 h-3 rounded-full', item.color]"></span>
              <span class="text-[12px] font-bold uppercase tracking-wider text-slate-500">{{ item.label }}</span>
            </div>
            <span class="text-sm font-black text-slate-700">{{ item.value }}</span>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import './dashboard.css';
import { stats, recentAnalyses, distribution } from './dashboard';
</script>

<style scoped>

</style>
