import { create } from 'zustand'

export type AuthUser = { name: string; email: string }

type AuthState = {
  token: string | null
  user: AuthUser | null
  login: (username: string, _password?: string) => void
  logout: () => void
}

function readToken(): string | null {
  try {
    return localStorage.getItem('auth_token')
  } catch {
    return null
  }
}

function parseUserFromToken(token: string | null): AuthUser | null {
  if (!token || !token.startsWith('mock.')) return null
  const parts = token.split('.')
  if (parts.length < 2) return null
  try {
    const name = atob(parts[1])
    return { name, email: `${name}@example.com` }
  } catch {
    return null
  }
}

const initialToken = readToken()

export const useAuthStore = create<AuthState>((set) => ({
  token: initialToken,
  user: parseUserFromToken(initialToken),
  login: (username) => {
    const name = username.trim() || 'Guest'
    const token = `mock.${btoa(name)}.jwt`
    try {
      localStorage.setItem('auth_token', token)
    } catch {
      /* ignore */
    }
    set({
      token,
      user: { name, email: `${name}@example.com` },
    })
  },
  logout: () => {
    try {
      localStorage.removeItem('auth_token')
    } catch {
      /* ignore */
    }
    set({ token: null, user: null })
  },
}))
