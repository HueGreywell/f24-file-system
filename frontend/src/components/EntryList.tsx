import type { MouseEvent } from 'react'
import { deleteFile, deleteFolder } from '../api/filesystem'
import { getErrorMessage } from '../api/errors'
import { useToast } from '../hooks/useToast'
import { FileIcon, FolderIcon } from './icons'
import { EntryType } from '../types/entry'
import type { Entry } from '../types/entry'

interface EntryListProps {
  entries: Entry[]
  onOpen: (entry: Entry) => void
  onDeleted: () => void
}

function displayName(entry: Entry): string {
  if (entry.type !== EntryType.Folder || entry.name.endsWith('/')) return entry.name
  return `${entry.name}/`
}

export function EntryList({ entries, onOpen, onDeleted }: EntryListProps) {
  const toast = useToast()

  function handleDelete(e: MouseEvent, entry: Entry) {
    e.stopPropagation()
    const action = entry.type === EntryType.Folder ? deleteFolder(entry.id) : deleteFile(entry.id)
    action
      .then(onDeleted)
      .catch((err: unknown) => toast.error(getErrorMessage(err)))
  }

  if (entries.length === 0) {
    return (
      <ul>
        <li className="empty">Empty</li>
      </ul>
    )
  }

  return (
    <ul>
      {entries.map((entry) => (
        <li
          key={entry.id}
          className={entry.type === EntryType.Folder ? 'folder' : ''}
          tabIndex={0}
          onClick={() => onOpen(entry)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault()
              onOpen(entry)
            }
          }}
        >
          <span className="name">
            {entry.type === EntryType.Folder ? <FolderIcon /> : <FileIcon />}
            {displayName(entry)}
          </span>
          <button type="button" className="delete" onClick={(e) => handleDelete(e, entry)}>
            Delete
          </button>
        </li>
      ))}
    </ul>
  )
}
