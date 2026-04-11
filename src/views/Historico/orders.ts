import { ref, computed } from 'vue'

export const search = ref('')
export const selectedStatus = ref('')
export const statusList = ref(['Aprovado', 'Rejeitado'])

export const list = ref([
  {
    id: 'OS-MMWMH3RO',
    nome: 'Raimundo',
    tipo: 'Comprovante escolaridade',
    status: 'Aprovado',
    veredito: 'Autêntico',
    data: '18/03/2026 15:37'
  },
  {
    id: 'OS-X1YZ2Z3',
    nome: 'Raimundo',
    tipo: 'Cert. pós graduação',
    status: 'Rejeitado',
    veredito: 'Suspeito',
    data: '18/03/2026 16:52'
  }
])

export const filteredList = computed(() => {
  return list.value.filter(item => {
    const s = search.value.toLowerCase()
    const matchSearch = item.nome.toLowerCase().includes(s) || item.id.toLowerCase().includes(s)
    const matchStatus = !selectedStatus.value || item.status === selectedStatus.value
    return matchSearch && matchStatus
  })
})

export const handleStatus = (status: string) => {
  selectedStatus.value = status
}

export const statusClass = (status: string) => {
  return [
    'px-2 py-1 text-xs rounded-full font-semibold',
    status === 'Aprovado' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
  ]
}

export const vereditoClass = (veredito: string) => {
  return [
    'px-2 py-1 text-xs rounded-full font-semibold',
    veredito === 'Autêntico' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
  ]
}

export const deleteOrder = (id: string) => {
  list.value = list.value.filter(item => item.id !== id)
}