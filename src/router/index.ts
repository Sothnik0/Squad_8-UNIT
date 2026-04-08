import { createRouter, createWebHistory } from 'vue-router'
import AnalysisView from '../views/AnalysisView.vue'
import ServiceOrder from '@/components/ServiceOrder.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: AnalysisView,
    },
    {
      path: '/analise',
      name: 'analysis',
      component: AnalysisView,
    },
    {
      path: '/ordens',
      name: 'orders',
      component: ServiceOrder,
    },
  ],
})

export default router
