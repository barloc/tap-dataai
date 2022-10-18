"""DataAI tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th

from tap_dataai.streams import (
    AppPerformanceStream,
)

STREAM_TYPES = [
    AppPerformanceStream,
]


class TapDataAI(Tap):
    """DataAI tap class."""
    name = "tap-dataai"
    config_jsonschema = th.PropertiesList(
        th.Property(
            "auth_token",
            th.StringType,
            required=True,
            description="The token to authenticate against the API service"
        ),
        th.Property(
            "type_report",
            th.StringType,
            required=True,
            description="Must be product_id or company_id."
        ),
        th.Property(
            "type_values",
            th.ArrayType(th.StringType),
            required=True,
            description="Ids of the products or companies (array)."
        ),
        th.Property(
            "granularity",
            th.StringType,
            required=True,
            description="The granularity of the report (monthly, weekly, daily)."
        ),
        th.Property(
            "countries",
            th.ArrayType(th.StringType),
            required=True,
            description="Countries in the report (array)."
        ),
        th.Property(
            "bundles",
            th.StringType,
            required=True,
            description="Bundles in the report."
        ),
        th.Property(
            "devices",
            th.StringType,
            required=False,
            default="all_supported",
            description="Devices in the report."
        ),
        th.Property(
            "start_date",
            th.StringType,
            required=True,
            description="The earliest record date to sync"
        ),
        th.Property(
            "end_date",
            th.StringType,
            required=True,
            description="The latest record date to sync"
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


if __name__ == "__main__":
    TapDataAI.cli()
