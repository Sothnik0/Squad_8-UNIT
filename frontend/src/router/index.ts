import { createRouter, createWebHistory } from 'vue-router'
import AnalysisView from '@/views/AnaliseIa/AnalysisView.vue'
import LinksView from '@/views/Links/LinksView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/analise',
    },
    {
      path: '/analise',
      name: 'analysis',
      component: AnalysisView,
    },
    {
      path: '/links',
      name: 'links',
      component: LinksView,
    },
  ],
})

export default router
