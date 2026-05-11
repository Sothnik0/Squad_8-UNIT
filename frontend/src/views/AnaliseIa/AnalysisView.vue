<template>
  <div class="min-h-screen bg-gray-50 p-8 text-slate-700">
    <div class="mx-auto max-w-5xl">
      <header class="mb-8">
        <h1 class="text-2xl font-bold text-slate-800 text-left">Análise de Documento</h1>
        <p class="text-sm text-slate-500 text-left">Envie o arquivo, acompanhe o score e veja exatamente o que levou o sistema a essa conclusão.</p>
      </header>

      <!-- Banner de Aviso -->
      <div class="mb-6 flex items-center gap-3 rounded-lg border border-blue-100 bg-blue-50 p-3 text-left">
        <span class="text-lg font-bold text-red-500">*</span>
        <p class="text-sm font-medium text-blue-700">Este símbolo indica campo obrigatório</p>
      </div>

      <!-- Formulário de Informações -->
      <div class="mb-6 rounded-xl border border-gray-100 bg-white p-8 shadow-sm text-left">
        <h3 class="mb-6 text-lg font-semibold text-slate-800">Informações da Solicitação</h3>

        <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
          <div class="space-y-2">
            <label class="text-sm font-medium">Nome do solicitante *</label>
            <input
              v-model="nomeSolicitante"
              type="text"
              placeholder="Nome completo"
              class="w-full rounded-lg border bg-gray-50 p-3 outline-none transition"
              :class="erros.nome ? 'border-red-500 ring-1 ring-red-500' : 'border-gray-200 focus:ring-2 focus:ring-blue-500'"
            />
            <p v-if="erros.nome" class="text-xs font-medium text-red-500">{{ erros.nome }}</p>
          </div>
          <div class="space-y-2">
            <label class="text-sm font-medium">Tipo de documento *</label>
            <select
              v-model="tipoDocumento"
              class="w-full rounded-lg border bg-gray-50 p-3 outline-none transition"
              :class="erros.tipo ? 'border-red-500 ring-1 ring-red-500' : 'border-gray-200 focus:ring-2 focus:ring-blue-500'"
            >
              <option value="">Selecione</option>
              <option value="atestado_medico">Atestado médico</option>
              <option value="certificado_ensino_medio">Certificado de conclusão do ensino médio</option>
              <option value="historico_escolar">Histórico escolar</option>
            </select>
            <p v-if="erros.tipo" class="text-xs font-medium text-red-500">{{ erros.tipo }}</p>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium">Descrição adicional</label>
            <input
              v-model="descricao"
              type="text"
              placeholder="Informações extras sobre o documento"
              class="w-full rounded-lg border border-gray-200 bg-gray-50 p-3 outline-none transition focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      <!-- Área de Upload -->
      <div
        class="group mb-4 cursor-pointer rounded-xl border-2 border-dashed bg-white p-12 text-center transition-all"
        :class="erros.arquivo ? 'border-red-400 bg-red-50' : 'border-gray-200 hover:border-blue-400 hover:bg-blue-50'"
        @click="triggerFile"
      >
        <input ref="fileInput" type="file" class="hidden" accept=".pdf,.jpg,.jpeg,.png" @change="onFileChange" />

        <div v-if="!file" class="flex flex-col items-center">
          <div class="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-blue-100 transition group-hover:scale-110">
            <svg class="h-8 w-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
          </div>
          <p class="text-lg font-medium">Clique para selecionar o documento</p>
          <p class="mt-1 text-sm text-gray-400">PDF, JPG, JPEG, PNG (máx. 10MB)</p>
        </div>

        <div v-else class="flex flex-col items-center font-medium text-green-600">
          <svg class="mb-2 h-16 w-16" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9 2a2 2 0 00-2 2v8a2 2 0 002 2h6a2 2 0 002-2V6.414A2 2 0 0016.414 5L14 2.586A2 2 0 0012.586 2H9z" />
            <path d="M3 8a2 2 0 012-2v10h8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z" />
          </svg>
          <span class="mb-2 break-all px-4">{{ file.name }}</span>
          <button class="text-xs text-red-500 underline transition hover:text-red-700" @click.stop="removeFile">Remover arquivo</button>
        </div>
      </div>

      <!-- Mensagens de Erro -->
      <div v-if="erros.arquivo || apiError" class="mb-8 space-y-2">
        <div v-if="erros.arquivo" class="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 p-3 text-left">
          <span class="font-bold text-red-600">!</span>
          <p class="text-sm font-bold text-red-700">{{ erros.arquivo }}</p>
        </div>
        <div v-if="apiError" class="rounded-lg border border-red-200 bg-red-50 p-4 text-left text-sm font-semibold text-red-700">
          {{ apiError }}
        </div>
      </div>

      <!-- Ação Principal -->
      <div class="mb-8 flex">
        <button
          :disabled="isAnalyzing"
          class="flex items-center gap-2 rounded-xl bg-blue-600 px-10 py-3 font-bold text-white shadow-lg transition-all hover:bg-blue-700 disabled:bg-slate-300"
          @click="startAnalysis"
        >
          <span v-if="isAnalyzing" class="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></span>
          {{ isAnalyzing ? 'Analisando documento...' : 'Analisar documento' }}
        </button>
      </div>

      <!-- Resultados da Análise -->
      <transition name="fade">
        <div v-if="isAnalyzed && !isAnalyzing && analysisResult" class="mt-10 space-y-6 pb-20">

          <!-- Card de Probabilidade -->
          <div class="flex flex-col gap-4 rounded-xl border p-6 shadow-sm md:flex-row md:items-start md:justify-between text-left" :class="riskTone">
            <div class="flex-1">
              <p class="mb-1 text-xs font-bold uppercase tracking-widest">Protocolo {{ analysisResult.protocolo }}</p>
              <h3 class="text-lg font-bold leading-tight">Probabilidade de fraude</h3>
              <p class="mt-1 text-sm">{{ analysisResult.resumo }}</p>
            </div>
            <div class="text-left md:text-right">
              <span class="text-4xl font-black">{{ analysisResult.probabilidade_fraude }}%</span>
              <p class="text-xs font-bold uppercase">Risco estimado</p>
            </div>
          </div>

          <!-- Grade de Informações Detalhadas -->
          <div class="grid grid-cols-1 gap-6 md:grid-cols-2">

            <!-- Dados Encontrados (Com Ver Mais) -->
            <section class="rounded-xl border border-gray-100 bg-white p-6 shadow-sm text-left">
              <h4 class="mb-4 font-bold text-slate-800">Dados encontrados e pendências</h4>
              <div class="space-y-3">
                <div v-for="item in dadosExibidos" :key="item.titulo" class="rounded-lg border border-gray-100 p-4">
                  <div class="mb-2 flex items-center justify-between gap-3">
                    <p class="font-semibold text-slate-800">{{ item.titulo }}</p>
                    <span class="rounded-full px-3 py-1 text-xs font-bold" :class="statusClass(item.status)">
                      {{ statusLabel(item.status) }}
                    </span>
                  </div>
                  <p class="text-sm text-slate-500">{{ item.detalhe }}</p>
                </div>
              </div>

              <div v-if="temMaisDados" class="mt-4">
                <button
                  @click="mostrarTodosDados = !mostrarTodosDados"
                  class="flex w-full items-center justify-center gap-2 rounded-lg border border-slate-200 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-50"
                >
                  <span>{{ mostrarTodosDados ? 'Ver menos' : `Ver mais (${analysisResult.dados_chave.length - 4} ocultos)` }}</span>
                  <svg class="h-4 w-4 transition-transform" :class="{ 'rotate-180': mostrarTodosDados }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </div>
            </section>

            <!-- Verificações Oficiais -->
            <section class="rounded-xl border border-gray-100 bg-white p-6 shadow-sm text-left">
              <h4 class="mb-4 font-bold text-slate-800">Verificações executadas</h4>
              <div class="space-y-3">
                <div v-for="item in analysisResult.verificacoes_oficiais" :key="item.titulo" class="rounded-lg border border-gray-100 p-4">
                  <div class="mb-2 flex items-center justify-between gap-3">
                    <p class="font-semibold text-slate-800">{{ item.titulo }}</p>
                    <span class="rounded-full px-3 py-1 text-xs font-bold" :class="statusClass(item.status)">
                      {{ statusLabel(item.status) }}
                    </span>
                  </div>
                  <p class="text-sm text-slate-500">{{ item.detalhe }}</p>
                </div>
              </div>
            </section>
          </div>

          <!-- OCR e Texto Bruto -->
          <div class="grid grid-cols-1 gap-6 md:grid-cols-2 text-left">
            <section class="rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
              <h4 class="mb-2 font-bold text-slate-800">Camada de extração</h4>
              <p class="text-sm text-slate-500">Origem principal dos dados exibidos no relatório.</p>
              <div class="mt-4 rounded-lg border border-blue-100 bg-blue-50 p-4">
                <p class="text-xs font-bold uppercase tracking-widest text-blue-700">Motor utilizado</p>
                <p class="mt-1 text-sm font-semibold text-blue-900">{{ analysisResult.motor_extracao || 'Google Gemini 2.0 Flash' }}</p>
              </div>
            </section>

            <section class="rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
              <h4 class="mb-2 font-bold text-slate-800 text-left">Texto extraído do documento</h4>
              <p class="text-sm text-slate-500">Trecho bruto lido pelo OCR para conferência.</p>
              <pre class="mt-4 max-h-40 overflow-auto rounded-lg bg-slate-950 p-4 text-xs leading-relaxed text-slate-100 whitespace-pre-wrap">{{ analysisResult.texto_extraido || 'Nenhum texto OCR disponível.' }}</pre>
            </section>
          </div>

          <!-- Ações Finais -->
          <div class="grid grid-cols-1 gap-4 pt-4 md:grid-cols-2">
            <button class="rounded-xl bg-emerald-600 py-4 font-bold text-white shadow-lg transition-all hover:bg-emerald-700 active:scale-95">Aceitar documento</button>
            <button class="rounded-xl bg-rose-600 py-4 font-bold text-white shadow-lg transition-all hover:bg-rose-700 active:scale-95">Rejeitar documento</button>
          </div>

          <!-- CTA Perícia Manual -->
          <div class="flex flex-col items-center justify-between gap-4 rounded-2xl bg-blue-600 p-8 shadow-xl md:flex-row text-left">
            <div class="text-white">
              <h4 class="text-xl font-bold">Deseja realizar a perícia manual?</h4>
              <p class="text-blue-100">Visualize o documento original e confira os selos de autenticidade.</p>
            </div>
            <button class="rounded-xl bg-white px-8 py-3 font-bold text-blue-600 shadow-sm transition-colors hover:bg-blue-50" @click="openManualAnalysis">
              Visualizar documento
            </button>
          </div>
        </div>
      </transition>

      <!-- Modal Visualizador de Documento -->
      <div v-if="showDocModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 text-left backdrop-blur-sm">
        <div class="flex h-[90vh] w-full max-w-5xl flex-col overflow-hidden rounded-2xl bg-white shadow-2xl">
          <div class="flex items-center justify-between border-b bg-slate-50 p-4">
            <div>
              <h3 class="font-bold text-slate-800">Visualizando: {{ file?.name }}</h3>
              <p class="text-xs italic text-slate-500">Confira o documento antes de tomar a decisão final.</p>
            </div>
            <button class="rounded-lg bg-slate-200 px-6 py-2 font-bold text-slate-600 transition hover:bg-slate-300" @click="showDocModal = false">Fechar</button>
          </div>
          <div class="flex flex-1 flex-col overflow-hidden md:flex-row">
            <div class="flex-1 bg-slate-200">
              <iframe :src="fileUrl" class="h-full w-full border-none"></iframe>
            </div>
            <div class="flex w-full flex-col gap-4 overflow-y-auto border-l bg-white p-6 md:w-72">
              <h4 class="text-xs font-bold uppercase tracking-widest text-slate-400">Checklist de Perícia</h4>
              <div class="rounded-xl border border-slate-100 bg-slate-50 p-4 text-xs leading-relaxed text-slate-600">
                1. O nome no documento é idêntico ao solicitado?<br /><br />
                2. Há sinais de edição digital (fontes diferentes, borrões)?<br /><br />
                3. O carimbo/assinatura parece legítimo?<br /><br />
                4. A data de emissão é coerente?
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  nomeSolicitante,
  tipoDocumento,
  descricao,
  fileInput,
  file,
  fileUrl,
  isAnalyzing,
  isAnalyzed,
  showDocModal,
  erros,
  analysisResult,
  apiError,
  triggerFile,
  onFileChange,
  removeFile,
  startAnalysis,
  openManualAnalysis,
  type AnalysisFinding,
} from './analysis'

// --- Lógica Visual de Expansão ---
const mostrarTodosDados = ref(false)

const dadosExibidos = computed(() => {
  const dados = analysisResult.value?.dados_chave || []
  return mostrarTodosDados.value ? dados : dados.slice(0, 4)
})

const temMaisDados = computed(() => {
  return (analysisResult.value?.dados_chave?.length || 0) > 4
})

// --- Helpers de Estilização ---
const riskTone = computed(() => {
  const probability = analysisResult.value?.probabilidade_fraude ?? 0
  if (probability >= 70) return 'border-red-200 bg-red-50 text-red-800'
  if (probability >= 40) return 'border-amber-200 bg-amber-50 text-amber-800'
  return 'border-emerald-200 bg-emerald-50 text-emerald-800'
})

const statusLabel = (status: AnalysisFinding['status']) => {
  const labels = {
    encontrado: 'Encontrado',
    nao_encontrado: 'Não encontrado',
    pendente: 'Pendente',
    alerta: 'Alerta',
  }
  return labels[status]
}

const statusClass = (status: AnalysisFinding['status']) => {
  const classes = {
    encontrado: 'bg-emerald-100 text-emerald-700',
    nao_encontrado: 'bg-slate-100 text-slate-600',
    pendente: 'bg-blue-100 text-blue-700',
    alerta: 'bg-amber-100 text-amber-700',
  }
  return classes[status]
}
</script>

<style scoped>
@import './analysis.css';

.fade-enter-active, .fade-leave-active { transition: opacity 0.4s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
