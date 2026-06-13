<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NSpin } from 'naive-ui'
import { chapterApi } from '@/api/client'

const route = useRoute()
const router = useRouter()

onMounted(async () => {
  const chapter = await chapterApi.get(route.params.id as string)
  router.replace({ path: `/novel/${chapter.novel_id}`, query: { chapter: chapter.id } })
})
</script>

<template>
  <NSpin :show="true" description="跳转中..." style="margin-top: 80px" />
</template>
