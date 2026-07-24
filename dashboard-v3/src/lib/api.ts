// Cookie-session based API client. No token storage in JS — the browser
// handles the HttpOnly mbio_session cookie automatically via credentials: 'include'.

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

export async function apiFetch<T = unknown>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`/api/dashboard${path}`, {
    ...options,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  })

  if (!res.ok) {
    let detail = `Request failed (${res.status})`
    try {
      const body = await res.json()
      detail = body.detail || detail
    } catch {
      // response wasn't JSON — keep generic message
    }
    throw new ApiError(res.status, detail)
  }

  // 204 / empty body responses
  const text = await res.text()
  return (text ? JSON.parse(text) : null) as T
}

export async function aiosTelemetry<T = unknown>(): Promise<T> {
  const res = await fetch("/api/aios/telemetry", {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  })

  if (!res.ok) {
    throw new ApiError(res.status, "AIOS telemetry request failed")
  }

  return await res.json() as T
}

