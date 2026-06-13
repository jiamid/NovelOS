<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  NButton,
  NCard,
  NDataTable,
  NGrid,
  NGridItem,
  NInput,
  NModal,
  NSpace,
  NSpin,
  useMessage,
} from 'naive-ui'
import { dashboardApi, novelApi } from '@/api/client'
import { useAppStore } from '@/stores/app'
import { tableActions } from '@/utils/tableActions'
import type { DashboardStats, Novel } from '@/types'

const router = useRouter()
const message = useMessage()
const store = useAppStore()
const stats = ref<DashboardStats | null>(null)
const loading = ref(true)
const showCreate = ref(false)
const showEdit = ref(false)
const editingId = ref<string | null>(null)
const form = ref({ name: '', description: '' })

async function load() {
  loading.value = true
  try {
    stats.value = await dashboardApi.stats()
    await store.loadNovels()
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  form.value = { name: '', description: '' }
  showCreate.value = true
}

function openEdit(row: Novel) {
  editingId.value = row.id
  form.value = { name: row.name, description: row.description || '' }
  showEdit.value = true
}

async function saveCreate() {
  if (!form.value.name.trim()) {
    message.warning('请输入小说名称')
    return
  }
  const novel = await novelApi.create(form.value)
  message.success('小说已创建')
  showCreate.value = false
  await load()
  router.push(`/novel/${novel.id}`)
}

async function saveEdit() {
  if (!editingId.value) return
  await novelApi.update(editingId.value, form.value)
  message.success('小说已更新')
  showEdit.value = false
  await load()
}

async function deleteNovel(row: Novel) {
  await novelApi.delete(row.id)
  message.success('小说已删除')
  await load()
}

onMounted(load)
</script>

<template>
  <NSpin :show="loading">
    <div class="dashboard-hero">
      <div>
        <h1>创作工作台</h1>
        <p>集中管理小说、章节、人物关系和时间线，让 AI 助手始终拥有清晰的故事上下文。</p>
      </div>
      <NSpace>
        <NButton type="primary" size="large" @click="openCreate">创建小说</NButton>
        <NButton secondary size="large" @click="router.push('/mcp')">MCP 配置</NButton>
      </NSpace>
    </div>

    <NGrid v-if="stats" :cols="4" :x-gap="18" :y-gap="18" style="margin-bottom: 24px">
      <NGridItem>
        <NCard class="stat-card">
          <div class="value">{{ stats.novel_count }}</div>
          <div class="label">小说</div>
        </NCard>
      </NGridItem>
      <NGridItem>
        <NCard class="stat-card">
          <div class="value">{{ stats.chapter_count }}</div>
          <div class="label">章节</div>
        </NCard>
      </NGridItem>
      <NGridItem>
        <NCard class="stat-card">
          <div class="value">{{ stats.character_count }}</div>
          <div class="label">人物</div>
        </NCard>
      </NGridItem>
      <NGridItem>
        <NCard class="stat-card">
          <div class="value">{{ stats.event_count }}</div>
          <div class="label">事件</div>
        </NCard>
      </NGridItem>
    </NGrid>

    <NCard title="小说列表" style="margin-bottom: 16px">
      <NSpace style="margin-bottom: 12px">
        <NButton type="primary" @click="openCreate">创建小说</NButton>
        <NButton @click="router.push('/mcp')">MCP 配置</NButton>
      </NSpace>
      <NDataTable
        :columns="[
          { title: '名称', key: 'name' },
          { title: '描述', key: 'description', ellipsis: { tooltip: true } },
          { title: '操作', key: 'actions', width: 200, render: (r: Novel) => tableActions(r, { onView: () => router.push(`/novel/${r.id}`), viewLabel: '打开', onEdit: () => openEdit(r), onDelete: () => deleteNovel(r) }) },
        ]"
        :data="store.novels"
      />
    </NCard>

    <NModal v-model:show="showCreate" preset="dialog" title="创建小说" positive-text="创建" @positive-click="saveCreate">
      <NSpace vertical style="width: 100%">
        <NInput v-model:value="form.name" placeholder="小说名称" />
        <NInput v-model:value="form.description" type="textarea" placeholder="描述" :rows="3" />
      </NSpace>
    </NModal>

    <NModal v-model:show="showEdit" preset="dialog" title="编辑小说" positive-text="保存" @positive-click="saveEdit">
      <NSpace vertical style="width: 100%">
        <NInput v-model:value="form.name" placeholder="小说名称" />
        <NInput v-model:value="form.description" type="textarea" placeholder="描述" :rows="3" />
      </NSpace>
    </NModal>
  </NSpin>
</template>
