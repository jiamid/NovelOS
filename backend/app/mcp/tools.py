from dataclasses import dataclass
from typing import Callable

from sqlalchemy.orm import Session

from app.mcp import handlers


@dataclass
class McpTool:
    name: str
    description: str
    input_schema: dict
    handler: Callable[[Session, dict], dict]


MCP_TOOLS: list[McpTool] = [
    McpTool(
        name="get_story_context",
        description="获取写作上下文：小说信息、章节、人物、关系、时间线与向量检索结果",
        input_schema={
            "type": "object",
            "properties": {
                "novel_id": {"type": "string", "description": "小说 ID"},
                "chapter_id": {"type": "string", "description": "当前章节 ID（可选）"},
            },
            "required": ["novel_id"],
        },
        handler=handlers.handle_get_story_context,
    ),
    McpTool(
        name="get_novel",
        description="获取小说基本信息",
        input_schema={
            "type": "object",
            "properties": {"novel_id": {"type": "string"}},
            "required": ["novel_id"],
        },
        handler=handlers.handle_get_novel,
    ),
    McpTool(
        name="list_chapters",
        description="列出小说下所有章节（不含正文）",
        input_schema={
            "type": "object",
            "properties": {"novel_id": {"type": "string"}},
            "required": ["novel_id"],
        },
        handler=handlers.handle_list_chapters,
    ),
    McpTool(
        name="get_chapter",
        description="获取章节详情（含正文）",
        input_schema={
            "type": "object",
            "properties": {"chapter_id": {"type": "string", "description": "章节 ID"}},
            "required": ["chapter_id"],
        },
        handler=handlers.handle_get_chapter,
    ),
    McpTool(
        name="save_chapter_content",
        description="保存章节正文并更新向量索引",
        input_schema={
            "type": "object",
            "properties": {
                "chapter_id": {"type": "string", "description": "章节 ID"},
                "content": {"type": "string", "description": "正文内容"},
            },
            "required": ["chapter_id", "content"],
        },
        handler=handlers.handle_save_chapter_content,
    ),
    McpTool(
        name="update_chapter",
        description="更新章节标题、摘要、状态或正文",
        input_schema={
            "type": "object",
            "properties": {
                "chapter_id": {"type": "string", "description": "章节 ID"},
                "data": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "summary": {"type": "string"},
                        "status": {"type": "string"},
                        "content": {"type": "string"},
                    },
                },
            },
            "required": ["chapter_id", "data"],
        },
        handler=handlers.handle_update_chapter,
    ),
    McpTool(
        name="search_character",
        description="搜索人物，支持关键词和语义检索",
        input_schema={
            "type": "object",
            "properties": {
                "keyword": {"type": "string"},
                "novel_id": {"type": "string", "description": "限定在某个小说内搜索"},
            },
            "required": ["keyword"],
        },
        handler=handlers.handle_search_character,
    ),
    McpTool(
        name="list_characters",
        description="列出小说下所有人物",
        input_schema={
            "type": "object",
            "properties": {"novel_id": {"type": "string"}},
            "required": ["novel_id"],
        },
        handler=handlers.handle_list_characters,
    ),
    McpTool(
        name="get_character_relations",
        description="获取人物关系列表",
        input_schema={
            "type": "object",
            "properties": {"novel_id": {"type": "string"}},
            "required": ["novel_id"],
        },
        handler=handlers.handle_get_character_relations,
    ),
    McpTool(
        name="get_timeline",
        description="获取小说时间线（时间、地点、人物、事件）",
        input_schema={
            "type": "object",
            "properties": {"novel_id": {"type": "string"}},
            "required": ["novel_id"],
        },
        handler=handlers.handle_get_timeline,
    ),
]

TOOL_MAP = {tool.name: tool for tool in MCP_TOOLS}
