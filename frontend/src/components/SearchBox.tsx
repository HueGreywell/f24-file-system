import { useState } from 'react'
import { useFileSearch } from '../hooks/useFileSearch'
import { FileIcon } from './icons'
import type { SearchResult } from '../types/entry'

interface SearchBoxProps {
  onSelect: (result: SearchResult) => void
}

export function SearchBox({ onSelect }: SearchBoxProps) {
  const [query, setQuery] = useState('')
  const { results, searched } = useFileSearch(query)

  function handleSelect(result: SearchResult) {
    setQuery('')
    onSelect(result)
  }

  return (
    <div className="search">
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search files…"
      />
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
