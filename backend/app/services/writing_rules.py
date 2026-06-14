from pathlib import Path

from app.config import get_settings

DEFAULT_WRITING_RULES = """# NovelOS 写作规则

这些规则用于 MCP 提供给 LLM，生成或续写正文时必须遵守：

1. 保持第三人称有限视角，优先贴近当前章节主角的感知与判断。
2. 延续已有章节的语气、节奏、人物称谓和世界设定，不突然改变文风。
3. 不擅自改写已发生的关键事实、人物关系、时间线或已定结局。
4. 新增设定必须服务当前情节，并尽量与已有上下文建立因果联系。
5. 人物行为要符合已知性格、能力、处境和动机，避免为了推进剧情强行降智。
6. 场景描写优先选择能推动情绪、冲突或信息揭示的细节，避免空泛堆砌。
7. 对话要有角色差异，避免所有人物使用同一种语气。
8. 每次续写应留下可继续推进的钩子，但不要强行制造反转。
9. 输出正文时不要附加解释、总结、标题或 Markdown，除非用户明确要求。
"""


def _rules_path() -> Path:
    settings = get_settings()
    path = Path(settings.writing_rules_file)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[2] / path
    return path


def get_writing_rules() -> str:
    path = _rules_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(DEFAULT_WRITING_RULES, encoding="utf-8")
    content = path.read_text(encoding="utf-8").strip()
    return content or DEFAULT_WRITING_RULES.strip()


def get_writing_rules_path() -> str:
    return str(_rules_path())


def save_writing_rules(content: str) -> str:
    path = _rules_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = content.strip()
    if not normalized:
        raise ValueError("写作规则不能为空")
    path.write_text(normalized + "\n", encoding="utf-8")
    return normalized
