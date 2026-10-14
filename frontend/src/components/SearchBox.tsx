import { useState } from 'react'
import { useFileSearch } from '../hooks/useFileSearch'
import { FileIcon } from './icons'
import type { SearchResult } from '../types/entry'

interface SearchBoxProps {
  currentFolderId?: string
  onSelect: (result: SearchResult) => void
}

export function SearchBox({ currentFolderId, onSelect }: SearchBoxProps) {
  const [query, setQuery] = useState('')
  const [scope, setScope] = useState<'global' | 'folder'>('global')
  const folderId = scope === 'folder' ? currentFolderId : undefined
  const { results, searched } = useFileSearch(query, folderId)

  function handleSelect(result: SearchResult) {
    setQuery('')
    onSelect(result)
  }

  return (
    <div className="search">
      <div className="search-controls">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={
            scope === 'folder' ? 'Exact name in this folder…' : 'Starts with, searches everywhere…'
          }
        />
        <div className="search-scope" role="radiogroup" aria-label="Search scope">
          <button
            type="button"
            role="radio"
            aria-checked={scope === 'global'}
            className={scope === 'global' ? 'active' : ''}
            onClick={() => setScope('global')}
          >
            Everywhere
          </button>
          <button
            type="button"
            role="radio"
            aria-checked={scope === 'folder'}
            className={scope === 'folder' ? 'active' : ''}
            disabled={!currentFolderId}
            onClick={() => setScope('folder')}
          >
            This folder only
          </button>
        </div>
      </div>
      {searched && (
        <ul className="search-results">
          {results.length > 0 ? (
            results.map((result) => (
              <li key={result.id} onClick={() => handleSelect(result)}>
                <span className="name">
                  <FileIcon />
                  {result.name}
                </span>
                <span className="result-path">{result.path}</span>
              </li>
            ))
          ) : (
            <li className="search-empty">No files found.</li>
          )}
        </ul>
      )}
    </div>
  )
}
