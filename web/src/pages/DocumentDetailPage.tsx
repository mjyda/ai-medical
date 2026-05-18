import { Link, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { mockDocuments } from '@/mocks/data'

export function DocumentDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { t } = useTranslation()
  const doc = mockDocuments.find((d) => d.id === id)

  if (!doc) {
    return (
      <div className="space-y-4">
        <p>未找到文档</p>
        <Button asChild variant="outline">
          <Link to="/documents">返回列表</Link>
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{doc.name}</h1>
          <p className="text-sm text-muted-foreground">{t('nav.documents')} / {doc.id}</p>
        </div>
        <Button asChild variant="outline">
          <Link to="/documents">返回</Link>
        </Button>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>元数据（Mock）</CardTitle>
          <CardDescription>类型 {doc.type} · {doc.sizeKb} KB</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Separator />
          <div className="rounded-md border bg-muted/30 p-4 text-sm text-muted-foreground">
            预览正文占位：对接后端后可渲染 Markdown / PDF 预览。
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
