"""Tests standard tap features using the built-in SDK tests library."""

from singer_sdk.testing import get_standard_tap_tests
from tap_dataai.tap import TapDataAI

SAMPLE_CONFIG = {
    "start_date": "2022-10-01",
    "end_date": "2022-10-01",
    "auth_token": "",
    "type_report": "product_id",
    "type_values": ["20600004989866", "1053416106", "20600015405980", "20600002660981"],
    "granularity": "weekly",
    "countries": ["IN", ],
    "bundles": "all_supported",
}


# Run standard built-in tap tests from the SDK:
def test_standard_tap_tests():
    """Run standard tap tests from the SDK."""
    tests = get_standard_tap_tests(
        TapDataAI,
        config=SAMPLE_CONFIG
    )
    for test in tests:
        test()
