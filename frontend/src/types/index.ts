export interface Paginated<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface Novel {
  id: string
  name: string
  description?: string
  created_at: string
  updated_at: string
}

export interface Chapter {
  id: string
  novel_id: string
  title: string
  summary?: string
  content: string
  word_count: number
  status: string
  created_at: string
  updated_at: string
}

export interface Character {
  id: string
  novel_id: string
  name: string
  gender?: string
  birthday?: string
  description?: string
  current_status?: string
  abilities: string[]
  tags: string[]
  created_at: string
  updated_at: string
}

export interface CharacterRelation {
  source_id: string
  target_id: string
  relation_type: string
}

export interface EventCharacterBrief {
  id: string
  name: string
}

export interface Event {
  id: string
  novel_id: string
  title: string
  description?: string
  occur_time?: string
  location?: string | null
  characters?: EventCharacterBrief[]
  character_ids?: string[]
}

export interface TimelineItem {
  id: string
  novel_id: string
  event_id: string
  sequence: number
  event?: Event
}

export interface DashboardStats {
  novel_count: number
  chapter_count: number
  character_count: number
  event_count: number
}

export interface McpEndpoint {
  transport: string
  endpoint: string
  description: string
}

export interface McpStatus {
  status: string
  auth_enabled: boolean
  api_key?: string
  api_key_hint?: string
  endpoints: McpEndpoint[]
  tools: string[]
}

export interface McpCallLog {
  id: string
  tool_name: string
  arguments?: string
  result_summary?: string
  success: boolean
  error_message?: string
  created_at: string
}

export interface WritingRules {
  content: string
  file_path: string
}
