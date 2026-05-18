import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'

type Msg = { role: 'user' | 'assistant'; text: string }

const seed: Msg[] = [
  { role: 'user', text: '什么是 RAG？' },
  { role: 'assistant', text: 'RAG（Retrieval-Augmented Generation）将检索到的文档片段作为上下文交给大模型生成回答。（Mock）' },
]

export function ChatPage() {
  const { t } = useTranslation()
  const [messages, setMessages] = useState<Msg[]>(seed)
  const [input, setInput] = useState('')

  const send = () => {
    const q = input.trim()
    if (!q) return
    setMessages((m) => [...m, { role: 'user', text: q }, { role: 'assistant', text: `（Mock 回复）已收到：${q}` }])
    setInput('')
  }

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-4">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">{t('nav.chat')}</h1>
        <p className="text-sm text-muted-foreground">Mock 对话 · 后续接 FastAPI + SSE</p>
      </div>
      <Card className="flex flex-1 flex-col">
        <CardHeader>
          <CardTitle>会话</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <ScrollArea className="h-[360px] rounded-md border p-3">
            <div className="space-y-3">
              {messages.map((m, i) => (
                <div key={i} className={m.role === 'user' ? 'text-right' : 'text-left'}>
                  <div
                    className={`inline-block max-w-[85%] rounded-lg border px-3 py-2 text-sm ${
                      m.role === 'user' ? 'bg-muted' : 'bg-card'
                    }`}
                  >
                    {m.text}
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
          <Separator />
          <div className="flex gap-2">
            <Input value={input} onChange={(e) => setInput(e.target.value)} placeholder="输入问题…" onKeyDown={(e) => e.key === 'Enter' && send()} />
            <Button type="button" onClick={send}>
              发送
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
