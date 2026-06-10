import { computed, ref } from 'vue'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

export const list = ref<any[]>([])
export const isLoading = ref(false)
export const hasError = ref(false)

export const fetchAnalyses = async () => {
  isLoading.value = true
  hasError.value = false
  try {
    const response = await fetch(`${API_URL}/analises`)
    if (!response.ok) throw new Error('Falha ao buscar análises do banco de dados')
    const data = await response.json()
    list.value = data
  } catch (error) {
    console.error('Error fetching analyses:', error)
    hasError.value = true
  } finally {
    isLoading.value = false
  }
}

export const stats = computed(() => {
  const total = list.value.length
  const aprovado = list.value.filter((o) => o.status === 'aprovado').length
  const rejeitado = list.value.filter((o) => o.status === 'rejeitado').length
  const pendente = total - aprovado - rejeitado

  return [
    {
      label: 'Total de Análises',
      value: String(total),
      icon: '📄',
      iconBg: 'bg-blue-50 dark:bg-blue-950/40',
      iconColor: 'text-blue-600 dark:text-blue-400',
    },
    {
      label: 'Aprovados',
      value: String(aprovado),
      icon: '✅',
      iconBg: 'bg-emerald-50 dark:bg-emerald-950/40',
      iconColor: 'text-emerald-600 dark:text-emerald-400',
    },
    {
      label: 'Pendentes',
      value: String(pendente),
      icon: '🕒',
      iconBg: 'bg-amber-50 dark:bg-amber-950/40',
      iconColor: 'text-amber-600 dark:text-amber-400',
    },
    {
      label: 'Rejeitados',
      value: String(rejeitado),
      icon: '❌',
      iconBg: 'bg-rose-50 dark:bg-rose-950/40',
      iconColor: 'text-rose-600 dark:text-rose-400',
    },
  ]
})

export const recentAnalyses = computed(() =>
  list.value.slice(0, 10).map((o) => {
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
  })
)

export const distribution = computed(() => {
  const total = list.value.length || 1
  const aprovado = list.value.filter((o) => o.status === 'aprovado').length
  const rejeitado = list.value.filter((o) => o.status === 'rejeitado').length
  const pendente = list.value.length - aprovado - rejeitado

  return [
    {
      label: 'Aprovado',
      value: String(aprovado),
      pct: Math.round((aprovado / total) * 100),
      color: 'bg-emerald-500',
      strokeColor: '#10b981'
    },
    {
      label: 'Pendente',
      value: String(pendente),
      pct: Math.round((pendente / total) * 100),
      color: 'bg-amber-400',
      strokeColor: '#fbbf24'
    },
    {
      label: 'Rejeitado',
      value: String(rejeitado),
      pct: Math.round((rejeitado / total) * 100),
      color: 'bg-rose-500',
      strokeColor: '#f43f5e'
    },
  ]
})
