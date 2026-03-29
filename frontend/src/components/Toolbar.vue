<script setup lang="ts">
import { useFileQueue } from '../composables/useFileQueue'
import { openFilePicker } from '../api/webview_bridge'
import { useSettings } from '../composables/useSettings'

const {
  totalCount,
  hasInvalid,
  clearFiles,
  validateFiles,
  addFiles,
} = useFileQueue()

const { settings } = useSettings()

async function handleAddFiles() {
  const res = await openFilePicker(settings.value.last_input_dir)
  if (res.success && res.data && res.data.length > 0) {
    await addFiles(res.data)
  }
}

function handleClear() {
  if (totalCount.value === 0) return
  if (!confirm('Are you sure you want to clear all files?')) return
  clearFiles()
}

function handleValidate() {
  validateFiles()
}
</script>

<template>
  <div class="flex items-center gap-2 p-3 bg-base-200 rounded-lg">
    <button
      class="btn btn-primary btn-sm"
      :disabled="false"
      @click="handleAddFiles"
    >
      Add Files
    </button>

    <button
      class="btn btn-warning btn-sm"
      :disabled="totalCount === 0"
      @click="handleClear"
    >
      Clear
    </button>

    <button
      class="btn btn-info btn-sm"
      :disabled="totalCount === 0"
      @click="handleValidate"
    >
      Validate
    </button>

    <div class="flex-1" />

    <span
      v-if="hasInvalid"
      class="text-warning text-sm"
    >
      Contains invalid files
    </span>
  </div>
</template>
