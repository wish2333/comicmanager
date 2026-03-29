<script setup lang="ts">
import { ref } from 'vue'
import { useSettings } from '../composables/useSettings'
import { useTheme } from '../composables/useTheme'

const { settings, saveSettings } = useSettings()
const { currentTheme, setTheme } = useTheme()

defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  close: []
}>()

const activeTab = ref<'general' | 'appearance'>('general')

const autoIncrement = ref(settings.value.auto_increment)
const preserveMetadata = ref(settings.value.preserve_metadata)
const theme = ref(currentTheme.value)

function handleSave() {
  saveSettings({
    auto_increment: autoIncrement.value,
    preserve_metadata: preserveMetadata.value,
  })
  setTheme(theme.value)
  emit('close')
}

function handleClose() {
  emit('close')
}
</script>

<template>
  <dialog :class="['modal', { 'modal-open': open }]">
    <div class="modal-box max-w-lg">
      <h3 class="font-bold text-lg">Settings</h3>

      <!-- Tabs -->
      <div role="tablist" class="tabs tabs-bordered mt-4">
        <a
          role="tab"
          class="tab"
          :class="{ 'tab-active': activeTab === 'general' }"
          @click="activeTab = 'general'"
        >
          General
        </a>
        <a
          role="tab"
          class="tab"
          :class="{ 'tab-active': activeTab === 'appearance' }"
          @click="activeTab = 'appearance'"
        >
          Appearance
        </a>
      </div>

      <div class="py-4">
        <!-- General tab -->
        <div v-if="activeTab === 'general'" class="flex flex-col gap-4">
          <label class="label cursor-pointer gap-2 justify-start">
            <input v-model="autoIncrement" type="checkbox" class="checkbox checkbox-sm checkbox-primary" />
            <span class="label-text">Auto-increment output filename on conflict</span>
          </label>

          <label class="label cursor-pointer gap-2 justify-start">
            <input v-model="preserveMetadata" type="checkbox" class="checkbox checkbox-sm checkbox-primary" />
            <span class="label-text">Include ComicInfo.xml metadata in output</span>
          </label>
        </div>

        <!-- Appearance tab -->
        <div v-if="activeTab === 'appearance'" class="flex flex-col gap-4">
          <div class="form-control">
            <label class="label">
              <span class="label-text">Theme</span>
            </label>
            <div class="flex gap-2">
              <button
                class="btn btn-sm"
                :class="{ 'btn-primary': theme === 'light' }"
                @click="theme = 'light'"
              >
                Light
              </button>
              <button
                class="btn btn-sm"
                :class="{ 'btn-primary': theme === 'dark' }"
                @click="theme = 'dark'"
              >
                Dark
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="modal-action">
        <button class="btn" @click="handleClose">Cancel</button>
        <button class="btn btn-primary" @click="handleSave">Save</button>
      </div>
    </div>
    <form method="dialog" class="modal-backdrop">
      <button @click="handleClose">close</button>
    </form>
  </dialog>
</template>
