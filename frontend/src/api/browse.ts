/** Browse API calls (OS file/directory dialogs). */

import { apiPost } from './client'

export async function browseFiles(initialDir = '') {
  return apiPost<string[]>('/api/browse/files', { initial_dir: initialDir })
}

export async function browseDirectory(initialDir = '') {
  return apiPost<string | null>('/api/browse/directory', { initial_dir: initialDir })
}
