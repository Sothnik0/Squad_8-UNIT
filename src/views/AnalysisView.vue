<template>
  <div class="min-h-screen bg-gray-50 p-8 text-slate-700">
    <div class="max-w-5xl mx-auto">
      <header class="mb-8">
        <h1 class="text-2xl font-bold text-slate-800">Análise de Documento</h1>
        <p class="text-slate-500">Envie um documento para análise de segurança com IA</p>
      </header>

      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-8 mb-6">
        <h3 class="text-lg font-semibold mb-6">Informações da Solicitação</h3>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-2">
            <label class="text-sm font-medium">Nome do Solicitante *</label>
            <input
              type="text"
              placeholder="Nome completo"
              class="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition"
            />
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium">Departamento</label>
            <input
              type="text"
              placeholder="Ex: Secretaria Acadêmica"
              class="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition"
            />
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium">Tipo de Documento *</label>
            <select
              class="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition"
            >
              <option value="">Selecione o tipo</option>
              <option value="certificado">Certificado Técnico</option>
              <option value="identidade">Documento de Identidade</option>
            </select>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium">Descrição Adicional</label>
            <input
              type="text"
              placeholder="Informações extras sobre o documento"
              class="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition"
            />
          </div>
        </div>
      </div>

      <div
        @click="triggerFile"
        class="group border-2 border-dashed border-gray-200 rounded-xl p-12 bg-white hover:border-blue-400 hover:bg-blue-50 transition-all cursor-pointer text-center mb-8"
      >
        <input type="file" ref="fileInput" class="hidden" @change="onFileChange" />

        <div v-if="!file" class="flex flex-col items-center">
          <div
            class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition"
          >
            <svg
              class="w-8 h-8 text-blue-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
              />
            </svg>
          </div>
          <p class="text-lg font-medium">Arraste o documento aqui ou clique para selecionar</p>
          <p class="text-sm text-gray-400 mt-1">PDF, JPG, JPEG, PNG (máx. 10MB)</p>
        </div>

        <div v-else class="flex flex-col items-center text-green-600 font-medium">
          <svg class="w-16 h-16 mb-2" fill="currentColor" viewBox="0 0 20 20">
            <path
              d="M9 2a2 2 0 00-2 2v8a2 2 0 002 2h6a2 2 0 002-2V6.414A2 2 0 0016.414 5L14 2.586A2 2 0 0012.586 2H9z"
            />
            <path d="M3 8a2 2 0 012-2v10h8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z" />
          </svg>
          <span>{{ file.name }}</span>
          <button @click.stop="file = null" class="mt-2 text-xs text-red-500 underline">
            Remover arquivo
          </button>
        </div>
      </div>

      <div class="flex gap-4">
        <button
          @click="isAnalyzed = true"
          class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-lg shadow-md transition-all flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
            />
          </svg>
          Analisar Documento
        </button>

        <button
          v-if="isAnalyzed"
          class="border border-gray-300 hover:bg-gray-50 py-3 px-8 rounded-lg font-semibold flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"
            />
          </svg>
          Salvar Ordem de Serviço
        </button>
      </div>

      <transition name="fade">
        <div v-if="isAnalyzed" class="mt-10 space-y-6">
          <div class="bg-red-50 border border-red-100 p-6 rounded-xl flex items-start gap-4">
            <div class="bg-red-500 p-2 rounded-lg text-white">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
            <div>
              <h3 class="text-red-800 font-bold text-lg leading-tight">
                Documento Suspeito de Fraude
              </h3>
              <p class="text-red-600">Confiança da análise: 0%</p>
            </div>
          </div>

          <div class="bg-white border border-gray-100 rounded-xl shadow-sm p-6">
            <div class="flex items-center gap-2 mb-4 font-semibold text-slate-800">
              <svg
                class="w-5 h-5 text-gray-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              Resumo da Análise
            </div>
            <div class="h-16 bg-gray-50 rounded-lg"></div>
          </div>

          <div
            class="bg-white border border-gray-100 rounded-xl shadow-sm p-6 inline-block min-w-[300px]"
          >
            <div class="flex items-center gap-2 mb-3 font-semibold text-slate-800">
              <svg
                class="w-5 h-5 text-gray-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                />
              </svg>
              Manipulação de Pixels
            </div>
            <span
              class="bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1 w-fit"
            >
              ✓ Não Detectada
            </span>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const fileInput = ref(null)
const file = ref(null)
const isAnalyzed = ref(false)

const triggerFile = () => fileInput.value.click()

const onFileChange = (e) => {
  const selected = e.target.files[0]
  if (selected) file.value = selected
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
