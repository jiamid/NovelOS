<script setup lang="ts">
import { computed, h, onMounted } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import {
  NConfigProvider,
  NDialogProvider,
  NLayout,
  NLayoutContent,
  NLayoutSider,
  NMenu,
  NIcon,
  NMessageProvider,
  NSpace,
  NText,
} from 'naive-ui'
import { BookOutline, GlobeOutline, HardwareChipOutline, HomeOutline } from '@vicons/ionicons5'
import { useAppStore } from '@/stores/app'

const route = useRoute()
const router = useRouter()
const store = useAppStore()

const themeOverrides = {
  common: {
    primaryColor: '#4f46e5',
    primaryColorHover: '#6366f1',
    primaryColorPressed: '#4338ca',
    primaryColorSuppl: '#818cf8',
    borderRadius: '14px',
    fontFamily:
      '-apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  },
  Card: {
    borderRadius: '20px',
  },
  Button: {
    borderRadiusMedium: '12px',
    borderRadiusSmall: '10px',
  },
  Input: {
    borderRadius: '12px',
  },
  DataTable: {
    thColor: '#f8fafc',
    thTextColor: '#64748b',
    borderRadius: '14px',
  },
  Tabs: {
    tabFontWeightActive: '700',
  },
}

const activeKey = computed(() => {
  if (route.name === 'dashboard') return 'dashboard'
  if (route.name === 'mcp') return 'mcp'
  if (route.name === 'novel') return `novel-${route.params.id}`
  if (route.name === 'chapter') return `chapter-${route.params.id}`
  return String(route.name || 'dashboard')
})

const menuOptions = computed(() => {
  const items = [
    {
      label: 'Dashboard',
      key: 'dashboard',
      icon: () => h(NIcon, null, { default: () => h(HomeOutline) }),
    },
    {
      label: '小说',
      key: 'novels',
      icon: () => h(NIcon, null, { default: () => h(GlobeOutline) }),
      children: store.novels.map((n) => ({
        label: n.name,
        key: `novel-${n.id}`,
      })),
    },
    {
      label: 'MCP',
      key: 'mcp',
      icon: () => h(NIcon, null, { default: () => h(HardwareChipOutline) }),
    },
  ]
  return items
})

function handleMenuSelect(key: string) {
  if (key === 'dashboard') router.push('/')
  else if (key === 'mcp') router.push('/mcp')
  else if (key.startsWith('novel-')) router.push(`/novel/${key.replace('novel-', '')}`)
}

onMounted(() => store.loadNovels())
</script>

<template>
  <NConfigProvider :theme-overrides="themeOverrides">
    <NMessageProvider>
      <NDialogProvider>
        <NLayout has-sider class="app-shell">
          <NLayoutSider :width="260" :native-scrollbar="false" class="app-sider">
            <div class="brand-panel">
              <NSpace align="center" :size="8">
                <div class="brand-icon">
                  <NIcon size="24">
                    <BookOutline />
                  </NIcon>
                </div>
                <div>
                  <NText strong class="brand-title">NovelOS</NText>
                  <NText depth="3" class="brand-subtitle">小说知识操作系统</NText>
                </div>
              </NSpace>
            </div>
            <NMenu
              class="app-menu"
              :value="activeKey"
              :options="menuOptions"
              @update:value="handleMenuSelect"
            />
          </NLayoutSider>
          <NLayout class="app-main">
            <NLayoutContent>
              <main class="content-surface">
                <RouterView />
              </main>
            </NLayoutContent>
          </NLayout>
        </NLayout>
      </NDialogProvider>
    </NMessageProvider>
  </NConfigProvider>
</template>
