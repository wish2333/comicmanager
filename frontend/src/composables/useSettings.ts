/** Settings state management. */

import { ref } from 'vue'
import type { AppSettings } from '../types'
import { getSettings, updateSettings } from '../api/settings'

const settings = ref<AppSettings>({
  last_output_dir: '',
  last_input_dir: '',
  zip_image_formats: ['jpg', 'jpeg', 'png', 'webp'],
  theme: 'light',
  preserve_metadata: true,
  auto_increment: true,
})

const loaded = ref(false)

async function fetchSettings() {
  const res = await getSettings()
  if (res.success && res.data) {
    settings.value = { ...settings.value, ...res.data }
    loaded.value = true
  }
}

async function saveSettings(partial: Partial<AppSettings>) {
  const res = await updateSettings(partial)
  if (res.success && res.data) {
    settings.value = { ...settings.value, ...res.data }
  }
}

export function useSettings() {
  return {
    settings,
    loaded,
    fetchSettings,
    saveSettings,
  }
}
