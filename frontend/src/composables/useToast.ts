/** Toast notification composable. */

import { ref } from 'vue'

interface Toast {
  id: number
  type: 'success' | 'error' | 'info' | 'warning'
  message: string
  dismissAfter: number
}

const toasts = ref<Toast[]>([])
let nextId = 0

function addToast(type: Toast['type'], message: string, dismissAfter = 3000) {
  const id = nextId++
  toasts.value = [...toasts.value, { id, type, message, dismissAfter }]

  if (dismissAfter > 0) {
    setTimeout(() => {
      removeToast(id)
    }, dismissAfter)
  }
}

function removeToast(id: number) {
  toasts.value = toasts.value.filter((t) => t.id !== id)
}

function success(message: string) { addToast('success', message) }
function error(message: string) { addToast('error', message, 5000) }
function info(message: string) { addToast('info', message) }
function warning(message: string) { addToast('warning', message) }

export function useToast() {
  return { toasts, success, error, info, warning, removeToast }
}
