import { ref } from 'vue'

export const nomeSolicitante = ref('')
export const departamento = ref('')
export const tipoDocumento = ref('')
export const descricao = ref('')

export const fileInput = ref<HTMLInputElement | null>(null)
export const file = ref<any>(null)
export const fileUrl = ref('')
export const isAnalyzing = ref(false)
export const isAnalyzed = ref(false)
export const showDocModal = ref(false)
export const erros = ref({ nome: '', tipo: '', arquivo: '' })

// Funções
export const triggerFile = () => fileInput.value?.click()

export const onFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    file.value = target.files[0]
    fileUrl.value = URL.createObjectURL(file.value)
    erros.value.arquivo = ''
  }
}

export const removeFile = () => {
  if (fileUrl.value) URL.revokeObjectURL(fileUrl.value)
  file.value = null
  fileUrl.value = ''
  isAnalyzed.value = false
  erros.value = { nome: '', tipo: '', arquivo: '' }
}

export const startAnalysis = () => {
  erros.value = { nome: '', tipo: '', arquivo: '' }
  isAnalyzed.value = false
  let valido = true

  if (!nomeSolicitante.value.trim()) {
    erros.value.nome = 'Campo obrigatório'
    valido = false
  }
  if (!tipoDocumento.value) {
    erros.value.tipo = 'Selecione o tipo'
    valido = false
  }
  if (!file.value) {
    erros.value.arquivo = 'Você deve enviar um documento antes de analisar.'
    valido = false
  }

  if (!valido) return

  isAnalyzing.value = true
  setTimeout(() => {
    isAnalyzing.value = false
    isAnalyzed.value = true
  }, 3000)
}

export const openManualAnalysis = () => {
  if (fileUrl.value) showDocModal.value = true
}