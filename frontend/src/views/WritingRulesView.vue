<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { NButton, NCard, NInput, NSpace, NSpin, NText, useMessage } from 'naive-ui'
import { getErrorMessage, writingRulesApi } from '@/api/client'

const loading = ref(true)
const saving = ref(false)
const content = ref('')
const savedContent = ref('')
const filePath = ref('')
const message = useMessage()

const dirty = computed(() => content.value !== savedContent.value)

async function load() {
  loading.value = true
  try {
    const data = await writingRulesApi.get()
    content.value = data.content
    savedContent.value = data.content
    filePath.value = data.file_path
  } catch (error) {
    message.error(getErrorMessage(error))
  } finally {
    loading.value = false
  }
}

async function save() {
  if (!dirty.value) return
  saving.value = true
  try {
    const data = await writingRulesApi.update(content.value)
    content.value = data.content
    savedContent.value = data.content
    filePath.value = data.file_path
    message.success('写作规则已保存')
  } catch (error) {
    message.error(getErrorMessage(error))
  } finally {
    saving.value = false
  }
}

function reset() {
  content.value = savedContent.value
}

onMounted(load)
</script>

<template>
  <NSpin :show="loading">
    <div class="page-header" style="display: flex; justify-content: space-between; align-items: flex-start">
      <div>
        <h1>写作规则</h1>
        <p>供 MCP 与 LLM 读取，生成或续写正文时需遵守</p>
      </div>
      <NSpace>
        <NButton :disabled="!dirty || saving" @click="reset">撤销修改</NButton>
        <NButton type="primary" :disabled="!dirty" :loading="saving" @click="save">保存</NButton>
      </NSpace>
    </div>

    <NCard>
      <NText v-if="filePath" depth="3" style="display: block; margin-bottom: 12px; font-size: 13px">
        存储路径：{{ filePath }}
      </NText>
      <NInput
        v-model:value="content"
        type="textarea"
        placeholder="在此编辑写作规则（Markdown）"
        :autosize="{ minRows: 18, maxRows: 40 }"
        class="rules-editor"
      />
    </NCard>
  </NSpin>
</template>

<style scoped>
.rules-editor :deep(textarea) {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New',
    monospace;
  font-size: 14px;
  line-height: 1.6;
}
</style>
