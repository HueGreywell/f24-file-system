import { useEffect, useState } from 'react'
import { searchFiles } from '../api/filesystem'
import { getErrorMessage } from '../api/errors'
import type { SearchResult } from '../types/entry'
import { useToast } from './useToast'
import { useDebouncedValue } from './useDebouncedValue'

interface FileSearchState {
  results: SearchResult[]
  searched: boolean
}

export function useFileSearch(query: string): FileSearchState {
  const [results, setResults] = useState<SearchResult[]>([])
  const debouncedQuery = useDebouncedValue(query.trim(), 250)
  const toast = useToast()

  useEffect(() => {
    if (!debouncedQuery) return

    searchFiles(debouncedQuery)
      .then(setResults)
      .catch((err: unknown) => {
        toast.error(getErrorMessage(err))
      })
  }, [debouncedQuery, toast])

  return debouncedQuery ? { results, searched: true } : { results: [], searched: false }
}
