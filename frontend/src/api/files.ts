/** File queue API calls. */

import type { QueuedFile } from '../types'
import { apiPost, apiGet, apiDelete, apiPut } from './client'

export async function addFiles(paths: string[]) {
  return apiPost<QueuedFile[]>('/api/files', { paths })
}

export async function getFiles() {
  return apiGet<QueuedFile[]>('/api/files')
}

export async function removeFiles(indices: number[]) {
  return apiDelete<QueuedFile[]>('/api/files', { indices })
}

export async function reorderFiles(fromIndex: number, toIndex: number) {
  return apiPut<QueuedFile[]>('/api/files/reorder', { from_index: fromIndex, to_index: toIndex })
}

export async function clearFiles() {
  return apiPost<QueuedFile[]>('/api/files/clear')
}

export async function validateFiles() {
  return apiPost<{ valid_count: number; invalid_count: number; files: QueuedFile[] }>('/api/files/validate')
}

export async function sortFiles(key: string = 'name', reverse: boolean = false) {
  return apiPost<QueuedFile[]>('/api/files/sort', { key, reverse })
}
