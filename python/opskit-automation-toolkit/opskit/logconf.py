"""Central logging configuration for every opskit module.

Machine-readable results (JSON) go to stdout;
human-readable diagnostics go to stderr through the logging module.
This lets you pipe results into jq or files without mixing in log noise.
"""

import logging
import os
import sys

FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"


def setup_logging(level=None):
  """Level comes from the argument, OPSKIT_LOG_LEVEL, or INFO."""
  resolved = (level or os.environ.get("OPSKIT_LOG_LEVEL", "INFO")).upper()
  logging.basicConfig(
      level=resolved, format=FORMAT, stream=sys.stderr, force=True
  )
