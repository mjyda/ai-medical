import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { mockTasks } from '@/mocks/data'

function statusBadge(status: string) {
  if (status === 'running') return <Badge variant="secondary">进行中</Badge>
  if (status === 'done') return <Badge>完成</Badge>
  return <Badge variant="destructive">失败</Badge>
}

export function TasksPage() {
  const { t } = useTranslation()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">{t('nav.tasks')}</h1>
        <p className="text-sm text-muted-foreground">Tabs + Table · Mock</p>
      </div>
      <Tabs defaultValue="all">
        <TabsList>
          <TabsTrigger value="all">全部</TabsTrigger>
          <TabsTrigger value="run">进行中</TabsTrigger>
          <TabsTrigger value="ok">已完成</TabsTrigger>
          <TabsTrigger value="fail">失败</TabsTrigger>
        </TabsList>
        <TabsContent value="all">
          <Card>
            <CardHeader>
              <CardTitle>任务列表</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>名称</TableHead>
                    <TableHead>类型</TableHead>
                    <TableHead>状态</TableHead>
                    <TableHead>进度</TableHead>
                    <TableHead>创建时间</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockTasks.map((row) => (
                    <TableRow key={row.id}>
                      <TableCell className="font-medium">{row.name}</TableCell>
                      <TableCell>{row.type}</TableCell>
                      <TableCell>{statusBadge(row.status)}</TableCell>
                      <TableCell>{row.progress}%</TableCell>
                      <TableCell>{row.created}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="run">
          <TaskTable rows={mockTasks.filter((r) => r.status === 'running')} />
        </TabsContent>
        <TabsContent value="ok">
          <TaskTable rows={mockTasks.filter((r) => r.status === 'done')} />
        </TabsContent>
        <TabsContent value="fail">
          <TaskTable rows={mockTasks.filter((r) => r.status === 'failed')} />
        </TabsContent>
      </Tabs>
    </div>
  )
}

function TaskTable({ rows }: { rows: typeof mockTasks }) {
  return (
    <Card>
      <CardContent className="pt-6">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>名称</TableHead>
              <TableHead>状态</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((row) => (
              <TableRow key={row.id}>
                <TableCell>{row.name}</TableCell>
                <TableCell>{row.status}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
