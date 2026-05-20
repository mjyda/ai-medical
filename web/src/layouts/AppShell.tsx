import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  BookOpen,
  Film,
  LayoutDashboard,
  LogOut,
  MessageSquare,
  Network,
  Settings,
  Sparkles,
  ListTodo,
  User,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { useAuthStore } from '@/stores/authStore'
import { cn } from '@/lib/utils'

const nav = [
  { to: '/dashboard', key: 'nav.dashboard', icon: LayoutDashboard },
  { to: '/documents', key: 'nav.documents', icon: BookOpen },
  { to: '/videos', key: 'nav.videos', icon: Film },
  { to: '/chat', key: 'nav.chat', icon: MessageSquare },
  { to: '/generate', key: 'nav.generate', icon: Sparkles },
  { to: '/tasks', key: 'nav.tasks', icon: ListTodo },
  { to: '/graph', key: 'nav.graph', icon: Network },
  { to: '/settings', key: 'nav.settings', icon: Settings },
] as const

function LanguageSwitcher() {
  const { i18n } = useTranslation()
  return (
    <div className="flex items-center gap-1 text-xs">
      <Button variant={i18n.language === 'zh' ? 'secondary' : 'ghost'} size="sm" onClick={() => void i18n.changeLanguage('zh')}>
        中文
      </Button>
      <Button variant={i18n.language === 'en' ? 'secondary' : 'ghost'} size="sm" onClick={() => void i18n.changeLanguage('en')}>
        EN
      </Button>
    </div>
  )
}

export function AppShell() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)

  const displayName = user?.display_name ?? user?.username ?? 'U'
  const avatarSrc = user?.avatar_url ? `/api${user.avatar_url}` : undefined

  return (
    <div className="flex min-h-screen">
      <aside className="hidden w-56 shrink-0 border-r bg-card md:flex md:flex-col">
        <div className="p-4">
          <div className="text-sm font-semibold">{t('app.title')}</div>
          <p className="mt-1 text-xs text-muted-foreground">{t('app.subtitle')}</p>
        </div>
        <Separator />
        <nav className="flex flex-1 flex-col gap-0.5 p-2">
          {nav.map(({ to, key, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors hover:bg-muted',
                  isActive && 'bg-muted font-medium',
                )
              }
            >
              <Icon className="h-4 w-4 shrink-0" />
              {t(key)}
            </NavLink>
          ))}
        </nav>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 items-center justify-between border-b bg-card px-4">
          <span className="text-sm text-muted-foreground md:hidden">{t('app.title')}</span>
          <div className="ml-auto flex items-center gap-3">
            <LanguageSwitcher />
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="rounded-full">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src={avatarSrc} />
                    <AvatarFallback>{displayName.slice(0, 1).toUpperCase()}</AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuLabel>{displayName}</DropdownMenuLabel>
                <DropdownMenuLabel className="text-xs font-normal text-muted-foreground">{user?.email}</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => navigate('/settings')}>
                  <User className="h-4 w-4" />
                  {t('nav.settings')}
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={() => {
                    logout()
                    navigate('/login', { replace: true })
                  }}
                >
                  <LogOut className="h-4 w-4" />
                  {t('auth.logout')}
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>
        <main className="flex-1 overflow-auto p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
