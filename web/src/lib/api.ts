import axios from 'axios'

/** 预留：对接 FastAPI 时 baseURL 走 Vite proxy `/api` */
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE ?? '/api',
  timeout: 30_000,
})

api.interceptors.request.use((config) => {
  const t = typeof localStorage !== 'undefined' ? localStorage.getItem('auth_token') : null
  if (t) {
    config.headers.Authorization = `Bearer ${t}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      try {
        localStorage.removeItem('auth_token')
      } catch {
        /* ignore */
      }
      window.location.href = '/login'
    }
    return Promise.reject(err)
  },
)
