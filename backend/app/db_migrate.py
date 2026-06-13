import logging

from sqlalchemy import inspect, text

from app.database import engine

logger = logging.getLogger(__name__)


def _column_names(table: str) -> set[str]:
    insp = inspect(engine)
    if table not in insp.get_table_names():
        return set()
    return {c["name"] for c in insp.get_columns(table)}


def _rename_universe_id_columns(tables: set[str]) -> None:
    with engine.begin() as conn:
        for table in ("characters", "events", "timelines", "chapters"):
            if table not in tables:
                continue
            cols = _column_names(table)
            if "universe_id" in cols and "novel_id" not in cols:
                conn.execute(text(f"ALTER TABLE {table} RENAME COLUMN universe_id TO novel_id"))
                logger.info("Renamed %s.universe_id to novel_id", table)


def rename_universe_schema() -> None:
    """Migrate old schema: universes→novels, novels(chapters)→chapters, universe_id→novel_id."""
    insp = inspect(engine)
    tables = set(insp.get_table_names())

    if "universes" not in tables:
        _rename_universe_id_columns(tables)
        return

    with engine.begin() as conn:
        if "chapters" in tables:
            cols = _column_names("chapters")
            # Legacy PlotNode chapter table (empty); drop before renaming old novels→chapters.
            if "plot_node_id" in cols and "novel_id" not in cols and "universe_id" not in cols:
                conn.execute(text("DROP TABLE chapters"))
                logger.info("Dropped legacy empty chapters table")
                tables.discard("chapters")

        if "novels" in tables and "universe_id" in _column_names("novels"):
            conn.execute(text("ALTER TABLE novels RENAME TO chapters"))
            conn.execute(text("ALTER TABLE chapters RENAME COLUMN universe_id TO novel_id"))
            logger.info("Renamed novels table to chapters")
            tables.discard("novels")
            tables.add("chapters")

        conn.execute(text("ALTER TABLE universes RENAME TO novels"))
        logger.info("Renamed universes table to novels")

    _rename_universe_id_columns(set(inspect(engine).get_table_names()))


def ensure_chapter_content_columns() -> None:
    insp = inspect(engine)
    if "chapters" not in insp.get_table_names():
        return
    cols = _column_names("chapters")
    with engine.begin() as conn:
        if "content" not in cols:
            conn.execute(text('ALTER TABLE chapters ADD COLUMN content TEXT DEFAULT ""'))
            logger.info("Added chapters.content column")
        if "word_count" not in cols:
            conn.execute(text("ALTER TABLE chapters ADD COLUMN word_count INTEGER DEFAULT 0"))
            logger.info("Added chapters.word_count column")


def ensure_event_columns() -> None:
    insp = inspect(engine)
    tables = insp.get_table_names()
    if "events" in tables:
        cols = _column_names("events")
        with engine.begin() as conn:
            if "location" not in cols:
                conn.execute(text("ALTER TABLE events ADD COLUMN location VARCHAR(255)"))
                logger.info("Added events.location column")
    if "event_characters" not in tables:
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    CREATE TABLE event_characters (
                        event_id VARCHAR(36) NOT NULL,
                        character_id VARCHAR(36) NOT NULL,
                        PRIMARY KEY (event_id, character_id),
                        FOREIGN KEY(event_id) REFERENCES events(id) ON DELETE CASCADE,
                        FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE
                    )
                    """
                )
            )
            logger.info("Created event_characters table")


def run_migrations() -> None:
    rename_universe_schema()
    ensure_chapter_content_columns()
    ensure_event_columns()
