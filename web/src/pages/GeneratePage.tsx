import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'

export function GeneratePage() {
  const { t } = useTranslation()
  const [out, setOut] = useState('')

  const editor = useEditor({
    extensions: [StarterKit],
    content: '<p>在此编写补充说明…</p>',
    immediatelyRender: false,
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">{t('nav.generate')}</h1>
        <p className="text-sm text-muted-foreground">TipTap · Mock 生成</p>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>输入</CardTitle>
            <CardDescription>选择类型与来源（占位）</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>生成类型</Label>
              <Input defaultValue="学习笔记" />
            </div>
            <div className="space-y-2">
              <Label>来源文件</Label>
              <Input defaultValue="faq.md" />
            </div>
            <div className="space-y-2">
              <Label>补充说明（TipTap）</Label>
              <div className="rounded-md border bg-background">
                {editor ? <EditorContent editor={editor} className="tiptap min-h-[180px] px-3 py-2 text-sm" /> : null}
              </div>
            </div>
            <Button
              type="button"
              onClick={() => {
                const html = editor?.getHTML() ?? ''
                setOut(`【Mock 输出】\n类型: 学习笔记\nHTML 片段:\n${html}`)
              }}
            >
              生成（Mock）
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>生成结果</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="whitespace-pre-wrap rounded-md border bg-muted/40 p-3 text-xs">{out || '点击「生成」查看占位输出'}</pre>
            <div className="mt-3 flex gap-2">
              <Button type="button" variant="outline" size="sm" disabled>
                复制
              </Button>
              <Button type="button" variant="outline" size="sm" disabled>
                导出 MD
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
