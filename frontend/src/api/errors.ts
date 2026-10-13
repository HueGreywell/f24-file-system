import { ApiError } from './client'

const ERROR_MESSAGES: Record<string, string> = {
  INVALID_NAME: 'That name is not valid.',
  NOT_FOUND: 'This item no longer exists.',
  CANNOT_DELETE_ROOT: "You can't delete the root folder.",
  DUPLICATE_NAME: 'An item with this name already exists here.',
  VALIDATION_ERROR: 'Invalid request.',
  INTERNAL_ERROR: 'Something went wrong. Please try again.',
}

const FALLBACK_MESSAGE = 'Something went wrong. Please try again.'

export function getErrorMessage(err: unknown): string {
  if (err instanceof ApiError && err.code) {
    return ERROR_MESSAGES[err.code] ?? FALLBACK_MESSAGE
  }
  return FALLBACK_MESSAGE
}
