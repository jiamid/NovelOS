<script setup lang="ts">
import { onBeforeUnmount, ref, watch } from 'vue'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'

const props = defineProps<{ modelValue: string }>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

const suppressEmit = ref(true)

const editor = useEditor({
  extensions: [StarterKit],
  onCreate: ({ editor: e }) => {
    e.commands.setContent(props.modelValue || '', { emitUpdate: false })
    queueMicrotask(() => {
      suppressEmit.value = false
    })
  },
  onUpdate: ({ editor: e }) => {
    if (suppressEmit.value) return
    emit('update:modelValue', e.getText())
  },
})

watch(
  () => props.modelValue,
  (val) => {
    if (!editor.value) return
    const current = editor.value.getText()
    if (current === val) return
    suppressEmit.value = true
    editor.value.commands.setContent(val || '', { emitUpdate: false })
    queueMicrotask(() => {
      suppressEmit.value = false
    })
  }
)

onBeforeUnmount(() => editor.value?.destroy())
</script>

<template>
  <div class="editor-area">
    <EditorContent :editor="editor" />
  </div>
</template>
