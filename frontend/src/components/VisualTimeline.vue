<script setup lang="ts">
import { LocationOutline, PeopleOutline, TimeOutline } from '@vicons/ionicons5'
import { NButton, NCard, NEmpty, NIcon, NSpace, NTag, NText } from 'naive-ui'
import type { TimelineItem } from '@/types'

defineProps<{
  items: TimelineItem[]
}>()

const emit = defineEmits<{
  edit: [eventId: string]
  delete: [item: TimelineItem]
}>()
</script>

<template>
  <div v-if="items.length" class="visual-timeline">
    <div v-for="item in items" :key="item.id" class="timeline-item">
      <div class="timeline-axis">
        <div class="timeline-dot" />
        <div class="timeline-line" />
      </div>
      <NCard class="timeline-card" size="small">
        <div class="timeline-card-header">
          <NSpace align="center" :size="8">
            <NTag size="small" type="info" round>#{{ item.sequence + 1 }}</NTag>
            <NText v-if="item.event?.occur_time" depth="2">
              <NIcon size="14" style="vertical-align: -2px; margin-right: 4px">
                <TimeOutline />
              </NIcon>
              {{ item.event.occur_time }}
            </NText>
          </NSpace>
          <NSpace :size="4">
            <NButton v-if="item.event" size="tiny" quaternary @click="emit('edit', item.event!.id)">
              编辑
            </NButton>
            <NButton size="tiny" quaternary type="error" @click="emit('delete', item)">删除</NButton>
          </NSpace>
        </div>

        <h3 class="timeline-title">{{ item.event?.title || '未命名事件' }}</h3>

        <NSpace v-if="item.event?.location || item.event?.characters?.length" :size="12" style="margin-bottom: 8px">
          <NText v-if="item.event?.location" depth="3">
            <NIcon size="14" style="vertical-align: -2px; margin-right: 4px">
              <LocationOutline />
            </NIcon>
            {{ item.event.location }}
          </NText>
          <NSpace v-if="item.event?.characters?.length" align="center" :size="4">
            <NIcon size="14" depth="3"><PeopleOutline /></NIcon>
            <NTag
              v-for="c in item.event.characters"
              :key="c.id"
              size="small"
              type="warning"
              round
            >
              {{ c.name }}
            </NTag>
          </NSpace>
        </NSpace>

        <p v-if="item.event?.description" class="timeline-desc">{{ item.event.description }}</p>
      </NCard>
    </div>
  </div>
  <NEmpty v-else description="暂无时间线事件，点击「添加事件」开始记录" />
</template>

<style scoped>
.visual-timeline {
  padding: 8px 0;
}

.timeline-item {
  display: flex;
  gap: 16px;
  margin-bottom: 0;
}

.timeline-item:last-child .timeline-line {
  display: none;
}

.timeline-axis {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 20px;
  flex-shrink: 0;
  padding-top: 18px;
}

.timeline-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #2563eb;
  border: 2px solid #dbeafe;
  flex-shrink: 0;
}

.timeline-line {
  flex: 1;
  width: 2px;
  background: #e5e7eb;
  min-height: 24px;
}

.timeline-card {
  flex: 1;
  margin-bottom: 20px;
}

.timeline-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.timeline-title {
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 600;
}

.timeline-desc {
  margin: 0;
  color: #6b7280;
  line-height: 1.6;
  white-space: pre-wrap;
}
</style>
