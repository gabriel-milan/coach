"""
Provides a configured logger for the application.
"""

__all__ = ["logger"]

from pathlib import Path

from loguru import logger

logger.add(Path.home() / "scoach.log")
