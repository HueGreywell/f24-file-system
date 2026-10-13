import { useState } from 'react'
import type { FormEvent } from 'react'
import { createEntry } from '../api/filesystem'
import { getErrorMessage } from '../api/errors'
import { EntryType } from '../types/entry'
import { useToast } from '../hooks/useToast'

interface NewEntryFormProps {
  parentId: string
  onCreated: () => void
}

export function NewEntryForm({ parentId, onCreated }: NewEntryFormProps) {
  const [name, setName] = useState('')
  const [type, setType] = useState<EntryType>(EntryType.Folder)
  const toast = useToast()

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const trimmed = name.trim()
    if (!trimmed) return

    createEntry(parentId, { name: trimmed, type })
      .then(() => {
        setName('')
        onCreated()
      })
      .catch((err: unknown) => toast.error(getErrorMessage(err)))
  }

  return (
    <form className="new-entry" onSubmit={handleSubmit}>
      <select value={type} onChange={(e) => setType(e.target.value as EntryType)}>
        <option value={EntryType.Folder}>Folder</option>
        <option value={EntryType.File}>File</option>
      </select>
      <input value={name} onChange={(e) => setName(e.target.value)} placeholder="name" />
      <button type="submit" className="primary">
        Add
      </button>
    </form>
  )
}
