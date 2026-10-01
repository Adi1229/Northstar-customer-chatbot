"""
models/base.py
--------------
SQLAlchemy declarative base shared by all ORM models.

All model classes must inherit from ``Base`` so that
``Base.metadata.create_all()`` can discover and create every table.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for all NorthStar ORM models."""
    pass
