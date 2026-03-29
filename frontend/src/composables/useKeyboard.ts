/** Keyboard shortcuts composable. */

import { onMounted, onUnmounted } from 'vue'

interface ShortcutHandlers {
  onAddFiles?: () => void
  onClear?: () => void
  onRemoveSelected?: () => void
  onQuit?: () => void
}

export function useKeyboard(handlers: ShortcutHandlers) {
  function onKeyDown(e: KeyboardEvent) {
    // Ignore if user is typing in an input
    const target = e.target as HTMLElement
    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
      return
    }

    if (e.ctrlKey && e.key === 'o') {
      e.preventDefault()
      handlers.onAddFiles?.()
    } else if (e.key === 'Delete') {
      e.preventDefault()
      handlers.onRemoveSelected?.()
    } else if (e.ctrlKey && e.key === 'q') {
      e.preventDefault()
      handlers.onQuit?.()
    }
  }

  onMounted(() => {
    window.addEventListener('keydown', onKeyDown)
  })

  onUnmounted(() => {
    window.removeEventListener('keydown', onKeyDown)
  })
}
