from loguru import logger
import sys

# Remove any existing handlers
logger.remove()

# Add a single handler with our desired format
logger.add(
    sys.stderr,
    format="<level>{level}</level> | {message}",
    level="INFO",
    colorize=True
) 