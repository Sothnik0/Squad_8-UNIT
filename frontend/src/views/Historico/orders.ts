import { ref, computed } from 'vue'

export interface Order {
  id:       string
  nome:     string
  tipo:     string
  score:    number
  status:   string
  veredito: string
  data:     string
}

export const search         = ref('')
export const selectedStatus = ref('')
export const statusList     = ref(['Aprovado', 'Pendente', 'Rejeitado'])

export const list = ref<Order[]>([])

// Chamado pelo analysis.ts após cada análise bem-sucedida
export const addOrder = (order: Order) => {
  list.value.unshift(order)
}

export const filteredList = computed(() =>
  list.value.filter(item => {
    const s = search.value.toLowerCase()
    const matchSearch = item.nome.toLowerCase().includes(s) || item.id.toLowerCase().includes(s)
    const matchStatus = !selectedStatus.value || item.status === selectedStatus.value
    return matchSearch && matchStatus
  })
)

export const handleStatus = (status: string) => {
  selectedStatus.value = status
}

export const statusClass = (status: string) => [
  'px-2 py-1 text-xs rounded-full font-semibold',
  status === 'Aprovado'
    ? 'bg-green-100 text-green-800'
    : status === 'Pendente'
    ? 'bg-amber-100 text-amber-800'
    : 'bg-red-100 text-red-800',
]

export const vereditoClass = (veredito: string) => [
  'px-2 py-1 text-xs rounded-full font-semibold',
  veredito === 'Verídico' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800',
]

export const deleteOrder = (id: string) => {
  list.value = list.value.filter(item => item.id !== id)
}