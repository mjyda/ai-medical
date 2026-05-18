import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuthStore } from '@/stores/authStore'

export function LoginPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const login = useAuthStore((s) => s.login)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  const onSubmit = (e: FormEvent) => {
    e.preventDefault()
    login(username, password)
    void navigate('/dashboard', { replace: true })
  }

  const skip = () => {
    login('dev', '')
    void navigate('/dashboard', { replace: true })
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <div className="grid w-full max-w-4xl gap-6 md:grid-cols-2">
        <Card className="hidden border-dashed md:block">
          <CardHeader>
            <CardTitle>Wireframe</CardTitle>
            <CardDescription>品牌 / 插画占位 · 灰度线稿</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex min-h-[200px] items-center justify-center rounded-md border border-dashed bg-muted/40 text-sm text-muted-foreground">
              左侧示意区
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>{t('auth.login')}</CardTitle>
            <CardDescription>Mock：任意账号密码即可</CardDescription>
          </CardHeader>
          <CardContent>
            <form className="space-y-4" onSubmit={onSubmit}>
              <div className="space-y-2">
                <Label htmlFor="u">{t('auth.username')}</Label>
                <Input id="u" value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="p">{t('auth.password')}</Label>
                <Input
                  id="p"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                />
              </div>
              <Button type="submit" className="w-full">
                {t('auth.login')}
              </Button>
            </form>
            <Button type="button" variant="outline" className="mt-3 w-full" onClick={skip}>
              {t('auth.skipDev')}
            </Button>
            <p className="mt-4 text-center text-sm text-muted-foreground">
              <Link to="/register" className="underline underline-offset-4">
                {t('auth.register')}
              </Link>
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
