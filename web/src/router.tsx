import { Navigate, Outlet, createBrowserRouter } from 'react-router-dom'
import { AppShell } from '@/layouts/AppShell'
import { LoginPage } from '@/pages/LoginPage'
import { RegisterPage } from '@/pages/RegisterPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { DocumentsPage } from '@/pages/DocumentsPage'
import { DocumentDetailPage } from '@/pages/DocumentDetailPage'
import { VideosPage } from '@/pages/VideosPage'
import { VideoDetailPage } from '@/pages/VideoDetailPage'
import { ChatPage } from '@/pages/ChatPage'
import { GeneratePage } from '@/pages/GeneratePage'
import { TasksPage } from '@/pages/TasksPage'
import { GraphPage } from '@/pages/GraphPage'
import { SettingsPage } from '@/pages/SettingsPage'
import { useAuthStore } from '@/stores/authStore'

function RequireAuth() {
  const token = useAuthStore((s) => s.token)
  if (!token) {
    return <Navigate to="/login" replace />
  }
  return <Outlet />
}

export const router = createBrowserRouter([
  { path: '/login', element: <LoginPage /> },
  { path: '/register', element: <RegisterPage /> },
  {
    element: <RequireAuth />,
    children: [
      {
        path: '/',
        element: <AppShell />,
        children: [
          { index: true, element: <Navigate to="/dashboard" replace /> },
          { path: 'dashboard', element: <DashboardPage /> },
          { path: 'documents', element: <DocumentsPage /> },
          { path: 'documents/:id', element: <DocumentDetailPage /> },
          { path: 'videos', element: <VideosPage /> },
          { path: 'videos/:id', element: <VideoDetailPage /> },
          { path: 'chat', element: <ChatPage /> },
          { path: 'generate', element: <GeneratePage /> },
          { path: 'tasks', element: <TasksPage /> },
          { path: 'graph', element: <GraphPage /> },
          { path: 'settings', element: <SettingsPage /> },
        ],
      },
    ],
  },
])
