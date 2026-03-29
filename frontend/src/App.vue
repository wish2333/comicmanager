<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Toolbar from './components/Toolbar.vue'
import FileList from './components/FileList.vue'
import OutputSettings from './components/OutputSettings.vue'
import MergeControls from './components/MergeControls.vue'
import StatsBar from './components/StatsBar.vue'
import FileDropZone from './components/FileDropZone.vue'
import SettingsModal from './components/SettingsModal.vue'
import ToastContainer from './components/ToastContainer.vue'
import { useSettings } from './composables/useSettings'
import { useTheme } from './composables/useTheme'
import { useKeyboard } from './composables/useKeyboard'
import { useFileQueue } from './composables/useFileQueue'
import { useFileDrop } from './composables/useFileDrop'
import { openFilePicker } from './api/webview_bridge'

const { fetchSettings } = useSettings()
const { currentTheme, toggleTheme } = useTheme()
const outputSettingsRef = ref<InstanceType<typeof OutputSettings>>()
const settingsOpen = ref(false)

const { addFiles, removeFiles } = useFileQueue()

// Register drag-drop handler here (App.vue is always mounted)
useFileDrop(async (paths) => {
  await addFiles(paths)
})

const selectedIndices = ref<Set<number>>(new Set())

useKeyboard({
  onAddFiles: async () => {
    const { settings } = useSettings()
    const res = await openFilePicker(settings.value.last_input_dir)
    if (res.success && res.data && res.data.length > 0) {
      await addFiles(res.data)
    }
  },
  onRemoveSelected: () => {
    if (selectedIndices.value.size > 0) {
      removeFiles([...selectedIndices.value])
    }
  },
  onQuit: () => {
    window.close()
  },
})

onMounted(() => {
  fetchSettings()
  // Apply saved theme
  const { settings } = useSettings()
  document.documentElement.setAttribute('data-theme', settings.value.theme || 'light')
})
</script>

<template>
  <div class="flex flex-col h-screen bg-base-100">
    <!-- Navbar -->
    <header class="navbar bg-primary text-primary-content shadow-lg shrink-0">
      <div class="flex-1">
        <span class="text-xl font-bold">ComicManager Neo</span>
      </div>
      <div class="flex-none flex items-center gap-2">
        <button
          class="btn btn-ghost btn-sm btn-circle"
          title="Toggle theme"
          @click="toggleTheme"
        >
          {{ currentTheme === 'light' ? '&#9790;' : '&#9788;' }}
        </button>
        <button
          class="btn btn-ghost btn-sm btn-circle"
          title="Settings"
          @click="settingsOpen = true"
        >
          &#9881;
        </button>
        <span class="text-sm opacity-80">v1.0.0</span>
      </div>
    </header>

    <!-- Main content -->
    <main class="flex-1 min-h-0 flex flex-col p-2 gap-2">
      <!-- Toolbar -->
      <Toolbar />

      <!-- Stats bar -->
      <StatsBar />

      <!-- File list -->
      <div class="flex-1 min-h-0 border border-base-300 rounded-lg overflow-hidden flex flex-col">
        <FileList @fill-filename="name => outputSettingsRef?.outputFilename !== undefined && (outputSettingsRef.outputFilename = name)" />
      </div>

      <!-- Bottom panel -->
      <div class="shrink-0 flex flex-col gap-2">
        <OutputSettings ref="outputSettingsRef" />
        <MergeControls
          :output-filename="outputSettingsRef?.outputFilename ?? 'merged'"
          :output-dir="outputSettingsRef?.outputDir ?? ''"
          :preserve-metadata="outputSettingsRef?.preserveMetadata ?? true"
        />
      </div>
    </main>

    <!-- Overlays -->
    <FileDropZone />
    <ToastContainer />
    <SettingsModal :open="settingsOpen" @close="settingsOpen = false" />
  </div>
</template>
