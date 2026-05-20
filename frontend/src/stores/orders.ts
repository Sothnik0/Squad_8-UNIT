import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface OrderItem {
  id: string
  nome: string
  tipo: string
  status: string
  veredito: string
  data: string
  descricao?: string
  documentoUrl?: string
}

export const useOrdersStore = defineStore('orders', () => {
  const orders = ref<OrderItem[]>([])

  const generateOS = () => {
    return `OS-${Math.random().toString(36).substring(2, 10).toUpperCase()}`
  }

  const addOrder = (payload: Omit<OrderItem, 'id' | 'data'>) => {
    orders.value.unshift({
      id: generateOS(),
      data: new Date().toLocaleString('pt-BR'),
      ...payload,
    })
  }

  const deleteOrder = (id: string) => {
    orders.value = orders.value.filter(item => item.id !== id)
  }

  return {
    orders,
    addOrder,
    deleteOrder,
  }
})
