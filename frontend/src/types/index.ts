/** Shared TypeScript type definitions */

export interface QueuedFile {
  path: string
  name: string
  type: 'CBZ' | 'ZIP'
  size: number
  page_count: number
  valid: boolean
  error: string | null
}

export interface MergeRequest {
  output_filename: string
  output_dir: string
  preserve_metadata: boolean
  zip_formats: string[]
}

export interface MergeProgressEvent {
  task_id: string
  stage: 'validating' | 'extracting' | 'merging' | 'writing' | 'done' | 'error'
  current_file: string | null
  current_index: number
  total_files: number
  current_page: number
  total_pages: number
  message: string
}

export interface MergeResult {
  success: boolean
  output_path: string | null
  total_pages: number
  merged_files: MergedFileInfo[]
  errors: string[]
}

export interface MergedFileInfo {
  path: string
  name: string
  type: 'CBZ' | 'ZIP'
  pages: number
}

export interface AppSettings {
  last_output_dir: string
  last_input_dir: string
  zip_image_formats: string[]
  theme: string
  preserve_metadata: boolean
  auto_increment: boolean
}

export interface ApiResponse<T> {
  success: boolean
  data: T | null
  error: string | null
}

export interface ReorderRequest {
  from_index: number
  to_index: number
}

export interface RemoveRequest {
  indices: number[]
}
