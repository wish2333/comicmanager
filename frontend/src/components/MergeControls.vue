<script setup lang="ts">
import { computed } from 'vue'
import { useMerge } from '../composables/useMerge'
import { useFileQueue } from '../composables/useFileQueue'
import { useSettings } from '../composables/useSettings'

const { merging, progress, result, mergeError, progressPercent, executeMerge } = useMerge()
const { totalCount, hasInvalid } = useFileQueue()
const { settings } = useSettings()

const props = defineProps<{
  outputFilename: string
  outputDir: string
  preserveMetadata: boolean
}>()

const canMerge = computed(() => totalCount.value > 0 && !hasInvalid.value && !merging.value)

async function handleMerge() {
  if (!props.outputFilename.trim()) {
    alert('Please enter an output filename')
    return
  }
  if (!props.outputDir.trim()) {
    alert('Please select an output directory')
    return
  }

  await executeMerge({
    output_filename: props.outputFilename.trim(),
    output_dir: props.outputDir.trim(),
    preserve_metadata: props.preserveMetadata,
    zip_formats: settings.value.zip_image_formats,
  })
}

function getStageLabel(stage: string): string {
  const labels: Record<string, string> = {
    validating: 'Validating...',
    extracting: 'Extracting...',
    merging: 'Merging...',
    writing: 'Writing...',
    done: 'Done!',
    error: 'Error!',
  }
  return labels[stage] || stage
}
</script>

<template>
  <div class="flex flex-col gap-3 p-3 bg-base-200 rounded-lg">
    <!-- Progress bar -->
    <div v-if="merging || result" class="w-full">
      <div class="flex justify-between text-sm mb-1">
        <span v-if="progress">
          {{ getStageLabel(progress.stage) }} - {{ progress.message }}
        </span>
        <span v-else-if="result && result.success">
          Merge complete!
        </span>
        <span v-else>
          Processing...
        </span>
        <span>{{ progressPercent }}%</span>
      </div>
      <progress
        class="progress progress-primary w-full"
        :value="progressPercent"
        max="100"
      />
    </div>

    <!-- Error message -->
    <div v-if="mergeError" class="alert alert-error text-sm">
      {{ mergeError }}
    </div>

    <!-- Result message -->
    <div v-if="result && result.success" class="alert alert-success text-sm">
      <span>
        Merge successful!
        {{ result.total_pages }} pages from {{ result.merged_files.length }} files.
        Output: {{ result.output_path }}
      </span>
    </div>

    <div v-if="result && !result.success" class="alert alert-error text-sm">
      <span> Merge failed: {{ result.errors.join(', ') }} </span>
    </div>

    <!-- Merge button -->
    <button
      class="btn btn-success"
      :class="{ 'btn-disabled': !canMerge, loading: merging }"
      :disabled="!canMerge"
      @click="handleMerge"
    >
      <template v-if="merging">
        <span class="loading loading-spinner loading-sm" />
        Merging...
      </template>
      <template v-else>
        Start Merge
      </template>
    </button>
  </div>
</template>
