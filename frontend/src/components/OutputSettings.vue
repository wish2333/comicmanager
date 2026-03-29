<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useSettings } from '../composables/useSettings'
import { openDirectoryPicker } from '../api/webview_bridge'
import FormatSelector from './FormatSelector.vue'

const { settings } = useSettings()

const outputFilename = ref('merged')
const outputDir = ref('')
const preserveMetadata = ref(true)

onMounted(() => {
  outputDir.value = settings.value.last_output_dir
  preserveMetadata.value = settings.value.preserve_metadata
})

async function pickDirectory() {
  const res = await openDirectoryPicker(outputDir.value)
  if (res.success && res.data) {
    outputDir.value = res.data
  }
}


defineExpose({
  outputFilename,
  outputDir,
  preserveMetadata,
})
</script>

<template>
  <div class="flex flex-col gap-3 p-3 bg-base-200 rounded-lg">
    <h3 class="font-semibold text-sm">Output Settings</h3>

    <div class="flex items-center gap-2">
      <label class="label text-sm shrink-0">Filename:</label>
      <input
        v-model="outputFilename"
        type="text"
        placeholder="merged"
        class="input input-bordered input-sm flex-1"
      />
      <span class="text-sm text-base-content/60">.cbz</span>
    </div>

    <div class="flex items-center gap-2">
      <label class="label text-sm shrink-0">Directory:</label>
      <input
        v-model="outputDir"
        type="text"
        placeholder="Output directory"
        class="input input-bordered input-sm flex-1"
      />
      <button class="btn btn-sm btn-outline" @click="pickDirectory">
        Browse
      </button>
    </div>

    <!-- Extract format selector -->
    <div>
      <label class="label">
        <span class="label-text text-sm font-semibold">Extract Formats</span>
      </label>
      <FormatSelector />
    </div>

    <label class="label cursor-pointer gap-2 justify-start">
      <input
        v-model="preserveMetadata"
        type="checkbox"
        class="checkbox checkbox-sm checkbox-primary"
      />
      <span class="label-text text-sm">Include ComicInfo.xml metadata</span>
    </label>
  </div>
</template>
