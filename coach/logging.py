__all__ = ["logger"]

from loguru import logger

logger.add("coach_{time}.log")
