<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NButton,
  NCard,
  NDescriptions,
  NDescriptionsItem,
  NIcon,
  NInput,
  NModal,
  NSpace,
  NSpin,
  NTag,
  useDialog,
  useMessage,
} from 'naive-ui'
import { ArrowBackOutline } from '@vicons/ionicons5'
import { characterApi, getErrorMessage } from '@/api/client'
import type { Character } from '@/types'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const dialog = useDialog()
const characterId = route.params.id as string

const loading = ref(true)
const character = ref<Character | null>(null)
const showEdit = ref(false)
const form = ref({
  name: '',
  gender: '',
  birthday: '',
  description: '',
  current_status: '',
  abilities: '',
  tags: '',
})

async function load() {
  loading.value = true
  try {
    character.value = await characterApi.get(characterId)
  } finally {
    loading.value = false
  }
}

function goBack() {
  const novelId = character.value?.novel_id
  if (novelId) router.push(`/novel/${novelId}`)
  else router.push('/')
}

function openEdit() {
  if (!character.value) return
  form.value = {
    name: character.value.name,
    gender: character.value.gender || '',
    birthday: character.value.birthday || '',
    description: character.value.description || '',
    current_status: character.value.current_status || '',
    abilities: character.value.abilities.join(', '),
    tags: character.value.tags.join(', '),
  }
  showEdit.value = true
}

async function save() {
  try {
    const abilities = form.value.abilities.split(',').map((s) => s.trim()).filter(Boolean)
    const tags = form.value.tags.split(',').map((s) => s.trim()).filter(Boolean)
    character.value = await characterApi.update(characterId, {
      name: form.value.name,
      gender: form.value.gender || undefined,
      birthday: form.value.birthday || undefined,
      description: form.value.description || undefined,
      current_status: form.value.current_status || undefined,
      abilities,
      tags,
    })
    message.success('人物已更新')
    showEdit.value = false
  } catch (e) {
    message.error(getErrorMessage(e))
  }
}

function confirmDelete() {
  dialog.warning({
    title: '删除人物',
    content: `确定删除「${character.value?.name}」吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      const novelId = character.value?.novel_id
      await characterApi.delete(characterId)
      message.success('人物已删除')
      router.push(novelId ? `/novel/${novelId}` : '/')
    },
  })
}

onMounted(load)
</script>

<template>
  <NSpin :show="loading">
    <NButton quaternary style="margin-bottom: 12px; padding-left: 0" @click="goBack">
      <template #icon>
        <NIcon><ArrowBackOutline /></NIcon>
      </template>
      返回小说
    </NButton>

    <div class="page-header" style="display: flex; justify-content: space-between; align-items: flex-start">
      <div>
        <h1>{{ character?.name }}</h1>
        <p>人物详情</p>
      </div>
      <NSpace v-if="character">
        <NButton @click="openEdit">编辑</NButton>
        <NButton type="error" secondary @click="confirmDelete">删除</NButton>
      </NSpace>
    </div>

    <NCard v-if="character">
      <NDescriptions bordered :column="2">
        <NDescriptionsItem label="性别">{{ character.gender || '-' }}</NDescriptionsItem>
        <NDescriptionsItem label="生日">{{ character.birthday || '-' }}</NDescriptionsItem>
        <NDescriptionsItem label="当前状态" :span="2">{{ character.current_status || '-' }}</NDescriptionsItem>
        <NDescriptionsItem label="描述" :span="2">{{ character.description || '-' }}</NDescriptionsItem>
        <NDescriptionsItem label="能力" :span="2">
          <NSpace>
            <NTag v-for="a in character.abilities" :key="a" size="small">{{ a }}</NTag>
            <span v-if="!character.abilities.length">-</span>
          </NSpace>
        </NDescriptionsItem>
        <NDescriptionsItem label="标签" :span="2">
          <NSpace>
            <NTag v-for="t in character.tags" :key="t" size="small" type="info">{{ t }}</NTag>
            <span v-if="!character.tags.length">-</span>
          </NSpace>
        </NDescriptionsItem>
      </NDescriptions>
    </NCard>

    <NModal v-model:show="showEdit" preset="dialog" title="编辑人物" positive-text="保存" @positive-click="save">
      <NSpace vertical style="width: 100%">
        <NInput v-model:value="form.name" placeholder="姓名（同一小说内不可重名）" />
        <NInput v-model:value="form.gender" placeholder="性别" />
        <NInput v-model:value="form.birthday" placeholder="生日" />
        <NInput v-model:value="form.current_status" placeholder="当前状态" />
        <NInput v-model:value="form.abilities" placeholder="能力（逗号分隔）" />
        <NInput v-model:value="form.tags" placeholder="标签（逗号分隔）" />
        <NInput v-model:value="form.description" type="textarea" placeholder="描述" :rows="3" />
      </NSpace>
    </NModal>
  </NSpin>
</template>
