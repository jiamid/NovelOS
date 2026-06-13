# NovelOS

面向 AI Agent 的小说知识管理系统。帮助你在写作过程中维护人物、章节正文与时间线，并通过 MCP 将结构化上下文注入 AI 助手。

## 数据模型

```
小说 (Novel)
├── 章节 (Chapter)        名称、摘要、正文
├── 人物 (Character)      属性 + 关系图
└── 时间线 (Event)        时间、地点、人物、事件
```

| UI 名称 | API 路径 | 说明 |
|---------|----------|------|
| 小说 | `/api/novel` | 一部作品的顶层容器 |
| 章节 | `/api/chapter` | 章节正文存在 `content` 字段 |
| 人物 | `/api/character` | 同一小说内姓名不可重复 |
| 时间线 | `/api/event` + `/api/timeline` | 事件按 sequence 排序 |

## 技术栈

- **Backend**: FastAPI + SQLAlchemy + MCP (SSE / Streamable HTTP)
- **Frontend**: Vue 3 + Naive UI + TipTap
- **Vector**: Qdrant + sentence-transformers（本地 Embedding，无外部 API）

## 本地开发

### 1. 启动 Qdrant（向量检索）

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 2. 后端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./scripts/dev.sh
```

`dev.sh` 使用 `--reload` 热重载，并排除 `novelos.db` 和 `data/`，避免每次保存数据时触发重启。

默认使用 SQLite（`backend/novelos.db`），首次启动自动建表并迁移。

### 3. 前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

## Docker 部署

```bash
docker compose up -d
```

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:3000 |
| API | http://localhost:8000/api |
| MCP HTTP | http://localhost:8000/mcp/http |
| MCP SSE | http://localhost:8000/mcp/sse |

## MCP 连接

MCP 默认启用 **API Key 认证**。Key 在首次启动时自动生成，保存在 `backend/data/mcp_api_key`，也可在前端 **MCP** 页面查看。

### HTTP（推荐）

```json
{
  "mcpServers": {
    "novelos": {
      "url": "http://localhost:8000/mcp/http",
      "transport": "streamable-http",
      "headers": {
        "Authorization": "Bearer <your-api-key>"
      }
    }
  }
}
```

也支持请求头：`X-API-Key: <your-api-key>`

### SSE（Cherry Studio 等）

```json
{
  "mcpServers": {
    "novelos": {
      "url": "http://localhost:8000/mcp/sse",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer <your-api-key>"
      }
    }
  }
}
```

## MCP Tools

| Tool | 说明 | 主要参数 |
|------|------|----------|
| `get_story_context` | 聚合写作上下文（小说、章节、人物、关系、时间线、向量检索） | `novel_id`, `chapter_id?` |
| `get_novel` | 获取小说信息 | `novel_id` |
| `list_chapters` | 列出所有章节（不含正文） | `novel_id` |
| `get_chapter` | 获取章节详情（含正文） | `chapter_id` |
| `save_chapter_content` | 保存章节正文并索引 | `chapter_id`, `content` |
| `update_chapter` | 更新章节标题/摘要/状态/正文 | `chapter_id`, `data` |
| `search_character` | 搜索人物（关键词 + 语义） | `keyword`, `novel_id?` |
| `list_characters` | 列出所有人物 | `novel_id` |
| `get_character_relations` | 获取人物关系 | `novel_id` |
| `get_timeline` | 获取时间线 | `novel_id` |

> **ID 说明**：`novel_id` 表示小说，`chapter_id` 表示章节。在 UI 中打开对应页面即可从 URL 获取 ID（如 `/novel/<id>`、`/chapter/<id>`）。

### 典型写作流程

1. `get_story_context` — 拉取当前小说/章节的完整上下文
2. `get_chapter` — 读取已有正文
3. AI 生成续写内容
4. `save_chapter_content` — 写回正文

## 环境变量

见 [backend/.env.example](backend/.env.example)

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DATABASE_URL` | `sqlite:///./novelos.db` | 数据库连接 |
| `QDRANT_URL` | `http://localhost:6333` | Qdrant 地址 |
| `EMBEDDING_MODEL` | `paraphrase-multilingual-MiniLM-L12-v2` | 本地 Embedding 模型 |
| `MCP_REQUIRE_AUTH` | `true` | 是否要求 MCP API Key |
