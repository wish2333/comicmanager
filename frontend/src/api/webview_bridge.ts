/** PyWebView JS bridge for native file/directory dialogs.

Uses window.pywebview.api to call Python methods directly,
bypassing HTTP-based Tkinter dialogs that fail on FastAPI's async loop.
*/

function getApi(): any {
  if (typeof window !== 'undefined' && (window as any).pywebview?.api) {
    return (window as any).pywebview.api
  }
  return null
}

/** Wait for pywebview API to be ready. */
export async function waitForPyWebView(timeout = 5000): Promise<boolean> {
  const start = Date.now()
  while (Date.now() - start < timeout) {
    if (getApi()) return true
    await new Promise((r) => setTimeout(r, 100))
  }
  return false
}

export interface BrowseFilesResult {
  success: boolean
  data: string[]
  error?: string
}

export interface BrowseDirectoryResult {
  success: boolean
  data: string | null
  error?: string
}

export async function openFilePicker(initialDir = ''): Promise<BrowseFilesResult> {
  const api = getApi()
  if (!api) {
    console.warn('pywebview API not available, falling back to HTTP')
    const { browseFiles } = await import('./browse')
    const res = await browseFiles(initialDir)
    return { success: res.success, data: res.data ?? [], error: res.error ?? undefined }
  }
  try {
    const result = await api.open_files(initialDir)
    return result
  } catch (e) {
    return { success: false, data: [], error: String(e) }
  }
}

export async function openDirectoryPicker(initialDir = ''): Promise<BrowseDirectoryResult> {
  const api = getApi()
  if (!api) {
    console.warn('pywebview API not available, falling back to HTTP')
    const { browseDirectory } = await import('./browse')
    const res = await browseDirectory(initialDir)
    return { success: res.success, data: res.data ?? null, error: res.error ?? undefined }
  }
  try {
    const result = await api.open_directory(initialDir)
    return result
  } catch (e) {
    return { success: false, data: null, error: String(e) }
  }
}
