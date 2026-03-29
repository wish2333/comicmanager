/** Settings API calls. */

import type { AppSettings } from '../types'
import { apiGet, apiPut } from './client'

export async function getSettings() {
  return apiGet<AppSettings>('/api/settings')
}

export async function updateSettings(settings: Partial<AppSettings>) {
  return apiPut<AppSettings>('/api/settings', settings)
}
