<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import cytoscape from 'cytoscape'
import type { Character, CharacterRelation } from '@/types'

const props = defineProps<{
  characters: Character[]
  relations: CharacterRelation[]
}>()

const container = ref<HTMLDivElement | null>(null)
let cy: cytoscape.Core | null = null

function render() {
  if (!container.value) return
  if (cy) cy.destroy()

  const charIds = new Set(props.characters.map((c) => c.id))

  const nodes = props.characters.map((c) => ({
    data: { id: c.id, label: c.name },
  }))

  const edges = props.relations
    .filter((r) => charIds.has(r.source_id) && charIds.has(r.target_id))
    .map((r) => ({
      data: {
        id: `${r.source_id}-${r.target_id}`,
        source: r.source_id,
        target: r.target_id,
        label: r.relation_type,
      },
    }))

  cy = cytoscape({
    container: container.value,
    elements: [...nodes, ...edges],
    style: [
      {
        selector: 'node',
        style: {
          label: 'data(label)',
          'text-valign': 'center',
          'text-halign': 'center',
          'background-color': '#fef3c7',
          'border-color': '#d97706',
          'border-width': '2px',
          shape: 'ellipse',
          width: '80px',
          height: '80px',
          'font-size': '12px',
          'text-wrap': 'wrap',
          'text-max-width': '70px',
        },
      },
      {
        selector: 'edge',
        style: {
          label: 'data(label)',
          'font-size': '10px',
          'text-rotation': 'autorotate',
          'text-margin-y': -10,
          width: '2px',
          'line-color': '#94a3b8',
          'target-arrow-color': '#94a3b8',
          'target-arrow-shape': 'triangle',
          'curve-style': 'bezier',
        },
      },
    ] as any,
    layout: { name: 'cose', animate: false, padding: 30 },
  })
}

watch(() => [props.characters, props.relations], render, { deep: true })
onMounted(render)
onUnmounted(() => cy?.destroy())
</script>

<template>
  <div ref="container" class="relation-graph" />
</template>
