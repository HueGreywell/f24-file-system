import { useCallback, useEffect, useRef, useState } from 'react'
import { getFolder } from '../api/filesystem'
import { getErrorMessage } from '../api/errors'
import type { FolderContents } from '../types/entry'
import { useToast } from './useToast'

interface UseFolderResult {
  folder: FolderContents | null
  error: string | null
  reload: () => void
}

export function useFolder(id: string): UseFolderResult {
  const [folder, setFolder] = useState<FolderContents | null>(null)
  const [error, setError] = useState<string | null>(null)
  const hasLoadedRef = useRef(false)
  const toast = useToast()

  const load = useCallback(() => {
    getFolder(id)
      .then((data) => {
        hasLoadedRef.current = true
        setFolder(data)
        setError(null)
      })
      .catch((err: unknown) => {
        const message = getErrorMessage(err)
        if (hasLoadedRef.current) {
          toast.error(message)
        } else {
          setError(message)
        }
      })
  }, [id, toast])

  useEffect(() => {
    load()
  }, [load])

  return { folder, error, reload: load }
}
