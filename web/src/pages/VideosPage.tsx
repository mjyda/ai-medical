import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { mockVideos } from '@/mocks/data'

export function VideosPage() {
  const { t } = useTranslation()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">{t('nav.videos')}</h1>
        <p className="text-sm text-muted-foreground">Mock 列表</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>视频</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>标题</TableHead>
                <TableHead>时长</TableHead>
                <TableHead>大小 (MB)</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>
            <TableBody>
              {mockVideos.map((v) => (
                <TableRow key={v.id}>
                  <TableCell className="font-medium">{v.title}</TableCell>
                  <TableCell>{v.duration}</TableCell>
                  <TableCell>{v.sizeMb}</TableCell>
                  <TableCell>
                    <Link to={`/videos/${v.id}`} className="text-sm underline underline-offset-4">
                      播放
                    </Link>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
