import { request } from './client'
import type { CreateEntryRequest, Entry, FolderContents, SearchResult } from '../types/entry'

export function getFolder(id: string | null, signal?: AbortSignal): Promise<FolderContents> {
  return request<FolderContents>(id ? `/folders/${id}` : '/folders', { signal })
}

export function createEntry(parentId: string, body: CreateEntryRequest): Promise<Entry> {
  return request<Entry>(`/folders/${parentId}/children`, {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export function deleteFolder(id: string): Promise<void> {
  return request<void>(`/folders/${id}`, { method: 'DELETE' })
}

export function deleteFile(id: string): Promise<void> {
  return request<void>(`/files/${id}`, { method: 'DELETE' })
}

export function searchFiles(
  query: string,
  folderId?: string,
  signal?: AbortSignal,
): Promise<SearchResult[]> {
  const params = new URLSearchParams({ query })
  if (folderId) params.set('folderId', folderId)
  return request<SearchResult[]>(`/files/search?${params}`, { signal })
}
