from loguru import logger
import sys


# Add a method for convenience
def deep_debug(self, message, *args, **kwargs):
    self.log("DEEPDEBUG", message, *args, **kwargs)

def setup_logging():
    logger.remove()

    # Define a custom level called "DEEPDEBUG" with a lower level number than DEBUG (10)
    # Add the custom level without checking first
    try:
        logger.level("DEEPDEBUG", no=5, color="<blue><bold>")
    except ValueError:
        # Level already exists
        pass

    logger.deep_debug = deep_debug.__get__(logger)

    logger.add("logs/info.log", level="INFO", format="{time} | {level} | {message}", rotation="10 MB", serialize=True)
    logger.add("logs/debug.log", level="DEBUG", format="{time} | {level} | {message}", rotation="10 MB", serialize=True)
    logger.add("logs/deepdebug.log", level="DEEPDEBUG", format="{time} | {level} | {message}", rotation="10 MB", serialize=True)
    logger.add(sys.stderr, level="ERROR")