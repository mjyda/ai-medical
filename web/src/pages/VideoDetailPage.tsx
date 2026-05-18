import { Link, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import ReactPlayer from 'react-player'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { mockVideos } from '@/mocks/data'

/** 公开示例视频，便于演示 react-player（可替换为自有媒资） */
const DEMO_MP4 = 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'

export function VideoDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { t } = useTranslation()
  const v = mockVideos.find((x) => x.id === id)

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{v?.title ?? 'Video'}</h1>
          <p className="text-sm text-muted-foreground">{t('nav.videos')} / {id}</p>
        </div>
        <Button asChild variant="outline">
          <Link to="/videos">返回</Link>
        </Button>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>播放器（react-player）</CardTitle>
          <CardDescription>演示 URL，非业务媒资</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="aspect-video overflow-hidden rounded-md border bg-black">
            <ReactPlayer src={DEMO_MP4} controls width="100%" height="100%" />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
