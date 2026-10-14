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
  const controllerRef = useRef<AbortController | null>(null)
  const toast = useToast()

  const load = useCallback(() => {
    controllerRef.current?.abort()
    const controller = new AbortController()
    controllerRef.current = controller

    getFolder(id, controller.signal)
      .then((data) => {
        hasLoadedRef.current = true
        setFolder(data)
        setError(null)
      })
      .catch((err: unknown) => {
        if (controller.signal.aborted) return
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
    return () => controllerRef.current?.abort()
  }, [load])

  return { folder, error, reload: load }
}
