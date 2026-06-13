import { h, type VNode } from 'vue'
import { NButton, NPopconfirm, NSpace } from 'naive-ui'

export function tableActions<T>(
  row: T,
  handlers: {
    onEdit?: (row: T) => void
    onDelete?: (row: T) => void
    onView?: (row: T) => void
    viewLabel?: string
  }
): VNode {
  const buttons: VNode[] = []
  if (handlers.onView) {
    buttons.push(
      h(
        NButton,
        { text: true, type: 'primary', onClick: () => handlers.onView!(row) },
        () => handlers.viewLabel || '查看'
      )
    )
  }
  if (handlers.onEdit) {
    buttons.push(
      h(NButton, { text: true, type: 'info', onClick: () => handlers.onEdit!(row) }, () => '编辑')
    )
  }
  if (handlers.onDelete) {
    buttons.push(
      h(
        NPopconfirm,
        { onPositiveClick: () => handlers.onDelete!(row) },
        {
          trigger: () => h(NButton, { text: true, type: 'error' }, () => '删除'),
          default: () => '确定删除？此操作不可恢复。',
        }
      )
    )
  }
  return h(NSpace, { size: 8 }, () => buttons)
}
