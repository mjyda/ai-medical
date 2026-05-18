export type MockDocument = {
  id: string
  name: string
  type: string
  sizeKb: number
  updatedAt: string
}

export const mockDocuments: MockDocument[] = [
  { id: '1', name: 'faq.md', type: '.md', sizeKb: 12, updatedAt: '2026-05-12' },
  { id: '2', name: 'company_profile.md', type: '.md', sizeKb: 8, updatedAt: '2026-05-11' },
  { id: '3', name: 'LangChain Intro.pdf', type: '.pdf', sizeKb: 420, updatedAt: '2026-05-10' },
]

export const mockVideos = [
  { id: 'v1', title: '大模型发展史导论.mp4', duration: '12:40', sizeMb: 128 },
  { id: 'v2', title: 'LangChain 入门.mp4', duration: '08:05', sizeMb: 64 },
]

export const mockTasks = [
  { id: 't1', name: '文档解析 - faq.md', type: '解析', status: 'running', progress: 62, created: '2026-05-13 09:00' },
  { id: 't2', name: '向量重建 - 全库', type: '索引', status: 'done', progress: 100, created: '2026-05-12 18:20' },
  { id: 't3', name: '视频转写 - sample.mp4', type: '转写', status: 'failed', progress: 12, created: '2026-05-11 11:05' },
]

export const mockChartDocs = [
  { name: 'Mon', count: 12 },
  { name: 'Tue', count: 18 },
  { name: 'Wed', count: 15 },
  { name: 'Thu', count: 22 },
  { name: 'Fri', count: 28 },
]

export const mockChartTasks = [
  { name: '进行中', value: 3 },
  { name: '已完成', value: 12 },
  { name: '失败', value: 1 },
]

export const mockGraph = {
  nodes: [
    { id: 'LLM', label: '大模型', x: 80, y: 60 },
    { id: 'RAG', label: 'RAG', x: 220, y: 60 },
    { id: 'Vec', label: '向量库', x: 360, y: 60 },
    { id: 'GPT', label: 'GPT', x: 150, y: 160 },
  ],
  edges: [
    { from: 'LLM', to: 'RAG' },
    { from: 'RAG', to: 'Vec' },
    { from: 'LLM', to: 'GPT' },
  ],
}
