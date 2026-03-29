<script setup lang="ts">
import { computed } from 'vue'
import { useSettings } from '../composables/useSettings'

const ALL_FORMATS = ['jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp']

const { settings, saveSettings } = useSettings()

const selectedFormats = computed({
  get: () => new Set(settings.value.zip_image_formats),
  set: (val: Set<string>) => {
    saveSettings({ zip_image_formats: [...val] })
  },
})

function toggleFormat(fmt: string) {
  const newSet = new Set(selectedFormats.value)
  if (newSet.has(fmt)) {
    newSet.delete(fmt)
  } else {
    newSet.add(fmt)
  }
  selectedFormats.value = newSet
}

function selectAll() {
  selectedFormats.value = new Set(ALL_FORMATS)
}

function selectNone() {
  selectedFormats.value = new Set()
}

function selectCommon() {
  selectedFormats.value = new Set(['jpg', 'jpeg', 'png', 'webp'])
}
</script>

<template>
  <div class="flex flex-col gap-2">
    <div class="flex items-center gap-2 flex-wrap">
      <label
        v-for="fmt in ALL_FORMATS"
        :key="fmt"
        class="label cursor-pointer gap-1"
      >
        <input
          type="checkbox"
          :checked="selectedFormats.has(fmt)"
          class="checkbox checkbox-xs checkbox-primary"
          @change="toggleFormat(fmt)"
        />
        <span class="label-text text-sm uppercase">{{ fmt }}</span>
      </label>
    </div>

    <div class="flex gap-2">
      <button class="btn btn-xs btn-ghost" @click="selectAll">All</button>
      <button class="btn btn-xs btn-ghost" @click="selectCommon">Common</button>
      <button class="btn btn-xs btn-ghost" @click="selectNone">None</button>
    </div>
  </div>
</template>
