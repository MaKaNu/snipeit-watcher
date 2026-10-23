import os

# Must be set before snipeit_watcher.config is imported (it instantiates Settings at import time).
os.environ.setdefault("SNIPEIT_API_TOKEN", "test-token")
