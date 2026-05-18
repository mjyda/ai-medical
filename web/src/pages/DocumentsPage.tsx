import { Link } from 'react-router-dom'
import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { mockDocuments } from '@/mocks/data'

export function DocumentsPage() {
  const { t } = useTranslation()
  const onDrop = useCallback((accepted: File[]) => {
    console.info('[mock] dropped files', accepted.map((f) => f.name))
  }, [])
  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, noClick: false })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">{t('nav.documents')}</h1>
        <p className="text-sm text-muted-foreground">react-dropzone · 仅本地列表，不上传</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>上传区（Mock）</CardTitle>
          <CardDescription>拖拽或点击选择文件</CardDescription>
        </CardHeader>
        <CardContent>
          <div
            {...getRootProps()}
            className={`cursor-pointer rounded-lg border-2 border-dashed p-8 text-center text-sm transition-colors ${
              isDragActive ? 'border-primary bg-muted' : 'border-muted-foreground/30'
            }`}
          >
            <input {...getInputProps()} />
            将文件拖到此处，或点击选择
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>文件列表</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>名称</TableHead>
                <TableHead>类型</TableHead>
                <TableHead>大小 (KB)</TableHead>
                <TableHead>更新</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>
            <TableBody>
              {mockDocuments.map((d) => (
                <TableRow key={d.id}>
                  <TableCell className="font-medium">{d.name}</TableCell>
                  <TableCell>{d.type}</TableCell>
                  <TableCell>{d.sizeKb}</TableCell>
                  <TableCell>{d.updatedAt}</TableCell>
                  <TableCell>
                    <Link to={`/documents/${d.id}`} className="text-sm underline underline-offset-4">
                      查看
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
