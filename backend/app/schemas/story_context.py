from pydantic import BaseModel


class StoryContextOut(BaseModel):
    writing_rules: str
    novel: dict
    current_chapter: dict | None
    chapters: list[dict]
    characters: list[dict]
    character_relations: list[dict]
    timeline: list[dict]
    vector_hits: list[dict]
