import { createRouter, createWebHistory } from 'vue-router'
import AnalysisView from '@/views/AnaliseIa/AnalysisView.vue' 
import ServiceOrder from '@/views/Historico/ServiceOrder.vue'
import DashboardView from '@/views/Dashboard/DashboardView.vue'
import LinksView from '@/views/Links/LinksView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/analise',
      name: 'analysis',
      component: AnalysisView,
    },
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView,
    },
    {
      path: '/ordens',
      name: 'orders',
      component: ServiceOrder,
    },
    {
      path: '/links',
      name: 'links',
      component: LinksView
    },
  ],

})

export default router
