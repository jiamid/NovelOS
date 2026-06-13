<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NButton,
  NDataTable,
  NInput,
  NModal,
  NSelect,
  NSpace,
  NSpin,
  NTabs,
  NTabPane,
  NTag,
  useDialog,
  useMessage,
} from 'naive-ui'
import {
  characterApi,
  eventApi,
  getErrorMessage,
  novelApi,
  timelineApi,
} from '@/api/client'
import CharacterRelationGraph from '@/components/CharacterRelationGraph.vue'
import ChapterPanel from '@/components/ChapterPanel.vue'
import VisualTimeline from '@/components/VisualTimeline.vue'
import { useAppStore } from '@/stores/app'
import { tableActions } from '@/utils/tableActions'
import type { Character, CharacterRelation, Event, Novel, TimelineItem } from '@/types'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const dialog = useDialog()
const store = useAppStore()
const novelId = route.params.id as string

const loading = ref(true)
const novel = ref<Novel | null>(null)
const characters = ref<Character[]>([])
const relations = ref<CharacterRelation[]>([])
const timelines = ref<TimelineItem[]>([])

const showNovelEdit = ref(false)
const novelForm = ref({ name: '', description: '' })
const activeTab = ref('chapters')

const showCharacter = ref(false)
const editingCharacterId = ref<string | null>(null)
const charForm = ref({ name: '', description: '', current_status: '' })

const showEvent = ref(false)
const editingEventId = ref<string | null>(null)
const eventForm = ref({
  title: '',
  description: '',
  occur_time: '',
  location: '',
  character_ids: [] as string[],
})

const showRelation = ref(false)
const relationForm = ref({ source_id: '', target_id: '', relation_type: '' })

const charModalTitle = computed(() => (editingCharacterId.value ? '编辑人物' : '添加人物'))

const relationColumns = computed(() => [
  {
    title: '人物 A',
    key: 'source_id',
    render: (r: CharacterRelation) => characters.value.find((c) => c.id === r.source_id)?.name,
  },
  {
    title: '关系',
    key: 'relation_type',
    render: (r: CharacterRelation) => h(NTag, { size: 'small', type: 'info' }, () => r.relation_type),
  },
  {
    title: '人物 B',
    key: 'target_id',
    render: (r: CharacterRelation) => characters.value.find((c) => c.id === r.target_id)?.name,
  },
  {
    title: '操作',
    key: 'actions',
    width: 100,
    render: (r: CharacterRelation) =>
      tableActions(r as unknown as { id: string }, {
        onDelete: () => deleteRelation(r),
      }),
  },
])
const charOptions = computed(() => characters.value.map((c) => ({ label: c.name, value: c.id })))
const eventModalTitle = computed(() => (editingEventId.value ? '编辑事件' : '添加事件'))

async function load() {
  loading.value = true
  try {
    novel.value = await novelApi.get(novelId)
    characters.value = (await characterApi.list(novelId)).items
    relations.value = await characterApi.listRelations(novelId)
    timelines.value = await timelineApi.withEvents(novelId)
  } finally {
    loading.value = false
  }
}

function openNovelEdit() {
  novelForm.value = { name: novel.value?.name || '', description: novel.value?.description || '' }
  showNovelEdit.value = true
}

async function saveNovel() {
  await novelApi.update(novelId, novelForm.value)
  message.success('小说已更新')
  showNovelEdit.value = false
  await load()
  await store.loadNovels()
}

function openRelationModal() {
  relationForm.value = { source_id: '', target_id: '', relation_type: '' }
  showRelation.value = true
}

async function saveRelation() {
  if (!relationForm.value.source_id || !relationForm.value.target_id || !relationForm.value.relation_type.trim()) {
    message.warning('请填写完整的关系信息')
    return
  }
  if (relationForm.value.source_id === relationForm.value.target_id) {
    message.warning('不能与自己建立关系')
    return
  }
  try {
    await characterApi.createRelation(relationForm.value)
    message.success('关系已添加')
    showRelation.value = false
    await load()
  } catch (e) {
    message.error(getErrorMessage(e))
  }
}

async function deleteRelation(row: CharacterRelation) {
  await characterApi.deleteRelation(row.source_id, row.target_id)
  message.success('关系已删除')
  await load()
}

function openCharacterModal(row?: Character) {
  editingCharacterId.value = row?.id || null
  charForm.value = {
    name: row?.name || '',
    description: row?.description || '',
    current_status: row?.current_status || '',
  }
  showCharacter.value = true
}

async function saveCharacter() {
  try {
    if (editingCharacterId.value) {
      await characterApi.update(editingCharacterId.value, charForm.value)
      message.success('人物已更新')
    } else {
      await characterApi.create({ novel_id: novelId, abilities: [], tags: [], ...charForm.value })
      message.success('人物已创建')
    }
    showCharacter.value = false
    editingCharacterId.value = null
    charForm.value = { name: '', description: '', current_status: '' }
    await load()
  } catch (e) {
    message.error(getErrorMessage(e))
  }
}

async function deleteCharacter(row: Character) {
  await characterApi.delete(row.id)
  message.success('人物已删除')
  await load()
}

function openEventModal(event?: Event) {
  editingEventId.value = event?.id || null
  if (event) {
    eventForm.value = {
      title: event.title,
      description: event.description || '',
      occur_time: event.occur_time || '',
      location: event.location || '',
      character_ids: event.character_ids || event.characters?.map((c) => c.id) || [],
    }
    showEvent.value = true
    return
  }
  eventForm.value = {
    title: '',
    description: '',
    occur_time: '',
    location: '',
    character_ids: [],
  }
  showEvent.value = true
}

async function editEventById(eventId: string) {
  const full = await eventApi.get(eventId)
  openEventModal(full)
}

async function saveEvent() {
  if (!eventForm.value.title.trim()) {
    message.warning('请输入事件标题')
    return
  }
  try {
    const payload = {
      title: eventForm.value.title,
      description: eventForm.value.description || undefined,
      occur_time: eventForm.value.occur_time || undefined,
      location: eventForm.value.location || undefined,
      character_ids: eventForm.value.character_ids,
    }
    if (editingEventId.value) {
      await eventApi.update(editingEventId.value, payload)
      message.success('事件已更新')
    } else {
      const ev = await eventApi.create({ novel_id: novelId, ...payload })
      await timelineApi.create({ novel_id: novelId, event_id: ev.id, sequence: timelines.value.length })
      message.success('事件已添加')
    }
    showEvent.value = false
    editingEventId.value = null
    await load()
  } catch (e) {
    message.error(getErrorMessage(e))
  }
}

async function deleteTimeline(row: TimelineItem) {
  if (row.event_id) await eventApi.delete(row.event_id)
  message.success('事件已删除')
  await load()
}

function confirmDeleteNovel() {
  const name = novel.value?.name || '该小说'
  dialog.warning({
    title: '删除小说',
    content: `确定删除「${name}」吗？该小说下所有数据将被永久删除。`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      await novelApi.delete(novelId)
      message.success('小说已删除')
      await store.loadNovels()
      router.push('/')
    },
  })
}

onMounted(() => {
  if (route.query.chapter) activeTab.value = 'chapters'
  load()
})
</script>

<template>
  <NSpin :show="loading">
    <div class="page-header" style="display: flex; justify-content: space-between; align-items: flex-start">
      <div>
        <h1>{{ novel?.name || '小说' }}</h1>
        <p>{{ novel?.description }}</p>
      </div>
      <NSpace>
        <NButton @click="openNovelEdit">编辑小说</NButton>
        <NButton type="error" secondary @click="confirmDeleteNovel">删除小说</NButton>
      </NSpace>
    </div>

    <NTabs v-model:value="activeTab" type="line" animated>
      <NTabPane name="chapters" tab="章节">
        <ChapterPanel :novel-id="novelId" />
      </NTabPane>

      <NTabPane name="characters" tab="人物">
        <NTabs type="segment" animated style="margin-bottom: 12px">
          <NTabPane name="char-list" tab="列表">
            <NSpace style="margin-bottom: 12px">
              <NButton type="primary" @click="openCharacterModal()">添加人物</NButton>
            </NSpace>
            <NDataTable
              :columns="[
                { title: '姓名', key: 'name' },
                { title: '状态', key: 'current_status' },
                { title: '操作', key: 'actions', width: 200, render: (r: Character) => tableActions(r, { onView: () => router.push(`/character/${r.id}`), viewLabel: '详情', onEdit: () => openCharacterModal(r), onDelete: () => deleteCharacter(r) }) },
              ]"
              :data="characters"
            />
          </NTabPane>
          <NTabPane name="char-graph" tab="关系图">
            <NSpace style="margin-bottom: 12px">
              <NButton type="primary" @click="openRelationModal()">添加关系</NButton>
            </NSpace>
            <CharacterRelationGraph :characters="characters" :relations="relations" />
            <NDataTable
              style="margin-top: 16px"
              :columns="relationColumns"
              :data="relations"
            />
          </NTabPane>
        </NTabs>
      </NTabPane>

      <NTabPane name="timeline" tab="时间线">
        <NSpace style="margin-bottom: 12px">
          <NButton type="primary" @click="openEventModal()">添加事件</NButton>
        </NSpace>
        <NTabs type="segment" animated>
          <NTabPane name="timeline-visual" tab="图示">
            <VisualTimeline
              :items="timelines"
              @edit="editEventById"
              @delete="deleteTimeline"
            />
          </NTabPane>
          <NTabPane name="timeline-list" tab="列表">
            <NDataTable
              :columns="[
                { title: '序号', key: 'sequence', width: 70, render: (r: TimelineItem) => r.sequence + 1 },
                { title: '时间', key: 'time', width: 120, render: (r: TimelineItem) => r.event?.occur_time || '-' },
                { title: '地点', key: 'location', width: 120, render: (r: TimelineItem) => r.event?.location || '-' },
                { title: '人物', key: 'characters', render: (r: TimelineItem) => r.event?.characters?.map(c => c.name).join('、') || '-' },
                { title: '事件', key: 'event', ellipsis: { tooltip: true }, render: (r: TimelineItem) => r.event?.title },
                { title: '操作', key: 'actions', width: 140, render: (r: TimelineItem) => tableActions(r, { onEdit: () => r.event && editEventById(r.event.id), onDelete: () => deleteTimeline(r) }) },
              ]"
              :data="timelines"
            />
          </NTabPane>
        </NTabs>
      </NTabPane>
    </NTabs>

    <NModal v-model:show="showNovelEdit" preset="dialog" title="编辑小说" positive-text="保存" @positive-click="saveNovel">
      <NSpace vertical style="width: 100%">
        <NInput v-model:value="novelForm.name" placeholder="小说名称" />
        <NInput v-model:value="novelForm.description" type="textarea" placeholder="描述" :rows="3" />
      </NSpace>
    </NModal>

    <NModal v-model:show="showCharacter" preset="dialog" :title="charModalTitle" positive-text="保存" @positive-click="saveCharacter">
      <NSpace vertical style="width: 100%">
        <NInput v-model:value="charForm.name" placeholder="姓名（同一小说内不可重名）" />
        <NInput v-model:value="charForm.current_status" placeholder="当前状态" />
        <NInput v-model:value="charForm.description" type="textarea" placeholder="描述" :rows="3" />
      </NSpace>
    </NModal>

    <NModal v-model:show="showRelation" preset="dialog" title="添加人物关系" positive-text="保存" @positive-click="saveRelation">
      <NSpace vertical style="width: 100%">
        <NSelect v-model:value="relationForm.source_id" :options="charOptions" placeholder="人物 A" filterable />
        <NInput v-model:value="relationForm.relation_type" placeholder="关系类型（如：朋友、敌人、师徒）" />
        <NSelect v-model:value="relationForm.target_id" :options="charOptions" placeholder="人物 B" filterable />
      </NSpace>
    </NModal>

    <NModal
      v-model:show="showEvent"
      preset="dialog"
      :title="eventModalTitle"
      positive-text="保存"
      style="width: 520px"
      @positive-click="saveEvent"
    >
      <NSpace vertical style="width: 100%">
        <NInput v-model:value="eventForm.occur_time" placeholder="时间（如：元年春、第三日黄昏）" />
        <NInput v-model:value="eventForm.location" placeholder="地点（如：王城、东海之滨）" />
        <NSelect
          v-model:value="eventForm.character_ids"
          :options="charOptions"
          multiple
          placeholder="相关人物"
          filterable
        />
        <NInput v-model:value="eventForm.title" placeholder="事件标题" />
        <NInput v-model:value="eventForm.description" type="textarea" placeholder="事件描述" :rows="4" />
      </NSpace>
    </NModal>
  </NSpin>
</template>
