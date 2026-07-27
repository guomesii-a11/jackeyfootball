import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/players', name: 'power', component: () => import('@/views/PowerRankingView.vue') },
    { path: '/data', name: 'data', component: () => import('@/views/DataRankingView.vue') },
    { path: '/compare', name: 'compare', component: () => import('@/views/CompareView.vue') },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

export default router
