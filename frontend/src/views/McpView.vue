<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import {
  NButton,
  NCard,
  NCode,
  NDataTable,
  NDescriptions,
  NDescriptionsItem,
  NSpace,
  NSpin,
  NTag,
  useDialog,
  useMessage,
} from 'naive-ui'
import { mcpApi } from '@/api/client'
import type { McpCallLog, McpStatus } from '@/types'

const loading = ref(true)
const status = ref<McpStatus | null>(null)
const logs = ref<McpCallLog[]>([])
const message = useMessage()
const dialog = useDialog()

const httpConfig = computed(() => {
  const key = status.value?.api_key || '<your-api-key>'
  return `{
  "mcpServers": {
    "novelos": {
      "url": "http://localhost:8000/mcp/http",
      "transport": "streamable-http",
      "headers": {
        "Authorization": "Bearer ${key}"
      }
    }
  }
}`
})

const sseConfig = computed(() => {
  const key = status.value?.api_key || '<your-api-key>'
  return `{
  "mcpServers": {
    "novelos": {
      "url": "http://localhost:8000/mcp/sse",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer ${key}"
      }
    }
  }
}`
})

const curlExample = computed(() => {
  const key = status.value?.api_key || '<your-api-key>'
  return `curl -X POST http://localhost:8000/mcp/http \\
  -H "Authorization: Bearer ${key}" \\
  -H "Content-Type: application/json" \\
  -H "Accept: application/json, text/event-stream" \\
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'`
})

async function load() {
  loading.value = true
  try {
    status.value = await mcpApi.status()
    logs.value = (await mcpApi.logs()).items
  } finally {
    loading.value = false
  }
}

async function copyApiKey() {
  if (!status.value?.api_key) return
  await navigator.clipboard.writeText(status.value.api_key)
  message.success('API Key 已复制')
}

function regenerateKey() {
  dialog.warning({
    title: '重新生成 API Key',
    content: '重新生成后，旧 Key 将立即失效，所有 Agent 连接需更新配置。',
    positiveText: '确认',
    negativeText: '取消',
    onPositiveClick: async () => {
      const res = await mcpApi.regenerateApiKey()
      if (status.value) status.value.api_key = res.api_key
      message.success('API Key 已更新')
    },
  })
}

onMounted(load)
</script>

<template>
  <NSpin :show="loading">
    <div class="page-header">
      <h1>MCP 调试</h1>
      <p>Agent 连接状态与调用日志</p>
    </div>

    <NCard title="连接状态" style="margin-bottom: 16px">
      <NDescriptions v-if="status" bordered :column="2">
        <NDescriptionsItem label="状态">
          <NTag type="success">{{ status.status }}</NTag>
        </NDescriptionsItem>
        <NDescriptionsItem label="认证">
          <NTag :type="status.auth_enabled ? 'warning' : 'default'">
            {{ status.auth_enabled ? 'API Key 已启用' : '未启用' }}
          </NTag>
        </NDescriptionsItem>
        <NDescriptionsItem v-if="status.api_key" label="API Key" :span="2">
          <NSpace align="center">
            <NCode :code="status.api_key" language="text" />
            <NButton size="small" @click="copyApiKey">复制</NButton>
            <NButton size="small" type="warning" @click="regenerateKey">重新生成</NButton>
          </NSpace>
        </NDescriptionsItem>
        <NDescriptionsItem label="端点" :span="2">
          <div v-for="ep in status.endpoints" :key="ep.endpoint" style="margin-bottom: 8px">
            <NTag size="small" type="info">{{ ep.transport }}</NTag>
            <code style="margin-left: 8px">{{ ep.endpoint }}</code>
            <span style="margin-left: 8px; color: #6b7280">{{ ep.description }}</span>
          </div>
        </NDescriptionsItem>
        <NDescriptionsItem label="已注册 Tools" :span="2">
          <NTag v-for="t in status.tools" :key="t" size="small" style="margin-right: 6px">{{ t }}</NTag>
        </NDescriptionsItem>
      </NDescriptions>
    </NCard>

    <NCard title="HTTP + API Key 配置（推荐）" style="margin-bottom: 16px">
      <p style="color: #6b7280; margin-top: 0">
        支持 <code>Authorization: Bearer &lt;api_key&gt;</code> 或 <code>X-API-Key: &lt;api_key&gt;</code>
      </p>
      <NCode :code="httpConfig" language="json" word-wrap />
    </NCard>

    <NCard title="SSE 配置（Cherry Studio）" style="margin-bottom: 16px">
      <NCode :code="sseConfig" language="json" word-wrap />
    </NCard>

    <NCard title="curl 测试示例" style="margin-bottom: 16px">
      <NCode :code="curlExample" language="shell" word-wrap />
    </NCard>

    <NCard title="调用日志">
      <NDataTable
        :columns="[
          { title: '时间', key: 'created_at', width: 180 },
          { title: 'Tool', key: 'tool_name', width: 160 },
          { title: '成功', key: 'success', width: 80, render: (r: McpCallLog) => h(NTag, { type: r.success ? 'success' : 'error', size: 'small' }, () => r.success ? '是' : '否') },
          { title: '参数', key: 'arguments', ellipsis: { tooltip: true } },
          { title: '结果', key: 'result_summary', ellipsis: { tooltip: true } },
        ]"
        :data="logs"
        :bordered="false"
      />
    </NCard>
  </NSpin>
</template>
