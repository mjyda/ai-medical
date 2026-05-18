import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { useAuthStore } from '@/stores/authStore'

export function SettingsPage() {
  const { t } = useTranslation()
  const user = useAuthStore((s) => s.user)

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">{t('nav.settings')}</h1>
        <p className="text-sm text-muted-foreground">Mock 表单</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>个人资料</CardTitle>
          <CardDescription>保存不落库</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>显示名</Label>
            <Input defaultValue={user?.name ?? ''} />
          </div>
          <div className="space-y-2">
            <Label>邮箱</Label>
            <Input defaultValue={user?.email ?? ''} type="email" />
          </div>
          <Separator />
          <Button type="button">保存（Mock）</Button>
        </CardContent>
      </Card>
    </div>
  )
}
