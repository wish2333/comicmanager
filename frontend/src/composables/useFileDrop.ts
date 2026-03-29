/** OS file drop composable - visual feedback and file path retrieval.

Visual feedback: window-level dragenter/dragover/dragleave listeners
  (reliable, fire immediately on component mount).

File path retrieval: after a drop, polls window.pywebview.api.get_dropped_files()
  to get real OS paths extracted by pywebview's CoreWebView2File bridge.
  The bridge is set up by Python's setup_drag_drop() which runs on page load.
*/

import { ref, onUnmounted } from 'vue'

const isDragging = ref(false)
let dragCounter = 0
let dropCallback: ((paths: string[]) => void) | null = null
let registered = false

function onDragEnter(e: DragEvent) {
  e.preventDefault()
  dragCounter++
  isDragging.value = true
}

function onDragOver(e: DragEvent) {
  e.preventDefault()
}

function onDragLeave() {
  dragCounter--
  if (dragCounter <= 0) {
    dragCounter = 0
    isDragging.value = false
  }
}

async function onDrop(e: DragEvent) {
  e.preventDefault()
  dragCounter = 0
  isDragging.value = false

  if (!dropCallback) return

  const api = (window as any).pywebview?.api
  if (!api || typeof api.get_dropped_files !== 'function') {
    console.warn('pywebview API not available, file drop not supported')
    return
  }

  // Poll for dropped files. pywebview's Python side processes the
  // CoreWebView2File paths asynchronously after the JS bridge call.
  for (let attempt = 0; attempt < 30; attempt++) {
    try {
      const result = await api.get_dropped_files()
      if (result.success && result.data && result.data.length > 0) {
        dropCallback(result.data)
        return
      }
    } catch {
      // Ignore, retry
    }
    await new Promise((r) => setTimeout(r, 100))
  }
}

function _registerListeners() {
  if (registered) return
  registered = true
  window.addEventListener('dragenter', onDragEnter)
  window.addEventListener('dragover', onDragOver)
  window.addEventListener('dragleave', onDragLeave)
  window.addEventListener('drop', onDrop)
}

export function useFileDrop(onFilesDropped?: (paths: string[]) => void) {
  if (onFilesDropped) {
    dropCallback = onFilesDropped
  }

  _registerListeners()

  onUnmounted(() => {
    if (registered) {
      registered = false
      window.removeEventListener('dragenter', onDragEnter)
      window.removeEventListener('dragover', onDragOver)
      window.removeEventListener('dragleave', onDragLeave)
      window.removeEventListener('drop', onDrop)
    }
  })

  return { isDragging }
}
