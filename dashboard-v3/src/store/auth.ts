import { create } from 'zustand'
import { apiFetch, ApiError } from '@/lib/api'

export interface User {
  id: string
  email: string
  name: string
  role: string
}

interface AuthState {
  user: User | null
  status: 'checking' | 'authenticated' | 'unauthenticated'
  error: string | null
  checkAuth: () => Promise<void>
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

export const useAuth = create<AuthState>((set) => ({
  user: null,
  status: 'checking',
  error: null,

  checkAuth: async () => {
    try {
      const user = await apiFetch<User>('/auth/me')
      set({ user, status: 'authenticated', error: null })
    } catch {
      set({ user: null, status: 'unauthenticated' })
    }
  },

  login: async (email: string, password: string) => {
    set({ error: null })
    try {
      const res = await apiFetch<{ user: User }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      set({ user: res.user, status: 'authenticated', error: null })
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : 'Login failed'
      set({ error: msg, status: 'unauthenticated' })
      throw e
    }
  },

  logout: async () => {
    try {
      await apiFetch('/auth/logout', { method: 'POST' })
    } finally {
      set({ user: null, status: 'unauthenticated' })
    }
  },
}))
