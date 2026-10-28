from types import SimpleNamespace

import pytest

from custom_components.iungo.sensor import (
    IungoBreakoutEnergySensor,
    IungoBreakoutWaterSensor,
    IungoFirmwareVersionSensor,
    IungoLatestFirmwareVersionSensor,
    IungoSensor,
)


def coordinator(data):
    return SimpleNamespace(data=data)


def test_sensor_preserves_value_and_hub_device():
    sensor = IungoSensor(
        coordinator({"object_values": {"meter": {"power": "42.5"}}}),
        "meter_power",
        "Power",
        "W",
        "meter",
        "Meter",
        "energy",
        "power",
        "hub-device-id",
    )

    assert sensor.native_value == 42.5
    assert sensor.unique_id == "meter_power"
    assert sensor.device_info["via_device_id"] == "hub-device-id"


def test_breakout_energy_sensor_calculates_kwh():
    sensor = IungoBreakoutEnergySensor(
        coordinator({"object_values": {"breakout": {
            "offset": "1.25",
            "pulstotal": "250",
            "ppkwh": "100",
        }}}),
        "breakout",
        "energy-breakout",
        "hub-device-id",
    )

    assert sensor.native_value == 3.75
    assert sensor.native_unit_of_measurement == "kWh"
    assert sensor.device_info["via_device_id"] == "hub-device-id"


def test_breakout_water_sensor_returns_none_for_zero_factor():
    sensor = IungoBreakoutWaterSensor(
        coordinator({"object_values": {"breakout": {
            "offset": 1,
            "pulstotal": 10,
            "kfact": 0,
        }}}),
        "breakout",
        "water-breakout",
        "hub-device-id",
    )

    assert sensor.native_value is None
    assert sensor.device_info["via_device_id"] == "hub-device-id"


def test_firmware_sensors_format_versions():
    data = {
        "sysinfo": {"version": {"version": "1.5", "build": "4664"}},
        "latest_version": {"fw": {"version": "1.6", "build": "5000"}},
    }
    firmware = coordinator(data)

    assert IungoFirmwareVersionSensor(
        firmware, "entry-id").native_value == "1.5.4664"
    assert IungoLatestFirmwareVersionSensor(
        firmware, "entry-id").native_value == "1.6.5000"


@pytest.mark.parametrize(
    "data",
    [
        None,
        {},
        {"latest_version": {}},
        {"latest_version": {"fw": {}}},
        {"latest_version": {"fw": {"version": "1.6"}}},
        {"latest_version": {"fw": {"build": "5000"}}},
        {"latest_version": {"fw": {"version": None, "build": "5000"}}},
        {"latest_version": {"fw": {"version": "1.6", "build": ""}}},
        {"latest_version": {"fw": {"version": "1.6", "build": " "}}},
    ],
)
def test_latest_firmware_sensor_requires_complete_version(data):
    sensor = IungoLatestFirmwareVersionSensor(coordinator(data), "entry-id")

    assert sensor.native_value is None


def test_latest_firmware_sensor_accepts_zero_build():
    sensor = IungoLatestFirmwareVersionSensor(
        coordinator({"latest_version": {"fw": {"version": "1.6", "build": 0}}}),
        "entry-id",
    )

    assert sensor.native_value == "1.6.0"
