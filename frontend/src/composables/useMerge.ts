/** Merge operation state and SSE progress management. */

import { ref } from 'vue'
import type { MergeProgressEvent, MergeResult } from '../types'
import { startMerge, parseSSEStream } from '../api/merge'

const merging = ref(false)
const progress = ref<MergeProgressEvent | null>(null)
const result = ref<MergeResult | null>(null)
const mergeError = ref<string | null>(null)

const progressPercent = ref(0)

function reset() {
  merging.value = false
  progress.value = null
  result.value = null
  mergeError.value = null
  progressPercent.value = 0
}

async function executeMerge(params: {
  output_filename: string
  output_dir: string
  preserve_metadata: boolean
  zip_formats: string[]
}) {
  reset()
  merging.value = true

  try {
    const response = await startMerge(params)

    if (!response.ok) {
      const body = await response.json().catch(() => ({ error: 'Merge request failed' }))
      mergeError.value = body.error || `HTTP ${response.status}`
      merging.value = false
      return
    }

    parseSSEStream(
      response,
      (event: MergeProgressEvent) => {
        progress.value = event

        if (event.total_files > 0) {
          progressPercent.value = Math.round((event.current_index / event.total_files) * 100)
        }
      },
      (mergeResult: MergeResult) => {
        result.value = mergeResult
        merging.value = false
      },
      (err: string) => {
        mergeError.value = err
        merging.value = false
      },
    )
  } catch (e) {
    mergeError.value = String(e)
    merging.value = false
  }
}

export function useMerge() {
  return {
    merging,
    progress,
    result,
    mergeError,
    progressPercent,
    executeMerge,
    reset,
  }
}
