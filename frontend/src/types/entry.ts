export const EntryType = {
  Folder: 'Folder',
  File: 'File',
} as const

export type EntryType = (typeof EntryType)[keyof typeof EntryType]

export interface Entry {
  id: string
  name: string
  type: EntryType
}

export interface FolderContents {
  id: string
  name: string
  parentId: string | null
  path: string
  children: Entry[]
}

export interface SearchResult {
  id: string
  name: string
  path: string
  parentId: string
}

export interface CreateEntryRequest {
  name: string
  type: EntryType
}
