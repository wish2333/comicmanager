/** Reactive file queue state management. */

import { ref, computed } from 'vue'
import type { QueuedFile } from '../types'
import * as filesApi from '../api/files'

const fileList = ref<QueuedFile[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

const totalCount = computed(() => fileList.value.length)
const totalPages = computed(() => fileList.value.reduce((sum, f) => sum + f.page_count, 0))
const totalSize = computed(() => fileList.value.reduce((sum, f) => sum + f.size, 0))
const cbzCount = computed(() => fileList.value.filter((f) => f.type === 'CBZ').length)
const zipCount = computed(() => fileList.value.filter((f) => f.type === 'ZIP').length)
const hasInvalid = computed(() => fileList.value.some((f) => !f.valid))

function setFiles(files: QueuedFile[]) {
  fileList.value = files
}

async function addFiles(paths: string[]) {
  loading.value = true
  error.value = null
  try {
    const res = await filesApi.addFiles(paths)
    if (res.success && res.data) {
      fileList.value = res.data
    } else {
      error.value = res.error || 'Failed to add files'
    }
  } catch (e) {
    error.value = String(e)
  } finally {
    loading.value = false
  }
}

async function fetchFiles() {
  loading.value = true
  error.value = null
  try {
    const res = await filesApi.getFiles()
    if (res.success && res.data) {
      fileList.value = res.data
    }
  } catch (e) {
    error.value = String(e)
  } finally {
    loading.value = false
  }
}

async function removeFiles(indices: number[]) {
  const res = await filesApi.removeFiles(indices)
  if (res.success && res.data) {
    fileList.value = res.data
  }
}

async function reorderFiles(fromIndex: number, toIndex: number) {
  const res = await filesApi.reorderFiles(fromIndex, toIndex)
  if (res.success && res.data) {
    fileList.value = res.data
  }
}

async function clearFiles() {
  const res = await filesApi.clearFiles()
  if (res.success && res.data) {
    fileList.value = res.data
  }
}

async function validateFiles() {
  loading.value = true
  try {
    const res = await filesApi.validateFiles()
    if (res.success && res.data) {
      fileList.value = res.data.files
    }
  } catch (e) {
    error.value = String(e)
  } finally {
    loading.value = false
  }
}

async function sortByName(reverse: boolean = false) {
  const res = await filesApi.sortFiles('name', reverse)
  if (res.success && res.data) {
    fileList.value = res.data
    selectedIndices.value = new Set()
  }
}

function moveUp(index: number) {
  if (index <= 0) return
  reorderFiles(index, index - 1)
}

function moveDown(index: number) {
  if (index >= fileList.value.length - 1) return
  reorderFiles(index, index + 1)
}

function moveToTop(index: number) {
  if (index === 0) return
  reorderFiles(index, 0)
}

function moveToBottom(index: number) {
  if (index === fileList.value.length - 1) return
  reorderFiles(index, fileList.value.length - 1)
}

export function useFileQueue() {
  return {
    fileList,
    loading,
    error,
    totalCount,
    totalPages,
    totalSize,
    cbzCount,
    zipCount,
    hasInvalid,
    setFiles,
    addFiles,
    fetchFiles,
    removeFiles,
    reorderFiles,
    clearFiles,
    validateFiles,
    sortByName,
    moveUp,
    moveDown,
    moveToTop,
    moveToBottom,
  }
}
