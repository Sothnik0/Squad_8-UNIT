import { computed } from 'vue'
import { list } from '@/views/Historico/orders'

// Estatísticas calculadas dinamicamente a partir das ordens reais
export const stats = computed(() => {
  const total    = list.value.length
  const aprovado = list.value.filter(o => o.status === 'Aprovado').length
  const pendente = list.value.filter(o => o.status === 'Pendente').length
  const rejeitado = list.value.filter(o => o.status === 'Rejeitado').length

  return [
    { label: 'Total de Análises', value: String(total),    icon: '📄', iconBg: 'bg-blue-50',    iconColor: 'text-blue-600'    },
    { label: 'Aprovados',         value: String(aprovado), icon: '✅', iconBg: 'bg-emerald-50', iconColor: 'text-emerald-600' },
    { label: 'Pendentes',         value: String(pendente), icon: '🕒', iconBg: 'bg-amber-50',   iconColor: 'text-amber-600'   },
    { label: 'Rejeitados',        value: String(rejeitado),icon: '❌', iconBg: 'bg-rose-50',    iconColor: 'text-rose-600'    },
  ]
})

// Últimas 5 análises para o dashboard
export const recentAnalyses = computed(() =>
  list.value.slice(0, 5).map(o => ({
    id:          o.id,
    document:    o.tipo,
    user:        o.nome,
    status:      o.status,
    statusClass: o.status === 'Aprovado'
      ? 'bg-emerald-100 text-emerald-600'
      : o.status === 'Pendente'
      ? 'bg-amber-100 text-amber-600'
      : 'bg-rose-100 text-rose-600',
    date: o.data,
  }))
)

// Distribuição para o gráfico de pizza
export const distribution = computed(() => {
  const total     = list.value.length || 1
  const aprovado  = list.value.filter(o => o.status === 'Aprovado').length
  const pendente  = list.value.filter(o => o.status === 'Pendente').length
  const rejeitado = list.value.filter(o => o.status === 'Rejeitado').length

  return [
    { label: 'Aprovado',  value: String(aprovado),  pct: Math.round((aprovado  / total) * 100), color: 'bg-emerald-500' },
    { label: 'Pendente',  value: String(pendente),  pct: Math.round((pendente  / total) * 100), color: 'bg-amber-400'   },
    { label: 'Rejeitado', value: String(rejeitado), pct: Math.round((rejeitado / total) * 100), color: 'bg-rose-400'    },
  ]
})