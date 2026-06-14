import axios from 'axios'
import type {
  Chapter,
  Character,
  CharacterRelation,
  DashboardStats,
  Event,
  McpCallLog,
  McpStatus,
  Novel,
  Paginated,
  TimelineItem,
  WritingRules,
} from '@/types'

const api = axios.create({ baseURL: '/api' })

function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
  }
  return '操作失败'
}

export { getErrorMessage }

export const dashboardApi = {
  stats: () => api.get<DashboardStats>('/dashboard/stats').then((r) => r.data),
}

export const novelApi = {
  list: (page = 1) =>
    api.get<Paginated<Novel>>('/novel', { params: { page } }).then((r) => r.data),
  get: (id: string) => api.get<Novel>(`/novel/${id}`).then((r) => r.data),
  create: (data: Partial<Novel>) => api.post<Novel>('/novel', data).then((r) => r.data),
  update: (id: string, data: Partial<Novel>) =>
    api.put<Novel>(`/novel/${id}`, data).then((r) => r.data),
  delete: (id: string) => api.delete(`/novel/${id}`),
}

export const chapterApi = {
  list: (novelId?: string) =>
    api
      .get<Paginated<Chapter>>('/chapter', { params: { novel_id: novelId } })
      .then((r) => r.data),
  get: (id: string) => api.get<Chapter>(`/chapter/${id}`).then((r) => r.data),
  create: (data: Partial<Chapter>) => api.post<Chapter>('/chapter', data).then((r) => r.data),
  update: (id: string, data: Partial<Chapter>) =>
    api.put<Chapter>(`/chapter/${id}`, data).then((r) => r.data),
  delete: (id: string) => api.delete(`/chapter/${id}`),
}

export const characterApi = {
  list: (novelId?: string, keyword?: string) =>
    api
      .get<Paginated<Character>>('/character', {
        params: { novel_id: novelId, keyword },
      })
      .then((r) => r.data),
  get: (id: string) => api.get<Character>(`/character/${id}`).then((r) => r.data),
  create: (data: Partial<Character>) =>
    api.post<Character>('/character', data).then((r) => r.data),
  update: (id: string, data: Partial<Character>) =>
    api.put<Character>(`/character/${id}`, data).then((r) => r.data),
  delete: (id: string) => api.delete(`/character/${id}`),
  listRelations: (novelId: string) =>
    api
      .get<CharacterRelation[]>('/character/relation/list', { params: { novel_id: novelId } })
      .then((r) => r.data),
  createRelation: (data: CharacterRelation) =>
    api.post<CharacterRelation>('/character/relation', data).then((r) => r.data),
  deleteRelation: (sourceId: string, targetId: string) =>
    api.delete('/character/relation', { params: { source_id: sourceId, target_id: targetId } }),
}

export const eventApi = {
  list: (novelId: string) =>
    api.get<Paginated<Event>>('/event', { params: { novel_id: novelId } }).then((r) => r.data),
  get: (id: string) => api.get<Event>(`/event/${id}`).then((r) => r.data),
  create: (data: Partial<Event>) => api.post<Event>('/event', data).then((r) => r.data),
  update: (id: string, data: Partial<Event>) =>
    api.put<Event>(`/event/${id}`, data).then((r) => r.data),
  delete: (id: string) => api.delete(`/event/${id}`),
}

export const timelineApi = {
  withEvents: (novelId: string) =>
    api.get<TimelineItem[]>('/timeline/with-events', { params: { novel_id: novelId } }).then((r) => r.data),
  create: (data: { novel_id: string; event_id: string; sequence: number }) =>
    api.post('/timeline', data).then((r) => r.data),
  update: (id: string, data: { sequence?: number }) =>
    api.put(`/timeline/${id}`, data).then((r) => r.data),
  delete: (id: string) => api.delete(`/timeline/${id}`),
}

export const mcpApi = {
  status: () => api.get<McpStatus>('/mcp/status').then((r) => r.data),
  getApiKey: () => api.get<{ api_key: string }>('/mcp/api-key').then((r) => r.data),
  regenerateApiKey: () => api.post<{ api_key: string }>('/mcp/api-key/regenerate').then((r) => r.data),
  logs: (page = 1) =>
    api.get<Paginated<McpCallLog>>('/mcp/logs', { params: { page } }).then((r) => r.data),
}

export const writingRulesApi = {
  get: () => api.get<WritingRules>('/writing-rules').then((r) => r.data),
  update: (content: string) =>
    api.put<WritingRules>('/writing-rules', { content }).then((r) => r.data),
}
