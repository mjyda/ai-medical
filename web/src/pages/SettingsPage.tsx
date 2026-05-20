import { useState, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import { Camera, Loader2 } from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'

function ProfileTab() {
  const { t } = useTranslation()
  const user = useAuthStore((s) => s.user)
  const updateProfile = useAuthStore((s) => s.updateProfile)
  const uploadAvatar = useAuthStore((s) => s.uploadAvatar)
  const loading = useAuthStore((s) => s.loading)

  const [displayName, setDisplayName] = useState(user?.display_name ?? user?.username ?? '')
  const [bio, setBio] = useState(user?.bio ?? '')
  const [status, setStatus] = useState<'idle' | 'saved' | 'error'>('idle')
  const [avatarUploading, setAvatarUploading] = useState(false)
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const handleSave = async () => {
    try {
      await updateProfile({ display_name: displayName, bio: bio || undefined })
      setStatus('saved')
      setTimeout(() => setStatus('idle'), 2500)
    } catch {
      setStatus('error')
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (!f) return
    setSelectedFile(f)
    setAvatarPreview(URL.createObjectURL(f))
  }

  const handleUploadAvatar = async () => {
    if (!selectedFile) return
    setAvatarUploading(true)
    try {
      await uploadAvatar(selectedFile)
      setDialogOpen(false)
      setSelectedFile(null)
      setAvatarPreview(null)
    } catch {
      /* error shown by store */
    } finally {
      setAvatarUploading(false)
    }
  }

  const avatarSrc = user?.avatar_url ? `/api${user.avatar_url}` : undefined

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>{t('settings.tabs.profile')}</CardTitle>
          <CardDescription>
            {status === 'saved' ? t('settings.profile.savedSuccess') : ''}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center gap-4">
            <Avatar className="h-20 w-20">
              <AvatarImage src={avatarSrc} />
              <AvatarFallback className="text-2xl">
                {(user?.display_name ?? user?.username ?? 'U').slice(0, 1).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
              <DialogTrigger asChild>
                <Button variant="outline" size="sm">
                  <Camera className="mr-2 h-4 w-4" />
                  {t('settings.profile.uploadAvatar')}
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>{t('settings.profile.uploadAvatar')}</DialogTitle>
                  <DialogDescription>
                    支持 JPG、PNG、WebP 格式，最大 2 MB
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <Input
                    ref={fileRef}
                    type="file"
                    accept=".jpg,.jpeg,.png,.webp"
                    onChange={handleFileChange}
                  />
                  {avatarPreview && (
                    <div className="flex justify-center">
                      <Avatar className="h-32 w-32">
                        <AvatarImage src={avatarPreview} />
                      </Avatar>
                    </div>
                  )}
                  <Button
                    onClick={handleUploadAvatar}
                    disabled={!selectedFile || avatarUploading}
                    className="w-full"
                  >
                    {avatarUploading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    {avatarUploading
                      ? t('settings.profile.saving')
                      : t('settings.profile.uploadAvatar')}
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>

          <Separator />

          <div className="space-y-2">
            <Label htmlFor="displayName">{t('settings.profile.displayName')}</Label>
            <Input
              id="displayName"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">{t('settings.profile.email')}</Label>
            <Input id="email" value={user?.email ?? ''} disabled />
          </div>

          <div className="space-y-2">
            <Label htmlFor="bio">{t('settings.profile.bio')}</Label>
            <Textarea
              id="bio"
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              placeholder={t('settings.profile.bioPlaceholder')}
              rows={3}
            />
          </div>

          <Button onClick={handleSave} disabled={loading}>
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {loading ? t('settings.profile.saving') : t('settings.profile.save')}
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}

function SecurityTab() {
  const { t } = useTranslation()
  const changePassword = useAuthStore((s) => s.changePassword)
  const loading = useAuthStore((s) => s.loading)

  const [oldPw, setOldPw] = useState('')
  const [newPw, setNewPw] = useState('')
  const [confirmPw, setConfirmPw] = useState('')
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const [msg, setMsg] = useState('')

  const handleSubmit = async () => {
    if (newPw !== confirmPw) {
      setStatus('error')
      setMsg(t('settings.security.passwordMismatch'))
      return
    }
    try {
      await changePassword(oldPw, newPw)
      setStatus('success')
      setMsg(t('settings.security.passwordChanged'))
      setOldPw('')
      setNewPw('')
      setConfirmPw('')
    } catch (err: any) {
      setStatus('error')
      setMsg(err.response?.data?.detail || t('settings.security.passwordError'))
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>{t('settings.security.changePassword')}</CardTitle>
          <CardDescription>
            {status === 'success' ? msg : status === 'error' ? msg : ''}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="oldPw">{t('settings.security.oldPassword')}</Label>
            <Input
              id="oldPw"
              type="password"
              value={oldPw}
              onChange={(e) => setOldPw(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="newPw">{t('settings.security.newPassword')}</Label>
            <Input
              id="newPw"
              type="password"
              value={newPw}
              onChange={(e) => setNewPw(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="confirmPw">{t('settings.security.confirmNewPassword')}</Label>
            <Input
              id="confirmPw"
              type="password"
              value={confirmPw}
              onChange={(e) => setConfirmPw(e.target.value)}
            />
          </div>
          <Button
            onClick={handleSubmit}
            disabled={loading || !oldPw || !newPw || !confirmPw}
          >
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {loading
              ? t('settings.security.changing')
              : t('settings.security.changeButton')}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t('settings.security.sessionInfo')}</CardTitle>
          <CardDescription>{t('settings.security.sessionNote')}</CardDescription>
        </CardHeader>
      </Card>
    </div>
  )
}

function NotificationsTab() {
  const { t } = useTranslation()
  const user = useAuthStore((s) => s.user)
  const updateProfile = useAuthStore((s) => s.updateProfile)
  const loading = useAuthStore((s) => s.loading)

  const prefs = (user?.preferences ?? {}) as Record<string, boolean>

  const [emailNotify, setEmailNotify] = useState(prefs.email_notify ?? true)
  const [inAppNotify, setInAppNotify] = useState(prefs.in_app_notify ?? true)
  const [docAlert, setDocAlert] = useState(prefs.doc_alert ?? true)
  const [videoAlert, setVideoAlert] = useState(prefs.video_alert ?? true)

  const handleSave = async () => {
    await updateProfile({
      preferences: {
        ...prefs,
        email_notify: emailNotify,
        in_app_notify: inAppNotify,
        doc_alert: docAlert,
        video_alert: videoAlert,
      },
    })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('settings.tabs.notifications')}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <label className="flex items-start gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={emailNotify}
            onChange={(e) => setEmailNotify(e.target.checked)}
            className="mt-0.5 h-4 w-4 accent-primary"
          />
          <div>
            <p className="text-sm font-medium">
              {t('settings.notifications.emailNotify')}
            </p>
            <p className="text-xs text-muted-foreground">
              {t('settings.notifications.emailNotifyDesc')}
            </p>
          </div>
        </label>
        <Separator />
        <label className="flex items-start gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={inAppNotify}
            onChange={(e) => setInAppNotify(e.target.checked)}
            className="mt-0.5 h-4 w-4 accent-primary"
          />
          <div>
            <p className="text-sm font-medium">
              {t('settings.notifications.inAppNotify')}
            </p>
            <p className="text-xs text-muted-foreground">
              {t('settings.notifications.inAppNotifyDesc')}
            </p>
          </div>
        </label>
        <Separator />
        <label className="flex items-start gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={docAlert}
            onChange={(e) => setDocAlert(e.target.checked)}
            className="mt-0.5 h-4 w-4 accent-primary"
          />
          <div>
            <p className="text-sm font-medium">
              {t('settings.notifications.docProcessAlert')}
            </p>
            <p className="text-xs text-muted-foreground">
              {t('settings.notifications.docProcessAlertDesc')}
            </p>
          </div>
        </label>
        <Separator />
        <label className="flex items-start gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={videoAlert}
            onChange={(e) => setVideoAlert(e.target.checked)}
            className="mt-0.5 h-4 w-4 accent-primary"
          />
          <div>
            <p className="text-sm font-medium">
              {t('settings.notifications.videoAnalysisAlert')}
            </p>
            <p className="text-xs text-muted-foreground">
              {t('settings.notifications.videoAnalysisAlertDesc')}
            </p>
          </div>
        </label>
        <Button onClick={handleSave} disabled={loading}>
          {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {loading ? t('settings.profile.saving') : t('settings.profile.save')}
        </Button>
      </CardContent>
    </Card>
  )
}

function ApiTab() {
  const { t } = useTranslation()

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('settings.tabs.api')}</CardTitle>
        <CardDescription>{t('settings.api.comingSoonDesc')}</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">{t('settings.api.comingSoon')}</p>
      </CardContent>
    </Card>
  )
}

export function SettingsPage() {
  const { t } = useTranslation()

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">{t('settings.title')}</h1>
        <p className="text-sm text-muted-foreground">{t('settings.desc')}</p>
      </div>

      <Tabs defaultValue="profile">
        <TabsList className="w-full">
          <TabsTrigger value="profile" className="flex-1">
            {t('settings.tabs.profile')}
          </TabsTrigger>
          <TabsTrigger value="security" className="flex-1">
            {t('settings.tabs.security')}
          </TabsTrigger>
          <TabsTrigger value="notifications" className="flex-1">
            {t('settings.tabs.notifications')}
          </TabsTrigger>
          <TabsTrigger value="api" className="flex-1">
            {t('settings.tabs.api')}
          </TabsTrigger>
        </TabsList>
        <TabsContent value="profile" className="mt-6">
          <ProfileTab />
        </TabsContent>
        <TabsContent value="security" className="mt-6">
          <SecurityTab />
        </TabsContent>
        <TabsContent value="notifications" className="mt-6">
          <NotificationsTab />
        </TabsContent>
        <TabsContent value="api" className="mt-6">
          <ApiTab />
        </TabsContent>
      </Tabs>
    </div>
  )
}
