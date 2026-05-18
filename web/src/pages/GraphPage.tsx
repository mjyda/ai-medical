import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { mockGraph } from '@/mocks/data'

export function GraphPage() {
  const { t } = useTranslation()
  const nodeById = Object.fromEntries(mockGraph.nodes.map((n) => [n.id, n]))

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">{t('nav.graph')}</h1>
        <p className="text-sm text-muted-foreground">静态 SVG · Neo4j Bloom 待后端</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>关系示意</CardTitle>
          <CardDescription>Mock 节点与边</CardDescription>
        </CardHeader>
        <CardContent>
          <svg viewBox="0 0 440 220" className="h-auto w-full max-w-2xl rounded-md border bg-muted/20">
            {mockGraph.edges.map((e, i) => {
              const a = nodeById[e.from]
              const b = nodeById[e.to]
              if (!a || !b) return null
              return (
                <line
                  key={i}
                  x1={a.x}
                  y1={a.y}
                  x2={b.x}
                  y2={b.y}
                  stroke="hsl(0,0%,60%)"
                  strokeWidth="2"
                />
              )
            })}
            {mockGraph.nodes.map((n) => (
              <g key={n.id}>
                <rect
                  x={n.x - 48}
                  y={n.y - 22}
                  width="96"
                  height="44"
                  rx="6"
                  fill="hsl(0,0%,100%)"
                  stroke="hsl(0,0%,45%)"
                />
                <text x={n.x} y={n.y + 4} textAnchor="middle" className="fill-foreground text-xs font-medium">
                  {n.label}
                </text>
              </g>
            ))}
          </svg>
        </CardContent>
      </Card>
    </div>
  )
}
