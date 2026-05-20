import { ref, computed } from 'vue'
import { useOrdersStore } from '@/stores/orders'

export const search = ref('')
export const selectedStatus = ref('')
export const statusList = ref(['Aprovado', 'Rejeitado'])

export const list = computed(() => useOrdersStore().orders)

export const filteredList = computed(() => {
  return list.value.filter(item => {
    const s = search.value.toLowerCase()

    const matchSearch =
      item.nome.toLowerCase().includes(s) ||
      item.id.toLowerCase().includes(s)

    const matchStatus =
      !selectedStatus.value ||
      item.status === selectedStatus.value

    return matchSearch && matchStatus
  })
})

export const handleStatus = (status: string) => {
  selectedStatus.value = status
}

export const statusClass = (status: string) => {
  return [
    'px-2 py-1 text-xs rounded-full font-semibold',
    status === 'Aprovado'
      ? 'bg-green-100 text-green-800'
      : 'bg-red-100 text-red-800'
  ]
}

export const vereditoClass = (veredito: string) => {
  return [
    'px-2 py-1 text-xs rounded-full font-semibold',
    veredito === 'Autêntico'
      ? 'bg-green-100 text-green-800'
      : 'bg-yellow-100 text-yellow-800'
  ]
}

export const deleteOrder = (id: string) => {
  useOrdersStore().deleteOrder(id)
}

export const openDocument = (url?: string) => {
  if (!url) return

  window.open(url, '_blank')
}
