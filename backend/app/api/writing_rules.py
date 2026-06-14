from fastapi import APIRouter, HTTPException

from app.schemas.writing_rules import WritingRulesOut, WritingRulesUpdate
from app.services.writing_rules import (
    get_writing_rules,
    get_writing_rules_path,
    save_writing_rules,
)

router = APIRouter(prefix="/writing-rules", tags=["writing-rules"])


@router.get("", response_model=WritingRulesOut)
def read_writing_rules():
    return WritingRulesOut(content=get_writing_rules(), file_path=get_writing_rules_path())


@router.put("", response_model=WritingRulesOut)
def update_writing_rules(body: WritingRulesUpdate):
    try:
        content = save_writing_rules(body.content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return WritingRulesOut(content=content, file_path=get_writing_rules_path())
