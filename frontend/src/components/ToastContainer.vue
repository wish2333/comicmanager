<script setup lang="ts">
import { useToast } from '../composables/useToast'

const { toasts, removeToast } = useToast()

function alertClass(type: string): string {
  const map: Record<string, string> = {
    success: 'alert-success',
    error: 'alert-error',
    info: 'alert-info',
    warning: 'alert-warning',
  }
  return map[type] || 'alert-info'
}
</script>

<template>
  <div class="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
    <div
      v-for="toast in toasts"
      :key="toast.id"
      :class="['alert shadow-lg', alertClass(toast.type)]"
    >
      <span class="text-sm">{{ toast.message }}</span>
      <button class="btn btn-sm btn-ghost" @click="removeToast(toast.id)">
        X
      </button>
    </div>
  </div>
</template>
