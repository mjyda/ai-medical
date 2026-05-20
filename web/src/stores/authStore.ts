import { create } from 'zustand'
import { api } from '@/lib/api'

export type AuthUser = {
  id: string
  username: string
  email: string
  display_name?: string
  avatar_url?: string
  bio?: string
  preferences?: Record<string, unknown>
}

type AuthState = {
  token: string | null
  user: AuthUser | null
  loading: boolean
  error: string | null

  login: (username: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
  fetchProfile: () => Promise<void>
  updateProfile: (data: {
    display_name?: string
    bio?: string
    bio_null?: boolean
    preferences?: Record<string, unknown>
  }) => Promise<void>
  changePassword: (oldPassword: string, newPassword: string) => Promise<void>
  uploadAvatar: (file: File) => Promise<string | undefined>
  clearError: () => void
}

function readToken(): string | null {
  try {
    return localStorage.getItem('auth_token')
  } catch {
    return null
  }
}

const initialToken = readToken()

export const useAuthStore = create<AuthState>((set, get) => ({
  token: initialToken,
  user: null,
  loading: false,
  error: null,

  login: async (username, password) => {
    set({ loading: true, error: null })
    try {
      const res = await api.post('/auth/login', { username, password })
      const { token, user } = res.data as { token: string; user: AuthUser }
      try {
        localStorage.setItem('auth_token', token)
      } catch {
        /* ignore */
      }
      set({ token, user, loading: false })
    } catch (err: any) {
      const msg = err.response?.data?.detail || '登录失败'
      set({ loading: false, error: msg })
      throw err
    }
  },

  register: async (username, email, password) => {
    set({ loading: true, error: null })
    try {
      const res = await api.post('/auth/register', { username, email, password })
      const { user } = res.data as { user: AuthUser }
      set({ loading: false })
      // After registration, auto-login
      await get().login(username, password)
    } catch (err: any) {
      const msg = err.response?.data?.detail || '注册失败'
      set({ loading: false, error: msg })
      throw err
    }
  },

  logout: () => {
    try {
      localStorage.removeItem('auth_token')
    } catch {
      /* ignore */
    }
    set({ token: null, user: null, error: null })
  },

  fetchProfile: async () => {
    try {
      const res = await api.get('/auth/me')
      set({ user: (res.data as { user: AuthUser }).user })
    } catch {
      // Token invalid — clear
      try {
        localStorage.removeItem('auth_token')
      } catch {
        /* ignore */
      }
      set({ token: null, user: null })
    }
  },

  updateProfile: async (data) => {
    set({ loading: true, error: null })
    try {
      const res = await api.put('/profile', data)
      set({ user: (res.data as { user: AuthUser }).user, loading: false })
    } catch (err: any) {
      const msg = err.response?.data?.detail || '保存失败'
      set({ loading: false, error: msg })
      throw err
    }
  },

  changePassword: async (oldPassword, newPassword) => {
    set({ loading: true, error: null })
    try {
      await api.put('/profile/password', {
        old_password: oldPassword,
        new_password: newPassword,
      })
      set({ loading: false })
    } catch (err: any) {
      const msg = err.response?.data?.detail || '密码修改失败'
      set({ loading: false, error: msg })
      throw err
    }
  },

  uploadAvatar: async (file) => {
    set({ loading: true, error: null })
    try {
      const form = new FormData()
      form.append('file', file)
      const res = await api.post('/profile/avatar', form)
      const data = res.data as { user: AuthUser; avatar_url: string }
      set({ user: data.user, loading: false })
      return data.avatar_url
    } catch (err: any) {
      const msg = err.response?.data?.detail || '头像上传失败'
      set({ loading: false, error: msg })
      throw err
    }
  },

  clearError: () => set({ error: null }),
}))

// Hydrate user on app load if token exists
if (initialToken) {
  useAuthStore.getState().fetchProfile()
}
