<script setup lang="ts">
import { ref, computed } from 'vue'
import { useFileQueue } from '../composables/useFileQueue'
import FileRow from './FileRow.vue'

const {
  fileList,
  totalCount,
  removeFiles,
  moveUp,
  moveDown,
  moveToTop,
  moveToBottom,
  sortByName,
} = useFileQueue()

const emit = defineEmits<{
  fillFilename: [name: string]
}>()

const selectedIndices = ref<Set<number>>(new Set())
const sortReverse = ref(false)

function handleFillFilename() {
  if (fileList.value.length > 0) {
    const name = fileList.value[0].name
    const stem = name.replace(/\.[^.]+$/, '')
    emit('fillFilename', stem)
  }
}

const allSelected = computed({
  get: () => totalCount.value > 0 && selectedIndices.value.size === totalCount.value,
  set: (val: boolean) => {
    if (val) {
      selectedIndices.value = new Set(fileList.value.map((_, i) => i))
    } else {
      selectedIndices.value = new Set()
    }
  },
})

const hasSelection = computed(() => selectedIndices.value.size > 0)

const lastClickedIndex = ref(-1)

function toggleSelect(index: number, shiftKey: boolean, ctrlKey: boolean) {
  if (shiftKey) {
    // Shift-click: select range from last clicked index
    const anchor = lastClickedIndex.value >= 0 ? lastClickedIndex.value : index
    const start = Math.min(anchor, index)
    const end = Math.max(anchor, index)
    const newSet = new Set(selectedIndices.value)
    for (let i = start; i <= end; i++) {
      newSet.add(i)
    }
    selectedIndices.value = newSet
  } else if (ctrlKey) {
    // Ctrl-click: toggle individual item (keep others selected)
    const newSet = new Set(selectedIndices.value)
    if (newSet.has(index)) {
      newSet.delete(index)
    } else {
      newSet.add(index)
    }
    selectedIndices.value = newSet
  } else {
    // Normal click: select only this item
    selectedIndices.value = new Set([index])
  }
  lastClickedIndex.value = index
}

function getFirstSelectedIndex(): number {
  const sorted = [...selectedIndices.value].sort((a, b) => a - b)
  return sorted[0] ?? -1
}

function getLastSelectedIndex(): number {
  const sorted = [...selectedIndices.value].sort((a, b) => a - b)
  return sorted[sorted.length - 1] ?? -1
}

async function handleMoveToTop() {
  if (selectedIndices.value.size === 0) return
  const firstIdx = getFirstSelectedIndex()
  if (firstIdx <= 0) return
  await moveToTop(firstIdx)
  // After reorder, the items are now at positions 0..N
  const count = selectedIndices.value.size
  selectedIndices.value = new Set(Array.from({ length: count }, (_, i) => i))
}

async function handleMoveToBottom() {
  if (selectedIndices.value.size === 0) return
  const lastIdx = getLastSelectedIndex()
  const total = fileList.value.length
  if (lastIdx >= total - 1) return
  await moveToBottom(lastIdx)
  // After reorder, items are now at the end
  const count = selectedIndices.value.size
  selectedIndices.value = new Set(
    Array.from({ length: count }, (_, i) => total - count + i)
  )
}

async function handleMoveUp() {
  if (selectedIndices.value.size === 0) return
  const firstIdx = getFirstSelectedIndex()
  if (firstIdx <= 0) return
  // Move the first selected item up by one
  await moveUp(firstIdx)
  // Update all selected indices
  const newSet = new Set<number>()
  for (const idx of selectedIndices.value) {
    newSet.add(idx - 1)
  }
  selectedIndices.value = newSet
}

async function handleMoveDown() {
  if (selectedIndices.value.size === 0) return
  const lastIdx = getLastSelectedIndex()
  const total = fileList.value.length
  if (lastIdx >= total - 1) return
  // Move the last selected item down by one
  await moveDown(lastIdx)
  // Update all selected indices
  const newSet = new Set<number>()
  for (const idx of selectedIndices.value) {
    newSet.add(idx + 1)
  }
  selectedIndices.value = newSet
}

async function handleRemoveSelected() {
  if (selectedIndices.value.size === 0) return
  await removeFiles([...selectedIndices.value])
  selectedIndices.value = new Set()
}
</script>

<template>
  <div class="flex flex-col flex-1 min-h-0">
    <div class="flex items-center gap-2 p-2 bg-base-200 rounded-t-lg">
      <label class="label cursor-pointer gap-2">
        <input
          v-model="allSelected"
          type="checkbox"
          class="checkbox checkbox-sm checkbox-primary"
        />
        <span class="label-text text-sm">Select All</span>
      </label>

      <div class="flex-1" />

      <button
        class="btn btn-xs btn-ghost"
        :disabled="totalCount === 0"
        title="Sort by filename (A-Z / Z-A)"
        @click="sortReverse = !sortReverse; sortByName(sortReverse.value)"
      >
        Sort A-Z
      </button>
      <button
        class="btn btn-xs btn-ghost"
        :disabled="totalCount === 0"
        title="Use first file's name as output filename"
        @click="handleFillFilename"
      >
        Fill Name
      </button>
      <button
        class="btn btn-xs btn-ghost"
        :disabled="!hasSelection || getFirstSelectedIndex() === 0"
        title="Move selected to top"
        @click="handleMoveToTop"
      >
        Top
      </button>
      <button
        class="btn btn-xs btn-ghost"
        :disabled="!hasSelection || getFirstSelectedIndex() === 0"
        title="Move selected up"
        @click="handleMoveUp"
      >
        Up
      </button>
      <button
        class="btn btn-xs btn-ghost"
        :disabled="!hasSelection || getLastSelectedIndex() === fileList.length - 1"
        title="Move selected down"
        @click="handleMoveDown"
      >
        Down
      </button>
      <button
        class="btn btn-xs btn-ghost"
        :disabled="!hasSelection || getLastSelectedIndex() === fileList.length - 1"
        title="Move selected to bottom"
        @click="handleMoveToBottom"
      >
        Bottom
      </button>
      <button
        class="btn btn-xs btn-error btn-ghost"
        :disabled="!hasSelection"
        @click="handleRemoveSelected"
      >
        Remove ({{ selectedIndices.size }})
      </button>
    </div>

    <div class="flex-1 min-h-0 overflow-y-auto overflow-x-hidden">
      <table v-if="fileList.length > 0" class="table table-sm" style="table-layout: fixed;">
        <thead class="sticky top-0 z-10 bg-base-200">
          <tr>
            <th class="w-12 text-center">#</th>
            <th>Name</th>
            <th class="w-16 text-center">Type</th>
            <th class="w-24 text-right">Size</th>
            <th class="w-16 text-center">Pages</th>
            <th class="w-16 text-center">Status</th>
            <th class="w-16 text-center">Actions</th>
          </tr>
        </thead>
        <tbody>
          <FileRow
            v-for="(file, index) in fileList"
            :key="file.path"
            :file="file"
            :index="index"
            :selected="selectedIndices.has(index)"
            @select="toggleSelect"
            @remove="removeFiles([$event])"
          />
        </tbody>
      </table>

      <div v-else class="flex items-center justify-center h-full text-base-content/40">
        <div class="text-center">
          <p class="text-lg">No files added</p>
          <p class="text-sm">Click "Add Files" to get started</p>
        </div>
      </div>
    </div>
  </div>
</template>
