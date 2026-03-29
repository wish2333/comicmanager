<script setup lang="ts">
import { useFileDrop } from '../composables/useFileDrop'

// Only read the reactive isDragging state; event listeners are registered
// by App.vue which is always mounted
const { isDragging } = useFileDrop()
</script>

<template>
  <div
    v-if="isDragging"
    class="fixed inset-0 z-50 flex items-center justify-center bg-primary/10 border-4 border-dashed border-primary"
  >
    <div class="text-center p-8">
      <p class="text-2xl font-bold text-primary">Drop comic files here</p>
      <p class="text-base-content/60 mt-2">CBZ / ZIP</p>
    </div>
  </div>
</template>
