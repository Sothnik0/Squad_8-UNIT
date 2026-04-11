<template>
  <div class="min-h-screen bg-gray-50 p-8 text-slate-700">
    <div class="max-w-5xl mx-auto">
      <header class="mb-8">
        <h1 class="text-2xl font-bold text-slate-800">Análise de Documento</h1>
        <p class="text-slate-500 text-sm">Envie um documento para análise de segurança com IA</p>
      </header>

      <div class="bg-blue-50 border border-blue-100 p-3 rounded-lg flex items-center gap-3 mb-6">
        <span class="text-red-500 font-bold text-lg">*</span>
        <p class="text-blue-700 text-sm font-medium">Este símbolo indica campo obrigatório</p>
      </div>

      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-8 mb-6">
        <h3 class="text-lg font-semibold mb-6">Informações da Solicitação</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-2">
            <label class="text-sm font-medium">Nome do Solicitante *</label>
            <input
              v-model="nomeSolicitante"
              type="text"
              placeholder="Nome completo"
              class="w-full p-3 bg-gray-50 border rounded-lg outline-none transition"
              :class="erros.nome ? 'border-red-500 ring-1 ring-red-500' : 'border-gray-200 focus:ring-2 focus:ring-blue-500'"
            />
            <p v-if="erros.nome" class="text-xs text-red-500 font-medium">{{ erros.nome }}</p>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium">Departamento</label>
            <input
              v-model="departamento"
              type="text"
              placeholder="Ex: Secretaria Acadêmica"
              class="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition"
            />
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium">Tipo de Documento *</label>
            <select
              v-model="tipoDocumento"
              class="w-full p-3 bg-gray-50 border rounded-lg outline-none transition"
              :class="erros.tipo ? 'border-red-500 ring-1 ring-red-500' : 'border-gray-200 focus:ring-2 focus:ring-blue-500'"
            >
              <option value="">Selecione o tipo</option>
              <option value="certificado">Certificado Técnico</option>
              <option value="identidade">Documento de Identidade</option>
            </select>
            <p v-if="erros.tipo" class="text-xs text-red-500 font-medium">{{ erros.tipo }}</p>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium">Descrição Adicional</label>
            <input
              v-model="descricao"
              type="text"
              placeholder="Informações extras sobre o documento"
              class="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition"
            />
          </div>
        </div>
      </div>

      <div
        @click="triggerFile"
        class="group border-2 border-dashed rounded-xl p-12 bg-white transition-all cursor-pointer text-center mb-4"
        :class="erros.arquivo ? 'border-red-400 bg-red-50' : 'border-gray-200 hover:border-blue-400 hover:bg-blue-50'"
      >
        <input type="file" ref="fileInput" class="hidden" @change="onFileChange" />

        <div v-if="!file" class="flex flex-col items-center">
          <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition">
            <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
          </div>
          <p class="text-lg font-medium">Clique para selecionar o documento</p>
          <p class="text-sm text-gray-400 mt-1">PDF, JPG, JPEG, PNG (máx. 10MB)</p>
        </div>

        <div v-else class="flex flex-col items-center text-green-600 font-medium">
          <svg class="w-16 h-16 mb-2" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9 2a2 2 0 00-2 2v8a2 2 0 002 2h6a2 2 0 002-2V6.414A2 2 0 0016.414 5L14 2.586A2 2 0 0012.586 2H9z" />
            <path d="M3 8a2 2 0 012-2v10h8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z" />
          </svg>
          <span class="mb-2">{{ file.name }}</span>
          <button @click.stop="removeFile" class="text-xs text-red-500 underline hover:text-red-700 transition">Remover arquivo</button>
        </div>
      </div>

      <div v-if="erros.arquivo" class="mb-8 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2">
        <span class="text-red-600 font-bold">!</span>
        <p class="text-red-700 text-sm font-bold">{{ erros.arquivo }}</p>
      </div>

      <div class="flex gap-4 mb-8">
        <button
          @click="startAnalysis"
          :disabled="isAnalyzing"
          class="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white font-bold py-3 px-10 rounded-xl shadow-lg transition-all flex items-center gap-2"
        >
          <span v-if="isAnalyzing" class="animate-spin text-xl">⏳</span>
          <span v-else>🛡️</span>
          {{ isAnalyzing ? 'IA Analisando...' : 'Analisar Documento' }}
        </button>
      </div>

      <transition name="fade">
        <div v-if="isAnalyzed && !isAnalyzing" class="mt-10 space-y-6 pb-20">
          
          <div class="bg-red-50 border border-red-200 p-6 rounded-xl flex items-start gap-4 shadow-sm">
            <div class="bg-red-600 p-3 rounded-lg text-white">⚠️</div>
            <div class="flex-1">
              <h3 class="text-red-900 font-bold text-lg leading-tight">Probabilidade de Fraude Detectada</h3>
              <p class="text-red-700 text-sm">Inconsistências detectadas pela inteligência artificial.</p>
            </div>
            <div class="text-right">
              <span class="text-red-600 font-black text-3xl">89%</span>
              <p class="text-red-400 text-[10px] font-bold uppercase">Confiança</p>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4">
            <button class="bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-4 rounded-xl shadow-lg transition-all flex items-center justify-center gap-2">
              <span>✅</span> Aceitar Documento
            </button>
            <button class="bg-rose-600 hover:bg-rose-700 text-white font-bold py-4 rounded-xl shadow-lg transition-all flex items-center justify-center gap-2">
              <span>✖</span> Rejeitar Documento
            </button>
          </div>

          <div class="bg-blue-600 p-6 rounded-2xl shadow-xl flex flex-col md:flex-row items-center justify-between gap-4 animate-pulse-subtle">
            <div class="flex items-center gap-4 text-white">
              <span class="text-3xl">🧐</span>
              <div>
                <h4 class="font-bold text-lg text-white">Deseja realizar a perícia manual?</h4>
                <p class="text-blue-100 text-sm">Visualize o documento e valide nos links oficiais.</p>
              </div>
            </div>
            <button @click="openManualAnalysis" class="bg-white text-blue-600 px-8 py-3 rounded-xl font-bold hover:bg-blue-50 transition-colors shadow-sm">
              Visualizar e Periciar
            </button>
          </div>
        </div>
      </transition>

      <div v-if="showDocModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 text-left">
        <div class="bg-white w-full max-w-5xl h-[90vh] rounded-2xl overflow-hidden flex flex-col shadow-2xl">
          <div class="p-4 border-b flex justify-between items-center bg-slate-50">
            <div>
              <h3 class="font-bold text-slate-800">Visualizando: {{ file?.name }}</h3>
              <p class="text-xs text-slate-500 italic">Analise o documento antes de tomar sua decisão final.</p>
            </div>
            <button @click="showDocModal = false" class="bg-slate-200 hover:bg-slate-300 text-slate-600 font-bold py-2 px-6 rounded-lg transition">Fechar</button>
          </div>
          <div class="flex-1 flex flex-col md:flex-row overflow-hidden">
            <div class="flex-1 bg-slate-200">
              <iframe :src="fileUrl" class="w-full h-full border-none"></iframe>
            </div>
            <div class="w-full md:w-72 bg-white border-l p-6 flex flex-col gap-4 overflow-y-auto">
              <h4 class="text-xs font-bold text-slate-400 uppercase tracking-widest">Validadores</h4>
              <RouterLink to="/links" target="_blank" class="p-3 bg-blue-50 border border-blue-100 rounded-xl hover:bg-blue-100 transition text-sm font-bold text-blue-700 text-center">
                🔗 Abrir Central de Links
              </RouterLink>
              <div class="text-xs text-slate-500 mt-4 leading-relaxed bg-slate-50 p-4 rounded-lg">
                <strong>Dica de Perícia:</strong><br><br>
                1. Verifique se o nome no documento coincide com o solicitado.<br><br>
                2. Consulte assinaturas e selos de autenticidade nos sites oficiais.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { 
    nomeSolicitante, departamento, tipoDocumento, descricao,
    fileInput, file, fileUrl, isAnalyzing, isAnalyzed, showDocModal, erros,
    triggerFile, onFileChange, removeFile, startAnalysis, openManualAnalysis 
  } from './analysis'
</script>

<style scoped>
  @import "./analysis.css";
</style>