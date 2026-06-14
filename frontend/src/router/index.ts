import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: () => import('@/views/DashboardView.vue') },
    { path: '/novel/:id', name: 'novel', component: () => import('@/views/NovelView.vue') },
    { path: '/chapter/:id', name: 'chapter', component: () => import('@/views/ChapterView.vue') },
    { path: '/character/:id', name: 'character', component: () => import('@/views/CharacterView.vue') },
    { path: '/writing-rules', name: 'writing-rules', component: () => import('@/views/WritingRulesView.vue') },
    { path: '/mcp', name: 'mcp', component: () => import('@/views/McpView.vue') },
  ],
})

export default router
