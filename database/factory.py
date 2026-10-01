"""
database/factory.py
--------------------
Repository factory — selects and constructs the correct database adapter
based on ``config.DATABASE_BACKEND``.

Adding a new backend:
    1. Implement a class that extends ``BaseRepository``.
    2. Add a matching ``elif`` branch below.
    3. Update ``config.DATABASE_BACKEND``.
    No other file needs to change.
"""

import logging

import config
from database.base import BaseRepository

logger = logging.getLogger(__name__)


def create_repository(db_path: str | None = None) -> BaseRepository:
    """
    Instantiate and return the configured database adapter.

    Parameters
    ----------
    db_path:
        Optional override for the database file path (useful in tests).

    Returns
    -------
    BaseRepository
        A fully initialised adapter ready for queries.

    Raises
    ------
    NotImplementedError
        If ``config.DATABASE_BACKEND`` names an unrecognised backend.
    """
    backend = config.DATABASE_BACKEND.lower()
    logger.info("factory: creating repository for backend=%r", backend)

    if backend == "sqlite":
        # Import here (not at module top) to keep the factory decoupled from
        # concrete implementations — only the selected adapter is ever loaded.
        from database.sqlite_adapter import SQLiteAdapter
        return SQLiteAdapter(db_path=db_path)

    # ------------------------------------------------------------------
    # Future backends — add branches here:
    # ------------------------------------------------------------------
    # elif backend == "postgres":
    #     from database.postgres_adapter import PostgreSQLAdapter
    #     return PostgreSQLAdapter()
    #
    # elif backend == "api":
    #     from database.api_adapter import CompanyAPIAdapter
    #     return CompanyAPIAdapter()

    raise NotImplementedError(
        f"Database backend '{backend}' is not implemented. "
        f"Set config.DATABASE_BACKEND to a supported value (e.g. 'sqlite')."
    )
