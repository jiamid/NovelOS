from app.models.character import Character


def character_to_dict(character: Character) -> dict:
    return {
        "id": character.id,
        "novel_id": character.novel_id,
        "name": character.name,
        "gender": character.gender,
        "birthday": character.birthday,
        "description": character.description,
        "current_status": character.current_status,
        "abilities": character.abilities_list,
        "tags": character.tags_list,
    }
