import json

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Character(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "characters"
    __table_args__ = (
        UniqueConstraint("novel_id", "name", name="uq_character_novel_name"),
    )

    novel_id: Mapped[str] = mapped_column(ForeignKey("novels.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    gender: Mapped[str | None] = mapped_column(String(50), nullable=True)
    birthday: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_status: Mapped[str | None] = mapped_column(Text, nullable=True)
    abilities: Mapped[str] = mapped_column(Text, default="[]")
    tags: Mapped[str] = mapped_column(Text, default="[]")

    novel = relationship("Novel", back_populates="characters")

    @property
    def abilities_list(self) -> list[str]:
        try:
            return json.loads(self.abilities)
        except (json.JSONDecodeError, TypeError):
            return []

    @abilities_list.setter
    def abilities_list(self, value: list[str]) -> None:
        self.abilities = json.dumps(value, ensure_ascii=False)

    @property
    def tags_list(self) -> list[str]:
        try:
            return json.loads(self.tags)
        except (json.JSONDecodeError, TypeError):
            return []

    @tags_list.setter
    def tags_list(self, value: list[str]) -> None:
        self.tags = json.dumps(value, ensure_ascii=False)


class CharacterRelation(Base):
    __tablename__ = "character_relations"

    source_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), primary_key=True
    )
    target_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), primary_key=True
    )
    relation_type: Mapped[str] = mapped_column(String(100), nullable=False)
