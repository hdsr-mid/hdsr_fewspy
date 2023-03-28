import logging
import time


logger = logging.getLogger(__name__)


class Timer:
    """Record function efficiency."""

    def __init__(self):
        self.start = time.time()
        self.milestone = self.start

    def start(self):
        """Start the timer."""
        self.start = time.time()

    def report(self, message: str = ""):
        """Set milestone and report."""
        logger.debug(f"{message} in {(time.time() - self.milestone):.3f} sec")
        self.milestone = time.time()

    def reset(self, message: str = ""):
        """Report task-efficiency and reset."""
        if message:
            logger.debug(f"{message} in {(time.time() - self.start):.3f} sec")
        self.start = time.time()
        self.milestone = self.start
