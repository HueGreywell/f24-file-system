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

export function useFileSearch(query: string, folderId?: string): FileSearchState {
  const [results, setResults] = useState<SearchResult[]>([])
  const debouncedQuery = useDebouncedValue(query.trim(), 250)
  const toast = useToast()

  useEffect(() => {
    if (!debouncedQuery) return

    const controller = new AbortController()

    searchFiles(debouncedQuery, folderId, controller.signal)
      .then(setResults)
      .catch((err: unknown) => {
        if (controller.signal.aborted) return
        toast.error(getErrorMessage(err))
      })

    return () => controller.abort()
  }, [debouncedQuery, folderId, toast])

  return debouncedQuery ? { results, searched: true } : { results: [], searched: false }
}
