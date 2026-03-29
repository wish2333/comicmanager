<script setup lang="ts">
import type { QueuedFile } from '../types'

defineProps<{
  file: QueuedFile
  index: number
  selected: boolean
}>()

const emit = defineEmits<{
  select: [index: number, shiftKey: boolean, ctrlKey: boolean]
  remove: [index: number]
}>()

function formatSize(bytes: number): string {
  for (const unit of ['B', 'KB', 'MB', 'GB']) {
    if (bytes < 1024) return `${bytes.toFixed(1)} ${unit}`
    bytes /= 1024
  }
  return `${bytes.toFixed(1)} TB`
}
</script>

<template>
  <tr
    class="hover cursor-pointer"
    :class="{ 'bg-error/10': !file.valid, 'bg-primary/5': selected }"
    @click="emit('select', index, $event.shiftKey, $event.ctrlKey)"
  >
    <td class="text-center w-12">{{ index + 1 }}</td>
    <td>
      <div class="font-medium truncate max-w-xs" :title="file.path">
        {{ file.name }}
      </div>
    </td>
    <td class="text-center">
      <span
        class="badge badge-sm"
        :class="file.type === 'CBZ' ? 'badge-primary' : 'badge-secondary'"
      >
        {{ file.type }}
      </span>
    </td>
    <td class="text-right font-mono text-sm">{{ formatSize(file.size) }}</td>
    <td class="text-center">{{ file.page_count }}</td>
    <td class="text-center">
      <span
        class="badge badge-sm"
        :class="file.valid ? 'badge-success' : 'badge-error'"
      >
        {{ file.valid ? 'OK' : 'Error' }}
      </span>
    </td>
    <td class="w-12 text-center">
      <button
        class="btn btn-ghost btn-xs text-error"
        title="Remove"
        @click.stop="emit('remove', index)"
      >
        &#x2715;
      </button>
    </td>
  </tr>
</template>
