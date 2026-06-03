<template>
  <div class="min-h-screen bg-gray-50 dark:bg-slate-900 p-10 text-slate-700 dark:text-slate-300 dark:text-slate-200 font-sans transition-colors duration-300">
    <div class="mx-auto max-w-6xl">
      <header class="mb-10 flex items-start justify-between">
        <div>
          <h1 class="text-4xl font-extrabold text-slate-800 dark:text-slate-100 text-left tracking-tight">
            Análise de Documento
          </h1>

          <p class="text-base text-slate-500 dark:text-slate-400 text-left mt-2">
            Envie o arquivo, acompanhe o score e veja exatamente o que levou o sistema a essa conclusão.
          </p>
        </div>

        <button
          @click="toggleDarkMode"
          class="px-4 py-2 rounded-xl bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-100 font-semibold transition-all hover:scale-105"
        >
          {{ darkMode ? '☀️ Light' : '🌙 Dark' }}
        </button>
      </header>

      <div class="mb-8 flex items-center gap-4 rounded-xl border border-blue-100 dark:border-blue-800 bg-blue-50 dark:bg-blue-950/40 p-4 text-left">
        <span class="text-xl font-bold text-red-500">*</span>
        <p class="text-base font-medium text-blue-700 dark:text-blue-300"> símbolo indica campo obrigatório</p>
      </div>

      <div class="mb-8 rounded-xl border border-gray-100 dark:border-slate-700 bg-white dark:bg-slate-800 dark:bg-slate-800 p-10 shadow-sm text-left">
        <h3 class="mb-6 text-xl font-bold text-slate-800 dark:text-slate-100 dark:text-slate-100">Informações da Solicitação</h3>

        <div class="grid grid-cols-1 gap-8 md:grid-cols-2">
          <div class="space-y-2">
            <label class="text-base font-semibold text-slate-700 dark:text-slate-300">Nome do solicitante *</label>
            <input
              v-model="nomeSolicitante"
              type="text"
              placeholder="Nome completo"
              class="w-full rounded-lg border bg-gray-50 dark:bg-slate-700 dark:border-slate-600 dark:text-slate-100 p-4 text-base outline-none transition"
              :class="erros.nome ? 'border-red-500 ring-1 ring-red-500' : 'border-gray-200 dark:border-slate-600 focus:ring-2 focus:ring-blue-500'"
            />
            <p v-if="erros.nome" class="text-xs font-medium text-red-500">{{ erros.nome }}</p>
          </div>
          <div class="space-y-2">
            <label class="text-base font-semibold text-slate-700 dark:text-slate-300">Tipo de documento *</label>
            <select
              v-model="tipoDocumento"
              class="w-full rounded-lg border bg-gray-50 dark:bg-slate-700 dark:border-slate-600 dark:text-slate-100 p-4 text-base outline-none transition"
              :class="erros.tipo ? 'border-red-500 ring-1 ring-red-500' : 'border-gray-200 dark:border-slate-600 focus:ring-2 focus:ring-blue-500'"
            >
              <option value="">Selecione</option>
              <option value="atestado_medico">Atestado médico</option>
              <option value="certificado_ensino_medio">Certificado de conclusão do ensino médio</option>
              <option value="historico_escolar">Histórico escolar</option>
              <option value="diploma">Diploma de graduação</option>
            </select>
            <p v-if="erros.tipo" class="text-xs font-medium text-red-500">{{ erros.tipo }}</p>
          </div>

          <div class="space-y-2 md:col-span-2">
            <label class="text-base font-semibold text-slate-700 dark:text-slate-300">Descrição adicional</label>
            <input
              v-model="descricao"
              type="text"
              placeholder="Informações extras sobre o documento"
              class="w-full rounded-lg border border-gray-200 dark:border-slate-600 dark:border-slate-600 bg-gray-50 dark:bg-slate-700 dark:text-slate-100 p-4 text-base outline-none transition focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      <div
        class="group mb-6 cursor-pointer rounded-xl border-2 border-dashed bg-white dark:bg-slate-800 p-14 text-center transition-all hover:shadow-md"
        :class="erros.arquivo ? 'border-red-400 bg-red-50' : 'border-gray-200 dark:border-slate-600 hover:border-blue-400 hover:bg-blue-50'"
        @click="triggerFile"
      >
        <input ref="fileInput" type="file" class="hidden" accept=".pdf,.jpg,.jpeg,.png" @change="onFileChange" />

        <div v-if="!file" class="flex flex-col items-center">
          <div class="mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-blue-100 transition group-hover:scale-110">
            <svg class="h-10 w-10 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
          </div>
          <p class="text-xl font-bold text-slate-800 dark:text-slate-100 dark:text-slate-100">Clique para selecionar o documento</p>
          <p class="mt-2 text-base text-gray-400 dark:text-slate-500 dark:text-slate-400">, JPG, JPEG, PNG (máx. 10MB)</p>
        </div>

        <div v-else class="flex flex-col items-center font-bold text-green-600">
          <svg class="mb-3 h-20 w-20" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9 2a2 2 0 00-2 2v8a2 2 0 002 2h6a2 2 0 002-2V6.414A2 2 0 0016.414 5L14 2.586A2 2 0 0012.586 2H9z" />
            <path d="M3 8a2 2 0 012-2v10h8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z" />
          </svg>
          <span class="mb-3 break-all px-4 text-base">{{ file.name }}</span>
          <button class="text-sm text-red-500 underline transition hover:text-red-700 cursor-pointer" @click.stop="removeFile">Remover arquivo</button>
        </div>
      </div>

      <div v-if="erros.arquivo || apiError" class="mb-8 space-y-3">
        <div v-if="erros.arquivo" class="flex items-center gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-left">
          <span class="font-bold text-red-600 text-lg">!</span>
          <p class="text-base font-bold text-red-700">{{ erros.arquivo }}</p>
        </div>
        <div v-if="apiError" class="rounded-lg border border-red-200 bg-red-50 p-4 text-left text-base font-bold text-red-700">
          {{ apiError }}
        </div>
      </div>

      <div class="mb-10 flex">
        <button
          :disabled="isAnalyzing"
          class="flex items-center gap-3 rounded-xl bg-blue-600 px-12 py-4 font-bold text-lg text-white shadow-lg transition-all hover:bg-blue-700 active:scale-95 disabled:bg-slate-300 cursor-pointer"
          @click="startAnalysis"
        >
          <span v-if="isAnalyzing" class="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent"></span>
          {{ isAnalyzing ? 'Analisando documento...' : 'Analisar documento' }}
        </button>
      </div>

      <transition name="fade">
        <div v-if="isAnalyzed && !isAnalyzing && analysisResult" class="mt-12 space-y-8 pb-20">

          <div class="flex flex-col gap-6 rounded-xl border p-8 shadow-sm md:flex-row md:items-start md:justify-between text-left transition-all duration-300 hover:shadow-md" :class="riskTone">
            <div class="flex-1">
              <p class="mb-2 text-sm font-bold uppercase tracking-widest opacity-70">Protocolo {{ analysisResult.protocolo }}</p>
              <h3 class="text-2xl font-black leading-tight">{{ scoreLabel }}</h3>
              <p class="mt-2 text-base opacity-80">{{ analysisResult.resumo }}</p>
            </div>
            <div class="text-left md:text-right shrink-0">
              <span class="text-6xl font-black">{{ analysisResult.probabilidade_fraude }}%</span>
              <p class="text-xs font-bold uppercase opacity-70 mt-1">Score de autenticidade</p>
              <p class="text-sm font-bold mt-1 opacity-90">{{ scoreDesc }}</p>
            </div>
          </div>

          <div class="grid grid-cols-1 gap-8 md:grid-cols-2">

            <section class="rounded-xl border border-gray-100 dark:border-slate-700 bg-white dark:bg-slate-800 dark:bg-slate-800 p-8 shadow-sm text-left cursor-pointer transition-all duration-500 hover:shadow-xl hover:shadow-blue-500/10 hover:-translate-y-1.5 hover:border-slate-200">
              <h4 class="mb-5 font-bold text-slate-800 dark:text-slate-100 text-xl">Dados encontrados e pendências</h4>
              <div class="space-y-4">
                <div v-for="item in dadosExibidos" :key="item.titulo" class="rounded-lg border border-gray-100 p-5 transition-all duration-200 bg-slate-50/30 hover:bg-white dark:bg-slate-800 hover:border-slate-300 hover:shadow-sm">
                  <div class="mb-2 flex items-center justify-between gap-3">
                    <p class="font-bold text-slate-800 dark:text-slate-100 text-base">{{ item.titulo }}</p>
                    <span class="rounded-full px-3 py-1 text-xs font-bold" :class="statusClass(item.status)">
                      {{ statusLabel(item.status) }}
                    </span>
                  </div>
                  <p class="text-sm text-slate-500 dark:text-slate-400">{{ item.detalhe }}</p>
                </div>
              </div>

              <div v-if="temMaisDados" class="mt-5">
                <button
                  @click="mostrarTodosDados = !mostrarTodosDados"
                  class="flex w-full items-center justify-center gap-2 rounded-lg border border-slate-200 py-3 text-sm font-bold text-slate-600 dark:text-slate-300 transition hover:bg-slate-50 cursor-pointer"
                >
                  <span>{{ mostrarTodosDados ? 'Ver menos' : `Ver mais (${analysisResult.dados_chave.length - 4} ocultos)` }}</span>
                  <svg class="h-4 w-4 transition-transform" :class="{ 'rotate-180': mostrarTodosDados }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </div>
            </section>

            <section class="rounded-xl border border-gray-100 dark:border-slate-700 bg-white dark:bg-slate-800 dark:bg-slate-800 p-8 shadow-sm text-left cursor-pointer transition-all duration-500 hover:shadow-xl hover:shadow-blue-500/10 hover:-translate-y-1.5 hover:border-slate-200">
              <h4 class="mb-5 font-bold text-slate-800 dark:text-slate-100 text-xl">Verificações executadas</h4>
              <div class="space-y-4">
                <div
                  v-for="item in verificacoesExibidas"
                  :key="item.titulo"
                  class="rounded-lg border border-gray-100 p-5 transition-all duration-200 bg-slate-50/30 hover:bg-white dark:bg-slate-800 hover:border-slate-300 hover:shadow-sm"
                >
                  <div class="mb-2 flex items-center justify-between gap-3">
                    <p class="font-bold text-slate-800 dark:text-slate-100 text-base">{{ item.titulo }}</p>
                    <span class="shrink-0 rounded-full px-3 py-1 text-xs font-bold" :class="statusClass(item.status)">
                      {{ statusLabel(item.status) }}
                    </span>
                  </div>
                  <p class="text-sm text-slate-500 dark:text-slate-400">{{ item.detalhe }}</p>

                  <div
                    v-if="nextAction(item.status, item.titulo)"
                    class="mt-3 flex items-start gap-2 rounded-md border-l-4 pl-3 py-2 bg-white dark:bg-slate-800"
                    :class="actionBorderClass(item.status)"
                  >
                    <span class="text-base leading-none mt-0.5">{{ actionIcon(item.status) }}</span>
                    <p class="text-xs font-semibold leading-relaxed" :class="actionTextClass(item.status)">
                      {{ nextAction(item.status, item.titulo) }}
                    </p>
                  </div>
                </div>
              </div>

              <div v-if="temMaisVerificacoes" class="mt-5">
                <button
                  @click="mostrarTodasVerificacoes = !mostrarTodasVerificacoes"
                  class="flex w-full items-center justify-center gap-2 rounded-lg border border-slate-200 py-3 text-sm font-bold text-slate-600 dark:text-slate-300 transition hover:bg-slate-50 cursor-pointer"
                >
                  <span>{{ mostrarTodasVerificacoes ? 'Ver menos' : `Ver mais (${analysisResult.verificacoes_oficiais.length - 4} ocultos)` }}</span>
                  <svg class="h-4 w-4 transition-transform" :class="{ 'rotate-180': mostrarTodasVerificacoes }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </div>
            </section>
          </div>

          <div class="grid grid-cols-1 gap-8 md:grid-cols-2 text-left">
            <section class="rounded-xl border border-gray-100 dark:border-slate-700 bg-white dark:bg-slate-800 dark:bg-slate-800 p-8 shadow-sm transition-all duration-300 hover:shadow-md">
              <h4 class="mb-2 font-bold text-slate-800 dark:text-slate-100 text-xl">Camada de extração</h4>
              <p class="text-sm text-slate-500 dark:text-slate-400">Origem principal dos dados exibidos no relatório.</p>
              <div class="mt-5 rounded-lg border border-blue-100 bg-blue-50 p-5">
                <p class="text-xs font-bold uppercase tracking-widest text-blue-700">Motor utilizado</p>
                <p class="mt-1 text-base font-bold text-blue-900">{{ analysisResult.motor_extracao || 'Google Gemini 2.0 Flash' }}</p>
              </div>
            </section>

            <section class="rounded-xl border border-gray-100 dark:border-slate-700 bg-white dark:bg-slate-800 dark:bg-slate-800 p-8 shadow-sm transition-all duration-300 hover:shadow-md">
              <h4 class="mb-2 font-bold text-slate-800 dark:text-slate-100 text-xl">Texto extraído do documento</h4>
              <p class="text-sm text-slate-500 dark:text-slate-400">Trecho bruto lido pelo OCR para conferência.</p>
              <pre class="mt-5 max-h-48 overflow-auto rounded-lg bg-slate-950 p-5 text-sm leading-relaxed text-slate-100 whitespace-pre-wrap font-mono">{{ analysisResult.texto_extraido || 'Nenhum texto OCR disponível.' }}</pre>
            </section>
          </div>

          <div class="grid grid-cols-1 gap-6 pt-4 md:grid-cols-2">
            <button class="rounded-xl bg-emerald-600 py-5 font-bold text-lg text-white shadow-lg transition-all hover:bg-emerald-700 active:scale-98 cursor-pointer">Aceitar documento</button>
            <button class="rounded-xl bg-rose-600 py-5 font-bold text-lg text-white shadow-lg transition-all hover:bg-rose-700 active:scale-98 cursor-pointer">Rejeitar documento</button>
          </div>

          <div class="flex flex-col items-center justify-between gap-6 rounded-2xl bg-blue-600 p-10 shadow-xl md:flex-row text-left">
            <div class="text-white">
              <h4 class="text-2xl font-black">Deseja realizar a perícia manual?</h4>
              <p class="text-blue-100 text-base mt-1">Visualize o documento original e confira os selos de autenticidade.</p>
            </div>
            <button class="rounded-xl bg-white dark:bg-slate-800 px-10 py-4 font-bold text-base text-blue-600 shadow-md transition-colors hover:bg-blue-50 cursor-pointer shrink-0" @click="openModal">
              Visualizar documento
            </button>
          </div>
        </div>
      </transition>

      <div v-if="showDocModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-3 backdrop-blur-sm">
        <div class="flex w-full max-w-6xl flex-col overflow-hidden rounded-2xl bg-white dark:bg-slate-800 shadow-2xl" style="height: 95vh;">

          <div class="flex flex-shrink-0 items-center justify-between border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 px-5 py-4">
            <div>
              <h3 class="font-bold text-xl text-slate-800 dark:text-slate-100">{{ file?.name }}</h3>
              <p class="text-xs text-slate-400">Confira o documento antes de tomar a decisão final.</p>
            </div>
            <div class="flex items-center gap-3">
              <div class="flex items-center gap-1 rounded-lg border border-slate-200 bg-white dark:bg-slate-800 px-2 py-1">
                <button @click="zoomOut" class="px-2 py-0.5 text-lg font-bold text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:text-slate-100 transition cursor-pointer" title="Reduzir">−</button>
                <span class="min-w-[3rem] text-center text-xs font-semibold text-slate-600 dark:text-slate-300">{{ zoomLevel }}%</span>
                <button @click="zoomIn"  class="px-2 py-0.5 text-lg font-bold text-slate-500 dark:text-slate-400 hover:text-slate-800 transition cursor-pointer" title="Ampliar">+</button>
                <button @click="zoomReset" class="ml-1 px-2 py-0.5 text-xs font-semibold text-slate-400 hover:text-slate-700 dark:text-slate-300 transition cursor-pointer" title="Resetar">↺</button>
              </div>
              <button class="rounded-lg bg-slate-200 px-5 py-2 text-sm font-bold text-slate-600 dark:text-slate-300 transition hover:bg-slate-300 cursor-pointer" @click="showDocModal = false">Fechar</button>
            </div>
          </div>

          <div class="flex min-h-0 flex-1 overflow-hidden">
            <div class="relative flex-1 overflow-auto bg-slate-700 p-4">
              <div
                class="mx-auto origin-top transition-transform duration-200"
                :style="{ transform: `scale(${zoomLevel / 100})`, transformOrigin: 'top center', width: docIsImage ? 'fit-content' : '100%' }"
              >
                <img
                  v-if="docIsImage"
                  :src="fileUrl"
                  class="block rounded shadow-lg"
                  style="max-width: 680px; width: 100%;"
                  alt="Documento"
                />
                <iframe
                  v-else
                  :src="fileUrl"
                  class="block w-full rounded shadow-lg border-none bg-white dark:bg-slate-800"
                  style="height: 75vh; min-height: 500px;"
                ></iframe>
              </div>
            </div>

            <div class="flex w-64 flex-shrink-0 flex-col gap-4 overflow-y-auto border-l bg-white dark:bg-slate-800 p-5">
              <h4 class="text-xs font-bold uppercase tracking-widest text-slate-400">Checklist de Perícia</h4>
              <div class="space-y-3">
                <label v-for="(item, i) in checklist" :key="i" class="flex cursor-pointer items-start gap-3 rounded-lg border border-slate-100 p-3 hover:bg-slate-50 transition">
                  <input type="checkbox" v-model="item.done" class="mt-0.5 h-4 w-4 rounded accent-blue-600 flex-shrink-0 cursor-pointer" />
                  <span class="text-xs leading-relaxed text-slate-600 dark:text-slate-300" :class="{ 'line-through text-slate-400': item.done }">{{ item.text }}</span>
                </label>
              </div>
              <div class="mt-auto rounded-lg border text-center py-2 text-xs font-bold"
                :class="checklist.every(c => c.done) ? 'border-emerald-200 bg-emerald-50 text-emerald-700' : 'border-slate-200 bg-slate-50 text-slate-400'">
                {{ checklist.filter(c => c.done).length }}/{{ checklist.length }} itens verificados
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
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

// --- Lógica Visual de Expansão ---
const mostrarTodosDados = ref(false)

const dadosExibidos = computed(() => {
  const dados = analysisResult.value?.dados_chave || []
  return mostrarTodosDados.value ? dados : dados.slice(0, 4)
})

const temMaisDados = computed(() => {
  return (analysisResult.value?.dados_chave?.length || 0) > 4
})

// --- Lógica Visual de Expansão (Verificações Executadas) ---
const mostrarTodasVerificacoes = ref(false)

const verificacoesExibidas = computed(() => {
  const verificacoes = analysisResult.value?.verificacoes_oficiais || []
  return mostrarTodasVerificacoes.value ? verificacoes : verificacoes.slice(0, 4)
})

const temMaisVerificacoes = computed(() => {
  return (analysisResult.value?.verificacoes_oficiais?.length || 0) > 4
})

// Zoom e tipo do documento para o modal
const zoomLevel = ref(75)
const zoomIn    = () => { zoomLevel.value = Math.min(zoomLevel.value + 15, 200) }
const zoomOut   = () => { zoomLevel.value = Math.max(zoomLevel.value - 15, 30) }
const zoomReset = () => { zoomLevel.value = 75 }

const docIsImage = computed(() => {
  const name = file.value?.name.toLowerCase() ?? ''
  return name.endsWith('.jpg') || name.endsWith('.jpeg') || name.endsWith('.png')
})

const checklist = ref([
  { text: 'O nome no documento é idêntico ao solicitante?', done: false },
  { text: 'Há sinais de edição digital (fontes diferentes, borrões)?', done: false },
  { text: 'O carimbo/assinatura parece legítimo?', done: false },
  { text: 'A data de emissão é coerente com o período informado?', done: false },
  { text: 'O documento pertence à instituição correta?', done: false },
])

// Reseta checklist ao abrir o modal
const openModal = () => {
  checklist.value.forEach(c => c.done = false)
  zoomLevel.value = 75
  openManualAnalysis()
}

// Score de autenticidade: 75-99 = verídico, 50-74 = verificação, 0-49 = suspeito
const score = computed(() => analysisResult.value?.probabilidade_fraude ?? 0)

const riskTone = computed(() => {
  if (score.value >= 75) return 'border-emerald-200 bg-emerald-50 text-emerald-800'
  if (score.value >= 50) return 'border-amber-200 bg-amber-50 text-amber-800'
  return 'border-red-200 bg-red-50 text-red-800'
})

const scoreLabel = computed(() => {
  if (score.value >= 75) return '✅ Documento provavelmente verídico'
  if (score.value >= 50) return '🟡 Requer verificação externa'
  return '⚠️ Documento suspeito — verificar manualmente'
})

const scoreDesc = computed(() => {
  if (score.value >= 75) return 'Alta confiança na autenticidade'
  if (score.value >= 50) return 'Confirmação manual recomendada'
  return 'Indícios de irregularidade detectados'
})

// Retorna o próximo passo recomendado para cada verificação
const nextAction = (status: string, titulo: string): string => {
  const t = titulo.toLowerCase()
  if (status === 'encontrado') return ''

  if (status === 'alerta') {
    if (t.includes('cnpj'))       return 'Consulte o CNPJ manualmente em receita.fazenda.gov.br e confirme se a instituição está ativa.'
    if (t.includes('cep'))        return 'Verifique o endereço no correios.com.br ou Google Maps e confira com o documento físico.'
    if (t.includes('cpf'))        return 'Solicite o documento de identidade original e confira os dígitos do CPF pessoalmente.'
    if (t.includes('assinatura') || t.includes('carimbo')) return 'Exija a apresentação do documento físico e confira assinatura/carimbo pessoalmente.'
    if (t.includes('crm'))        return 'Consulte o CFM em portal.cfm.org.br > Consulta de Médicos e confirme o CRM e UF.'
    if (t.includes('formatacao')) return 'Compare com um documento original da mesma instituição — repetições suspeitas podem indicar cópia ou adulteração.'
    return 'Investigue o alerta antes de aprovar o documento.'
  }

  if (status === 'nao_encontrado') {
    if (t.includes('cpf'))        return 'Solicite o CPF ao solicitante e confirme com documento de identidade original.'
    if (t.includes('nascimento')) return 'Solicite RG ou certidão de nascimento para cruzar a data com o cadastro.'
    if (t.includes('crm'))        return 'Consulte manualmente em portal.cfm.org.br > Consulta de Médicos.'
    if (t.includes('cnpj'))       return 'Solicite o CNPJ à instituição emissora e valide em receita.fazenda.gov.br.'
    if (t.includes('afastamento') || t.includes('periodo')) return 'Confirme o número de dias diretamente no documento físico ou com o emissor.'
    if (t.includes('hospital') || t.includes('emissor')) return 'Confirme o nome e endereço do local emissor no documento físico.'
    if (t.includes('endereco'))   return 'Solicite o endereço completo ao emissor e verifique no ViaCEP ou Google Maps.'
    if (t.includes('cidade') || t.includes('estado')) return 'Confirme a cidade e estado de emissão no documento físico ou com o emissor.'
    if (t.includes('assinatura') || t.includes('carimbo')) return 'Exija a apresentação física do documento — atestado sem assinatura não tem validade legal.'
    if (t.includes('aluno') || t.includes('paciente')) return 'Confirme a identidade do solicitante com documento original (RG/CPF).'
    if (t.includes('escola') || t.includes('instituicao')) return 'Solicite o nome completo da instituição e pesquise no portal e-MEC ou CNPJ.'
    if (t.includes('disciplina') || t.includes('nota')) return 'Solicite o histórico físico ou verificação junto à secretaria acadêmica.'
    if (t.includes('data'))       return 'Localize a data de emissão no documento físico e confronte com os dados fornecidos.'
    return 'Solicite a informação faltante diretamente ao solicitante ou instituição emissora.'
  }

  if (status === 'pendente') {
    if (t.includes('crm'))        return 'Acesse portal.cfm.org.br > Consulta de Médicos e confirme CRM e UF manualmente.'
    if (t.includes('cnpj'))       return 'Consulte o CNPJ em receita.fazenda.gov.br para confirmar nome e situação cadastral.'
    if (t.includes('cep'))        return 'Confirme o CEP em viacep.com.br ou correios.com.br.'
    if (t.includes('cpf'))        return 'Solicite o CPF e valide os dígitos verificadores manualmente.'
    if (t.includes('nascimento')) return 'Solicite RG ou certidão ao solicitante para cruzar a data de nascimento.'
    if (t.includes('afastamento') || t.includes('periodo')) return 'Localize o número de dias no documento físico e enquadre conforme a Lei 8.213/91.'
    if (t.includes('endereco'))   return 'Confirme o endereço no documento físico ou com o emissor.'
    return 'Aguarde informações complementares ou solicite o documento físico para conferência.'
  }

  return ''
}

const actionIcon = (status: string): string => {
  if (status === 'alerta')         return '⚠️'
  if (status === 'nao_encontrado') return '📋'
  if (status === 'pendente')       return '🔍'
  return ''
}

const actionBorderClass = (status: string): string => {
  if (status === 'alerta')         return 'border-amber-400 bg-amber-50'
  if (status === 'nao_encontrado') return 'border-blue-400 bg-blue-50'
  if (status === 'pendente')       return 'border-slate-300 bg-slate-50'
  return ''
}

const actionTextClass = (status: string): string => {
  if (status === 'alerta')         return 'text-amber-800'
  if (status === 'nao_encontrado') return 'text-blue-800'
  if (status === 'pendente')       return 'text-slate-700 dark:text-slate-300'
  return ''
}

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
    nao_encontrado: 'bg-slate-100 text-slate-600 dark:text-slate-300',
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
