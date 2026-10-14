import { useRef, useState } from 'react'
import type { FocusEvent, KeyboardEvent } from 'react'
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
  const [closed, setClosed] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const folderId = scope === 'folder' ? currentFolderId : undefined
  const { results, searched } = useFileSearch(query, folderId)
  const isOpen = searched && !closed

  function handleQueryChange(value: string) {
    setQuery(value)
    setClosed(false)
  }

  function handleSelect(result: SearchResult) {
    setQuery('')
    onSelect(result)
  }

  function handleKeyDown(e: KeyboardEvent<HTMLElement>) {
    if (e.key === 'Escape') setClosed(true)
  }

  function handleBlur(e: FocusEvent<HTMLDivElement>) {
    const nextFocus = e.relatedTarget as Node | null
    if (nextFocus && containerRef.current?.contains(nextFocus)) return
    setClosed(true)
  }

  return (
    <div className="search" ref={containerRef} onKeyDown={handleKeyDown} onBlur={handleBlur}>
      <div className="search-controls">
        <input
          value={query}
          onChange={(e) => handleQueryChange(e.target.value)}
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
      {isOpen && (
        <ul className="search-results" role="listbox">
          {results.length > 0 ? (
            results.map((result) => (
              <li
                key={result.id}
                role="option"
                aria-selected={false}
                tabIndex={0}
                onClick={() => handleSelect(result)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault()
                    handleSelect(result)
                  }
                }}
              >
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
