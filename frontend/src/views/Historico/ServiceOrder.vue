<template>
  <div class="min-h-screen bg-gray-50 p-8 text-slate-700">
    <div class="max-w-5xl mx-auto">
      <header class="mb-8">
        <h1 class="text-2xl font-bold text-slate-800 text-left">Ordens de serviço</h1>
        <p class="text-slate-500 text-left">Histórico completo de análises de documentos</p>
      </header>

      <div class="flex items-center gap-4 mb-6">
        <div class="flex-1 text-left">
          <div class="relative">
            <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
              <svg class="w-4 h-4 text-gray-400" viewBox="0 0 24 24" fill="none">
                <path stroke="currentColor" stroke-width="2" stroke-linecap="round" d="m21 21-3.5-3.5M17 10a7 7 0 1 1-14 0 7 7 0 0 1 14 0Z"/>
              </svg>
            </div>
            <input
              v-model="search"
              type="search"
              class="w-full p-3 pl-9 pr-28 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none transition"
              placeholder="Buscar por OS ou solicitante"
            />
          </div>
        </div>

        <el-dropdown @command="handleStatus" trigger="click">
          <span class="cursor-pointer px-4 py-3 text-sm font-semibold bg-white border border-gray-200 rounded-lg flex items-center gap-2 hover:bg-gray-50 transition">
            {{ selectedStatus || 'Todos os status' }}
            <svg class="w-4 h-4 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
              <path d="M5.22 8.22a.75.75 0 0 1 1.06 0L10 11.94l3.72-3.72a.75.75 0 1 1 1.06 1.06l-4.25 4.25a.75.75 0 0 1-1.06 0L5.22 9.28a.75.75 0 0 1 0-1.06Z"/>
            </svg>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="">Todos</el-dropdown-item>
              <el-dropdown-item v-for="status in statusList" :key="status" :command="status">
                {{ status }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>

      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table class="w-full">
          <thead>
            <tr class="text-xs text-gray-400 uppercase bg-gray-50/50">
              <th class="px-6 py-4 text-left font-bold">Nº OS</th>
              <th class="px-6 py-4 text-left font-bold">Solicitante</th>
              <th class="px-6 py-4 text-left font-bold">Tipo</th>
              <th class="px-6 py-4 text-center font-bold">Status</th>
              <th class="px-6 py-4 text-center font-bold">Veredito</th>
              <th class="px-6 py-4 text-left font-bold">Data</th>
              <th class="px-6 py-4 text-center font-bold">Ações</th>
            </tr>
          </thead>

          <tbody class="divide-y divide-gray-100">
            <tr v-for="item in filteredList" :key="item.id" class="hover:bg-gray-50 transition-colors">
              <td class="px-6 py-4 text-sm font-bold text-blue-600">{{ item.id }}</td>
              <td class="px-6 py-4 text-sm font-medium">{{ item.nome }}</td>
              <td class="px-6 py-4 text-sm text-gray-500">{{ item.tipo }}</td>
              <td class="px-6 py-4 text-center">
                <span :class="statusClass(item.status)">{{ item.status }}</span>
              </td>
              <td class="px-6 py-4 text-center">
                <span :class="vereditoClass(item.veredito)">{{ item.veredito }}</span>
              </td>
              <td class="px-6 py-4 text-xs text-gray-400">{{ item.data }}</td>
              <td class="px-6 py-4">
                <div class="flex items-center justify-center gap-2">
                  <button @click="deleteOrder(item.id)" class="p-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-600 hover:text-white transition-all active:scale-90">
                    <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-width="2" stroke-linecap="round" d="M4 6h16M9 6V4h6v2M7 6v13a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V6M10 11v6M14 11v6"/>
                    </svg>
                  </button>
                  <button class="p-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-600 hover:text-white transition-all active:scale-90">
                    <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-width="2" stroke-linecap="round" d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8S1 12 1 12Z"/>
                      <circle cx="12" cy="12" r="3" stroke-width="2"/>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { 
  search, selectedStatus, statusList, filteredList, 
  handleStatus, statusClass, vereditoClass, deleteOrder 
} from './orders'
</script>

<style scoped>
@import "./orders.css";
</style>