import { createRouter, createWebHistory } from 'vue-router'
import AnalysisView from '@/views/AnaliseIa/AnalysisView.vue'
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
      path: '/links',
      name: 'links',
      component: LinksView,
    },
  ],
})

export default router
