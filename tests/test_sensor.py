from types import SimpleNamespace

from custom_components.iungo.sensor import (
    IungoBreakoutEnergySensor,
    IungoBreakoutWaterSensor,
    IungoFirmwareVersionSensor,
    IungoLatestFirmwareVersionSensor,
)


def coordinator(data):
    return SimpleNamespace(data=data)


def test_breakout_energy_sensor_calculates_kwh():
    sensor = IungoBreakoutEnergySensor(
        coordinator({"object_values": {"breakout": {
            "offset": "1.25",
            "pulstotal": "250",
            "ppkwh": "100",
        }}}),
        "breakout",
        "energy-breakout",
        "entry-id",
    )

    assert sensor.native_value == 3.75
    assert sensor.native_unit_of_measurement == "kWh"


def test_breakout_water_sensor_returns_none_for_zero_factor():
    sensor = IungoBreakoutWaterSensor(
        coordinator({"object_values": {"breakout": {
            "offset": 1,
            "pulstotal": 10,
            "kfact": 0,
        }}}),
        "breakout",
        "water-breakout",
        "entry-id",
    )

    assert sensor.native_value is None


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
