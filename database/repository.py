"""
database/repository.py
-----------------------
Module-level singleton accessor for the active database repository.

Business services import ``get_repository()`` from this module to obtain
the configured adapter.  The adapter is created once (lazy singleton) and
reused for the lifetime of the process.

Usage
-----
    from database.repository import get_repository

    repo = get_repository()
    order = repo.get_order("111")

To override the repository in tests, call ``set_repository()`` before
any service code runs:

    from database.repository import set_repository
    from unittest.mock import MagicMock

    set_repository(MagicMock(spec=BaseRepository))
"""

import logging

from database.base import BaseRepository
from database.factory import create_repository

logger = logging.getLogger(__name__)

# Module-level singleton — initialised on first call to get_repository().
_repository: BaseRepository | None = None


def get_repository() -> BaseRepository:
    """
    Return the shared repository instance, creating it on first call.

    Returns
    -------
    BaseRepository
        The active database adapter.
    """
    global _repository
    if _repository is None:
        logger.info("repository: initialising singleton repository.")
        _repository = create_repository()
    return _repository


def set_repository(repo: BaseRepository) -> None:
    """
    Override the singleton repository (intended for use in tests).

    Parameters
    ----------
    repo:
        A ``BaseRepository`` instance (or mock) to use instead of the
        default adapter.
    """
    global _repository
    logger.debug("repository: singleton overridden with %r", repo)
    _repository = repo


def reset_repository() -> None:
    """
    Clear the singleton so ``get_repository()`` re-initialises on next call.
    Useful for resetting state between integration tests.
    """
    global _repository
    _repository = None
