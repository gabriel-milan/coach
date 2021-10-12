"""
Provides a configured logger for the application.
"""

__all__ = ["logger"]

from loguru import logger

logger.add("scoach.log")
