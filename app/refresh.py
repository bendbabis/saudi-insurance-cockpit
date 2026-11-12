"""Public source registry discovery job; schedule using cron."""
import json
from .sources import refresh_sources
if __name__ == "__main__":
    print(json.dumps(refresh_sources(), indent=2))
