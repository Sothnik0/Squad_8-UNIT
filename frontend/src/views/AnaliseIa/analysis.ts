import { ref } from 'vue'
import { addOrder } from '@/views/Historico/orders'

type FindingStatus = 'encontrado' | 'nao_encontrado' | 'pendente' | 'alerta'

export interface AnalysisFinding {
  titulo: string
  status: FindingStatus
  detalhe: string
}

export interface AnalysisResult {
  protocolo: string
  status: 'rascunho_tecnico' | 'ia_indisponivel' | 'analisado'
  probabilidade_fraude: number
  resumo: string
  dados_chave: AnalysisFinding[]
  verificacoes_oficiais: AnalysisFinding[]
  alertas: string[]
  fatores_score: string[]
  proximos_passos: string[]
  motor_extracao?: string
  texto_extraido?: string
}

const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'
const MAX_FILE_SIZE = 10 * 1024 * 1024
const ALLOWED_TYPES = ['application/pdf', 'image/jpeg', 'image/png']

export const nomeSolicitante = ref('')
export const departamento    = ref('')
export const tipoDocumento   = ref('')
export const descricao       = ref('')

export const fileInput      = ref<HTMLInputElement | null>(null)
export const file           = ref<File | null>(null)
export const fileUrl        = ref('')
export const isAnalyzing    = ref(false)
export const isAnalyzed     = ref(false)
export const showDocModal   = ref(false)
export const analysisResult = ref<AnalysisResult | null>(null)
export const apiError       = ref('')
export const erros          = ref({ nome: '', tipo: '', arquivo: '' })

const TIPO_LABEL: Record<string, string> = {
  atestado_medico:          'Atestado médico',
  certificado_ensino_medio: 'Certificado de ensino médio',
  historico_escolar:        'Histórico escolar',
  diploma:                  'Diploma de graduação',
}

export const triggerFile = () => fileInput.value?.click()

export const onFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  const selectedFile = target.files?.[0]
  if (!selectedFile) return

  erros.value.arquivo  = ''
  apiError.value       = ''
  analysisResult.value = null
  isAnalyzed.value     = false

  if (!ALLOWED_TYPES.includes(selectedFile.type)) {
    erros.value.arquivo = 'Formato não suportado. Envie PDF, JPG, JPEG ou PNG.'
    target.value = ''
    return
  }
  if (selectedFile.size > MAX_FILE_SIZE) {
    erros.value.arquivo = 'O arquivo deve ter no máximo 10MB.'
    target.value = ''
    return
  }

  if (fileUrl.value) URL.revokeObjectURL(fileUrl.value)
  file.value    = selectedFile
  fileUrl.value = URL.createObjectURL(selectedFile)
}

export const removeFile = () => {
  if (fileUrl.value) URL.revokeObjectURL(fileUrl.value)
  file.value           = null
  fileUrl.value        = ''
  isAnalyzed.value     = false
  analysisResult.value = null
  apiError.value       = ''
  erros.value          = { nome: '', tipo: '', arquivo: '' }
  if (fileInput.value) fileInput.value.value = ''
}

export const startAnalysis = async () => {
  erros.value          = { nome: '', tipo: '', arquivo: '' }
  apiError.value       = ''
  analysisResult.value = null
  isAnalyzed.value     = false
  let valido = true

  if (!nomeSolicitante.value.trim()) { erros.value.nome    = 'Campo obrigatório'; valido = false }
  if (!tipoDocumento.value)          { erros.value.tipo    = 'Selecione o tipo';  valido = false }
  if (!file.value)                   { erros.value.arquivo = 'Envie um documento antes de analisar.'; valido = false }
  if (!valido || !file.value) return

  isAnalyzing.value = true

  try {
    const conteudoBase64 = await fileToBase64(file.value)
    const response = await fetch(`${API_URL}/analises/documento`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        solicitante:    nomeSolicitante.value.trim(),
        departamento:   departamento.value.trim(),
        tipo_documento: tipoDocumento.value,
        descricao:      descricao.value.trim(),
        arquivo: {
          nome:            file.value.name,
          tipo_mime:       file.value.type,
          tamanho_bytes:   file.value.size,
          conteudo_base64: conteudoBase64,
        },
      }),
    })

    const data = await response.json()
    if (!response.ok) throw new Error(data.detail ?? 'Não foi possível analisar o documento.')

    analysisResult.value = data
    isAnalyzed.value     = true

    // Registra automaticamente na lista de ordens de serviço
    addOrder({
      id:       data.protocolo,
      nome:     nomeSolicitante.value.trim(),
      tipo:     TIPO_LABEL[tipoDocumento.value] ?? tipoDocumento.value,
      score:    data.probabilidade_fraude,
      status:   data.probabilidade_fraude >= 75 ? 'Aprovado' : 'Pendente',
      veredito: data.probabilidade_fraude >= 75 ? 'Verídico' : 'Requer verificação',
      data:     new Date().toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' }),
    })
  } catch (error) {
    apiError.value = error instanceof Error ? error.message : 'Erro inesperado na análise.'
  } finally {
    isAnalyzing.value = false
  }
}

export const openManualAnalysis = () => {
  if (fileUrl.value) showDocModal.value = true
}

const fileToBase64 = (selectedFile: File) =>
  new Promise<string>((resolve, reject) => {
    const reader = new FileReader()
    reader.onload  = () => resolve(String(reader.result).split(',')[1] ?? '')
    reader.onerror = () => reject(new Error('Não foi possível ler o arquivo.'))
    reader.readAsDataURL(selectedFile)
  })