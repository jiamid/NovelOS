import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Novel } from '@/types'
import { novelApi } from '@/api/client'

export const useAppStore = defineStore('app', () => {
  const novels = ref<Novel[]>([])
  const loading = ref(false)

  async function loadNovels() {
    loading.value = true
    try {
      const res = await novelApi.list()
      novels.value = res.items
    } finally {
      loading.value = false
    }
  }

  return { novels, loading, loadNovels }
})
