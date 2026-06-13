from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

event_characters = Table(
    "event_characters",
    Base.metadata,
    Column("event_id", ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
    Column("character_id", ForeignKey("characters.id", ondelete="CASCADE"), primary_key=True),
)


class Event(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "events"

    novel_id: Mapped[str] = mapped_column(ForeignKey("novels.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    occur_time: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    novel = relationship("Novel", back_populates="events")
    characters = relationship("Character", secondary=event_characters)
    timelines = relationship("Timeline", back_populates="event", cascade="all, delete-orphan")


class Timeline(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "timelines"

    novel_id: Mapped[str] = mapped_column(ForeignKey("novels.id", ondelete="CASCADE"))
    event_id: Mapped[str] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    sequence: Mapped[int] = mapped_column(Integer, default=0)

    event = relationship("Event", back_populates="timelines")
