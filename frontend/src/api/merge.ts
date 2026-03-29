/** Merge API calls including SSE progress parsing. */

import type { MergeProgressEvent, MergeResult } from '../types'

export interface MergeStartResult {
  taskId: string
}

export async function startMerge(request: {
  output_filename: string
  output_dir: string
  preserve_metadata: boolean
  zip_formats: string[]
}): Promise<Response> {
  return fetch('/api/merge', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })
}

export function parseSSEStream(
  response: Response,
  onProgress: (event: MergeProgressEvent) => void,
  onResult: (result: MergeResult) => void,
  onError: (error: string) => void,
): void {
  const reader = response.body?.getReader()
  if (!reader) {
    onError('No response stream')
    return
  }

  const decoder = new TextDecoder()
  let buffer = ''

  function processLine(line: string) {
    if (line.startsWith('data: ')) {
      const data = line.slice(6).trim()
      if (!data) return

      try {
        const parsed = JSON.parse(data)

        // Check if it's a progress event (has 'stage' field)
        if ('stage' in parsed) {
          onProgress(parsed as MergeProgressEvent)
        }

        // Check if it's a result (has 'success' and 'output_path' fields)
        if ('success' in parsed && 'merged_files' in parsed) {
          onResult(parsed as MergeResult)
        }
      } catch {
        // Ignore non-JSON lines
      }
    }
  }

  async function read() {
    while (true) {
      const { done, value } = await reader!.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        processLine(line)
      }
    }

    // Process remaining buffer
    if (buffer.trim()) {
      processLine(buffer)
    }
  }

  read().catch((err) => onError(String(err)))
}
