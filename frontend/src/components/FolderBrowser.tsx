import { useState } from 'react'
import { useFolder } from '../hooks/useFolder'
import { ErrorWidget } from './ErrorWidget'
import { EntryList } from './EntryList'
import { NewEntryForm } from './NewEntryForm'
import { SearchBox } from './SearchBox'
import { EntryType } from '../types/entry'
import type { Entry, SearchResult } from '../types/entry'

export function FolderBrowser() {
  const [currentId, setCurrentId] = useState<string>('')
  const { folder, error, reload } = useFolder(currentId)

  function handleOpen(entry: Entry) {
    if (entry.type === EntryType.Folder) setCurrentId(entry.id)
  }

  function handleSearchSelect(result: SearchResult) {
    setCurrentId(result.parentId)
  }

  if (error) {
    return <ErrorWidget message={error} onRetry={reload} />
  }

  const parentId = folder?.parentId

  return (
    <>
      <SearchBox onSelect={handleSearchSelect} />

      <p className="path">{folder?.path ?? '…'}</p>

      {parentId && (
        <button type="button" className="up" onClick={() => setCurrentId(parentId)}>
          &uarr; Up
        </button>
      )}

      <EntryList entries={folder?.children ?? []} onOpen={handleOpen} onDeleted={reload} />

      {folder && <NewEntryForm parentId={folder.id} onCreated={reload} />}
    </>
  )
}
