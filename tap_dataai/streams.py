"""Stream type classes for tap-dataai."""

from pathlib import Path
from tap_dataai.client import DataAIStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class AppPerformanceStream(DataAIStream):
    """An app-performance report."""
    name = "app-performance"
    path = "app-performance"
    primary_keys = ["product_id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "app_performance.json"
