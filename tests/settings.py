"""Test settings: development mode, DATABASE_URL (SQLite by default) and no rate limit."""

import os

os.environ["EXAMPLE_DEBUG"] = "true"
os.environ["EXAMPLE_API_AUTH_MODE"] = "session"
os.environ["EXAMPLE_RATE_LIMIT_PER_MINUTE"] = "0"

from example_project.settings import *  # noqa: F403
