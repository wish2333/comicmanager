/** HTTP client wrapper with typed responses. */

import type { ApiResponse } from '../types'

const BASE = ''

export async function apiGet<T>(path: string): Promise<ApiResponse<T>> {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: res.statusText }))
    return { success: false, data: null, error: body.error || 'Request failed' }
  }
  const body = await res.json()
  return { success: true, data: body.data ?? body, error: null }
}

export async function apiPost<T>(path: string, body?: unknown): Promise<ApiResponse<T>> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body != null ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    const errBody = await res.json().catch(() => ({ error: res.statusText }))
    return { success: false, data: null, error: errBody.error || 'Request failed' }
  }
  const resBody = await res.json()
  return { success: true, data: resBody.data ?? resBody, error: null }
}

export async function apiPut<T>(path: string, body: unknown): Promise<ApiResponse<T>> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const errBody = await res.json().catch(() => ({ error: res.statusText }))
    return { success: false, data: null, error: errBody.error || 'Request failed' }
  }
  const resBody = await res.json()
  return { success: true, data: resBody.data ?? resBody, error: null }
}

export async function apiDelete<T>(path: string, body?: unknown): Promise<ApiResponse<T>> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: body != null ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    const errBody = await res.json().catch(() => ({ error: res.statusText }))
    return { success: false, data: null, error: errBody.error || 'Request failed' }
  }
  const resBody = await res.json()
  return { success: true, data: resBody.data ?? resBody, error: null }
}
