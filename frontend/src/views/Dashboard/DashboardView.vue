<template>
  <div class="p-8 bg-slate-50/50 min-h-screen w-full font-sans">
    <header class="mb-8 animate-fade-in">
      <h1 class="text-3xl font-extrabold text-slate-800 tracking-tight">Dashboard</h1>
      <p class="text-slate-500 text-sm mt-1 font-medium">Visão geral das análises de segurança documental</p>
    </header>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 mb-8">
      <div v-for="(stat, index) in stats" :key="index" 
           class="dashboard-card group animate-scale-in"
           :class="`delay-${(index + 1) * 100}`">
        <div class="flex justify-between items-center">
          <div>
            <p class="text-slate-500 text-[10px] font-bold uppercase tracking-widest mb-1">{{ stat.label }}</p>
            <p class="text-3xl font-black text-slate-800">{{ stat.value }}</p>
          </div>
          <div :class="['stat-icon', stat.iconBg, stat.iconColor]">
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

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Recent Analysis Table -->
      <div class="lg:col-span-2 dashboard-card animate-fade-in delay-500">
        <div class="flex justify-between items-center mb-6">
          <h3 class="font-bold text-slate-800 text-lg">Últimas Análises</h3>
          <button class="text-blue-600 text-xs font-bold hover:underline cursor-pointer">Ver todas</button>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left">
            <thead>
              <tr class="text-slate-400 text-[10px] uppercase tracking-wider border-b border-slate-50">
                <th class="pb-4 font-bold">Protocolo / Documento</th>
                <th class="pb-4 font-bold">Status</th>
                <th class="pb-4 font-bold text-right">Data</th>
              </tr>
            </thead>
            <tbody class="text-sm">
              <tr v-for="(analysis, index) in recentAnalyses" :key="index" 
                  class="border-b border-slate-50 last:border-0 table-row-hover group transition-all">
                <td class="py-4">
                  <div class="font-bold text-slate-700 group-hover:text-blue-600 transition-colors">{{ analysis.id }}</div>
                  <div class="text-[11px] text-slate-400 font-semibold">{{ analysis.document }} · {{ analysis.user }}</div>
                </td>
                <td class="py-4">
                  <span :class="['status-badge', analysis.statusClass]">
                    {{ analysis.status }}
                  </span>
                </td>
                <td class="py-4 text-right text-slate-400 font-medium">{{ analysis.date }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Chart / Distribution -->
      <div class="dashboard-card flex flex-col items-center animate-fade-in delay-500">
        <h3 class="font-bold text-slate-800 text-lg self-start mb-6">Distribuição por Status</h3>

        <div class="relative w-48 h-48 flex items-center justify-center">
          <!-- Mock Chart SVG -->
          <svg viewBox="0 0 36 36" class="w-full h-full transform -rotate-90">
            <path class="text-emerald-500" stroke-dasharray="40, 100" stroke-width="3.8" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
            <path class="text-rose-400" stroke-dasharray="40, 100" stroke-dashoffset="-40" stroke-width="3.8" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
            <path class="text-amber-400" stroke-dasharray="20, 100" stroke-dashoffset="-80" stroke-width="3.8" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
          </svg>
          <div class="absolute flex flex-col items-center">
            <span class="text-2xl font-black text-slate-800">5</span>
            <span class="text-[10px] font-bold text-slate-400 uppercase">Total</span>
          </div>
        </div>

        <div class="mt-8 grid grid-cols-1 w-full gap-3">
          <div v-for="item in distribution" :key="item.label" class="flex items-center justify-between p-2 rounded-xl hover:bg-slate-50 transition-colors">
            <div class="flex items-center gap-2">
              <span :class="['w-2.5 h-2.5 rounded-full', item.color]"></span>
              <span class="text-[11px] font-bold uppercase tracking-wider text-slate-500">{{ item.label }}</span>
            </div>
            <span class="text-xs font-black text-slate-700">{{ item.value }}</span>
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
/* Scoped styles can be added here if needed, but we use dashboard.css */
</style>
