<script setup lang="ts">
import { useFileQueue } from '../composables/useFileQueue'

const { totalCount, totalPages, cbzCount, zipCount } = useFileQueue()

function formatSize(bytes: number): string {
  for (const unit of ['B', 'KB', 'MB', 'GB']) {
    if (bytes < 1024) return `${bytes.toFixed(1)} ${unit}`
    bytes /= 1024
  }
  return `${bytes.toFixed(1)} TB`
}

const { totalSize } = useFileQueue()
</script>

<template>
  <div class="flex items-center gap-4 px-3 py-2 bg-base-200 text-sm text-base-content/70">
    <span>Files: {{ totalCount }} (CBZ: {{ cbzCount }}, ZIP: {{ zipCount }})</span>
    <span class="divider divider-horizontal m-0" />
    <span>Pages: {{ totalPages }}</span>
    <span class="divider divider-horizontal m-0" />
    <span>Total: {{ formatSize(totalSize) }}</span>
  </div>
</template>
