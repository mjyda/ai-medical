import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export function RegisterPage() {
  const { t } = useTranslation()

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>{t('auth.register')}</CardTitle>
          <CardDescription>Mock · 不落库</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="e">Email</Label>
            <Input id="e" type="email" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="u2">{t('auth.username')}</Label>
            <Input id="u2" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="p2">{t('auth.password')}</Label>
            <Input id="p2" type="password" />
          </div>
          <Button className="w-full" type="button">
            {t('auth.register')}
          </Button>
          <p className="text-center text-sm text-muted-foreground">
            <Link to="/login" className="underline underline-offset-4">
              {t('auth.login')}
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
