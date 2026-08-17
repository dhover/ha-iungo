import json
from pathlib import Path

import pytest

from custom_components.iungo.iungo import (
    CannotConnect,
    async_get_hwinfo,
    async_get_latest_version,
    async_get_object_info,
    async_get_object_values,
    async_get_sysinfo,
    extract_sensors_from_object_info,
    parse_object_values,
)


FIXTURE_DIR = Path(__file__).parents[1] / "custom_components"


def load_fixture(name):
    with (FIXTURE_DIR / name).open(encoding="utf-8") as fixture_file:
        return json.load(fixture_file)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return None

    def raise_for_status(self):
        return None

    async def json(self, **kwargs):
        return self.payload


class FakeSession:
    def __init__(self, payload):
        self.payload = payload
        self.urls = []

    def get(self, url):
        self.urls.append(url)
        return FakeResponse(self.payload)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("function", "fixture", "expected_key"),
    [
        (async_get_object_info, "objects.json", "20fa6711"),
        (async_get_object_values, "values.json", "objects"),
        (async_get_sysinfo, "sysinfo.json", "fw"),
        (async_get_hwinfo, "hwinfo.json", "hardware"),
        (async_get_latest_version, "lastest_version.json", "fw"),
    ],
)
async def test_api_functions_return_rv_payload(function, fixture, expected_key):
    session = FakeSession(load_fixture(fixture))

    result = await function(session, "192.168.1.20")

    assert expected_key in result
    assert session.urls[0].startswith("http://192.168.1.20/iungo/api_request/")


@pytest.mark.asyncio
async def test_api_timeout_becomes_cannot_connect():
    class TimeoutResponse:
        async def __aenter__(self):
            raise TimeoutError

        async def __aexit__(self, exc_type, exc, traceback):
            return None

    class TimeoutSession:
        def get(self, _url):
            return TimeoutResponse()

    with pytest.raises(CannotConnect, match="Timeout while connecting"):
        await async_get_sysinfo(TimeoutSession(), "iungo.local")


def test_parse_object_values_normalizes_fixture():
    values = parse_object_values(load_fixture("values.json")["rv"])

    assert values["86218d46"]["solar"] == 310.701
    assert values["86218d46"]["name"] == "Fronius omvormer"
    assert "missing" not in values["86218d46"]


def test_extract_sensors_skips_duplicates_and_numeric_property_keys():
    object_info = {
        "object": {
            "info": {
                "type": "energy",
                "driver": {
                    "name": "energy-meter",
                    "props": {
                        "1": {"id": "power", "type": "number", "unit": "W"},
                        "power": {"id": "power", "type": "number", "unit": "W"},
                        "voltage": {
                            "type": "number",
                            "unit": "V",
                            "label": "Voltage",
                        },
                    },
                },
            }
        }
    }

    sensors = extract_sensors_from_object_info(object_info)

    assert [sensor["prop_id"] for sensor in sensors] == ["power", "voltage"]
    assert sensors[1]["prop_label"] == "Voltage"
