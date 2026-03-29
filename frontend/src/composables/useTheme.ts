/** Theme switching composable. */

import { ref, watch } from 'vue'
import { useSettings } from '../composables/useSettings'

const { settings, saveSettings } = useSettings()

const currentTheme = ref(settings.value.theme || 'light')

watch(currentTheme, (theme) => {
  document.documentElement.setAttribute('data-theme', theme)
  saveSettings({ theme })
})

function toggleTheme() {
  currentTheme.value = currentTheme.value === 'light' ? 'dark' : 'light'
}

function setTheme(theme: string) {
  currentTheme.value = theme
}

export function useTheme() {
  return { currentTheme, toggleTheme, setTheme }
}
