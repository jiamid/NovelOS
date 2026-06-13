<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NButton,
  NEmpty,
  NInput,
  NModal,
  NScrollbar,
  NSpace,
  NSpin,
  NText,
  useDialog,
  useMessage,
} from 'naive-ui'
import { chapterApi, getErrorMessage } from '@/api/client'
import ChapterEditor from '@/components/ChapterEditor.vue'
import type { Chapter } from '@/types'

const props = defineProps<{ novelId: string }>()

const route = useRoute()
const router = useRouter()
const message = useMessage()
const dialog = useDialog()

const loadingList = ref(true)
const loadingChapter = ref(false)
const saving = ref(false)
const chapters = ref<Chapter[]>([])
const selectedId = ref<string | null>(null)
const form = ref({ title: '', summary: '', content: '' })
const savedForm = ref({ title: '', summary: '', content: '' })

const showCreate = ref(false)
const createForm = ref({ title: '', summary: '' })

function normalizeText(value: string): string {
  return value.replace(/\r\n/g, '\n').replace(/\n+$/g, '')
}

const isDirty = computed(() => {
  if (form.value.title !== savedForm.value.title) return true
  if (form.value.summary !== savedForm.value.summary) return true
  return normalizeText(form.value.content) !== normalizeText(savedForm.value.content)
})

const selectedChapter = computed(() => chapters.value.find((c) => c.id === selectedId.value))

async function loadChapters(preferredId?: string | null) {
  loadingList.value = true
  try {
    chapters.value = (await chapterApi.list(props.novelId)).items
    const target =
      preferredId ??
      (typeof route.query.chapter === 'string' ? route.query.chapter : null) ??
      selectedId.value
    if (target && chapters.value.some((c) => c.id === target)) {
      await selectChapter(target, { skipDirtyCheck: true })
    } else if (!selectedId.value && chapters.value.length) {
      await selectChapter(chapters.value[0].id, { skipDirtyCheck: true })
    } else if (selectedId.value && !chapters.value.some((c) => c.id === selectedId.value)) {
      selectedId.value = null
      form.value = { title: '', summary: '', content: '' }
      savedForm.value = { title: '', summary: '', content: '' }
    }
  } finally {
    loadingList.value = false
  }
}

function syncRouteQuery(chapterId: string | null) {
  const query = { ...route.query }
  if (chapterId) query.chapter = chapterId
  else delete query.chapter
  router.replace({ query })
}

async function loadChapterContent(id: string) {
  loadingChapter.value = true
  try {
    const chapter = await chapterApi.get(id)
    form.value = {
      title: chapter.title,
      summary: chapter.summary || '',
      content: chapter.content || '',
    }
    savedForm.value = { ...form.value }
  } finally {
    loadingChapter.value = false
  }
}

async function selectChapter(id: string, opts?: { skipDirtyCheck?: boolean }) {
  if (selectedId.value === id && !loadingChapter.value) return

  if (!opts?.skipDirtyCheck && isDirty.value) {
    const ok = await new Promise<boolean>((resolve) => {
      dialog.warning({
        title: '未保存的修改',
        content: '当前章节有未保存的内容，切换后将丢失。是否继续？',
        positiveText: '放弃修改',
        negativeText: '取消',
        onPositiveClick: () => resolve(true),
        onNegativeClick: () => resolve(false),
        onClose: () => resolve(false),
      })
    })
    if (!ok) return
  }

  selectedId.value = id
  syncRouteQuery(id)
  await loadChapterContent(id)
}

async function saveCurrent() {
  if (!selectedId.value) return
  if (!form.value.title.trim()) {
    message.warning('请输入章节名称')
    return
  }
  saving.value = true
  try {
    await chapterApi.update(selectedId.value, form.value)
    savedForm.value = { ...form.value }
    message.success('章节已保存')
    const id = selectedId.value
    chapters.value = (await chapterApi.list(props.novelId)).items
    selectedId.value = id
  } catch (e) {
    message.error(getErrorMessage(e))
  } finally {
    saving.value = false
  }
}

function openCreate() {
  createForm.value = { title: '', summary: '' }
  showCreate.value = true
}

async function createChapter() {
  if (!createForm.value.title.trim()) {
    message.warning('请输入章节名称')
    return false
  }
  try {
    const ch = await chapterApi.create({ novel_id: props.novelId, ...createForm.value })
    message.success('章节已创建')
    showCreate.value = false
    await loadChapters(ch.id)
    return true
  } catch (e) {
    message.error(getErrorMessage(e))
    return false
  }
}

function confirmDelete() {
  if (!selectedId.value || !selectedChapter.value) return
  dialog.warning({
    title: '删除章节',
    content: `确定删除「${selectedChapter.value.title}」吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      const id = selectedId.value!
      await chapterApi.delete(id)
      message.success('章节已删除')
      selectedId.value = null
      syncRouteQuery(null)
      form.value = { title: '', summary: '', content: '' }
      savedForm.value = { title: '', summary: '', content: '' }
      await loadChapters()
    },
  })
}

watch(
  () => route.query.chapter,
  (id) => {
    if (typeof id === 'string' && id !== selectedId.value && chapters.value.some((c) => c.id === id)) {
      selectChapter(id, { skipDirtyCheck: true })
    }
  }
)

onMounted(() => loadChapters())
</script>

<template>
  <NSpin :show="loadingList">
    <div class="chapter-panel">
      <aside class="chapter-sidebar">
        <div class="sidebar-header">
          <NText strong>章节目录</NText>
          <NButton type="primary" size="small" @click="openCreate">新建</NButton>
        </div>
        <NScrollbar class="sidebar-scroll">
          <div
            v-for="(ch, index) in chapters"
            :key="ch.id"
            class="chapter-item"
            :class="{ active: selectedId === ch.id }"
            @click="selectChapter(ch.id)"
          >
            <div class="chapter-index">{{ index + 1 }}</div>
            <div class="chapter-info">
              <div class="chapter-title">{{ ch.title || '未命名章节' }}</div>
              <div class="chapter-meta">{{ ch.word_count }} 字</div>
            </div>
          </div>
          <NEmpty v-if="!chapters.length" description="暂无章节" style="padding: 24px 0" />
        </NScrollbar>
      </aside>

      <main class="chapter-main">
        <NSpin :show="loadingChapter" class="chapter-spin">
          <div v-if="selectedId" class="chapter-content">
            <div class="chapter-toolbar">
              <NSpace>
                <NButton type="primary" :loading="saving" :disabled="!isDirty" @click="saveCurrent">
                  保存
                </NButton>
                <NButton type="error" secondary @click="confirmDelete">删除</NButton>
              </NSpace>
              <NText v-if="isDirty" depth="3" style="font-size: 12px">有未保存的修改</NText>
            </div>

            <div class="chapter-fields">
              <div>
                <NText depth="3" style="display: block; margin-bottom: 6px">章节名称</NText>
                <NInput v-model:value="form.title" placeholder="章节名称" />
              </div>
              <div>
                <NText depth="3" style="display: block; margin-bottom: 6px">章节摘要</NText>
                <NInput
                  v-model:value="form.summary"
                  type="textarea"
                  placeholder="章节摘要"
                  :rows="2"
                  :autosize="{ minRows: 2, maxRows: 4 }"
                />
              </div>
            </div>

            <div class="chapter-editor-wrap">
              <ChapterEditor :key="selectedId" v-model="form.content" />
            </div>
          </div>
          <NEmpty v-else description="选择左侧章节，或新建章节开始写作" style="margin-top: 80px" />
        </NSpin>
      </main>
    </div>

    <NModal
      v-model:show="showCreate"
      preset="dialog"
      title="创建章节"
      positive-text="创建"
      @positive-click="createChapter"
    >
      <NSpace vertical style="width: 100%">
        <NInput v-model:value="createForm.title" placeholder="章节标题" />
        <NInput v-model:value="createForm.summary" type="textarea" placeholder="摘要（可选）" :rows="3" />
      </NSpace>
    </NModal>
  </NSpin>
</template>

<style scoped>
.chapter-panel {
  display: flex;
  gap: 0;
  height: calc(100vh - 252px);
  min-height: 560px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 18px;
  overflow: hidden;
  background: #fff;
}

.chapter-sidebar {
  width: 268px;
  flex-shrink: 0;
  border-right: 1px solid rgba(148, 163, 184, 0.22);
  display: flex;
  flex-direction: column;
  background: #f8fafc;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 16px 14px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.18);
}

.sidebar-scroll {
  flex: 1;
  max-height: 100%;
}

.chapter-item {
  display: flex;
  gap: 12px;
  margin: 8px 10px;
  padding: 12px;
  cursor: pointer;
  border: 1px solid transparent;
  border-radius: 16px;
  transition:
    background 0.16s ease,
    border-color 0.16s ease;
}

.chapter-item:hover {
  background: #fff;
  border-color: rgba(148, 163, 184, 0.24);
}

.chapter-item.active {
  background: #fff;
  border-color: rgba(37, 99, 235, 0.35);
}

.chapter-index {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  line-height: 28px;
  text-align: center;
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  background: #eef2ff;
  border-radius: 10px;
}

.chapter-item.active .chapter-index {
  background: #2563eb;
  color: #fff;
}

.chapter-info {
  min-width: 0;
  flex: 1;
}

.chapter-title {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chapter-meta {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
}

.chapter-main {
  flex: 1;
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  padding: 20px 22px 22px;
  overflow: hidden;
}

.chapter-spin {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.chapter-spin :deep(.n-spin-container) {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.chapter-spin :deep(.n-spin-content) {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.chapter-content {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.chapter-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
  flex-shrink: 0;
}

.chapter-fields {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 18px;
  flex-shrink: 0;
}

.chapter-editor-wrap {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding-right: 4px;
  scrollbar-width: thin;
  scrollbar-color: rgba(99, 102, 241, 0.4) transparent;
}

.chapter-editor-wrap :deep(.editor-area) {
  min-height: auto;
  border-color: rgba(148, 163, 184, 0.22);
}

.chapter-editor-wrap :deep(.ProseMirror) {
  min-height: 340px;
  outline: none;
}

@media (max-width: 1100px) {
  .chapter-panel {
    height: auto;
    min-height: 0;
    flex-direction: column;
  }

  .chapter-sidebar {
    width: 100%;
    max-height: 260px;
    border-right: 0;
    border-bottom: 1px solid rgba(148, 163, 184, 0.22);
  }

  .chapter-main {
    min-height: 640px;
  }
}
</style>
