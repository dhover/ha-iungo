"""Support for Iungo sensors."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import IungoDataUpdateCoordinator
from .coordinator import IungoFirmwareUpdateCoordinator
from .iungo import extract_sensors_from_object_info

_LOGGER = logging.getLogger(__name__)

# Simple mapping for device_class and state_class based on unit/label/id
DEVICE_CLASS_MAP = {
    "W": SensorDeviceClass.POWER,
    "kWh": SensorDeviceClass.ENERGY,
    "V": SensorDeviceClass.VOLTAGE,
    "A": SensorDeviceClass.CURRENT,
    "°C": SensorDeviceClass.TEMPERATURE,
    "m³": SensorDeviceClass.GAS,
    "m³/h": SensorDeviceClass.VOLUME_FLOW_RATE,
    "%": SensorDeviceClass.HUMIDITY,
    "hPa": SensorDeviceClass.PRESSURE,
    "mm/h": SensorDeviceClass.PRECIPITATION_INTENSITY,
    "L/min": SensorDeviceClass.VOLUME_FLOW_RATE,
    "W/m²": SensorDeviceClass.IRRADIANCE,
    "m/s": SensorDeviceClass.WIND_SPEED,
    "°": SensorDeviceClass.WIND_DIRECTION,
}

STATE_CLASS_MAP = {
    "kWh": SensorStateClass.TOTAL_INCREASING,
    "m³": SensorStateClass.TOTAL_INCREASING,
    "m³/h": SensorStateClass.MEASUREMENT,
    "W": SensorStateClass.MEASUREMENT,
    "V": SensorStateClass.MEASUREMENT,
    "A": SensorStateClass.MEASUREMENT,
    "°C": SensorStateClass.MEASUREMENT,
    "%": SensorStateClass.MEASUREMENT,
    "hPa": SensorStateClass.MEASUREMENT,
    "mm/h": SensorStateClass.MEASUREMENT,
    "L/min": SensorStateClass.MEASUREMENT,
    "W/m²": SensorStateClass.MEASUREMENT,
    "m/s": SensorStateClass.MEASUREMENT,
    "°": SensorStateClass.MEASUREMENT_ANGLE,
}

DISPLAY_PRECISION_MAP = {
    "kWh": 3,
    "m³": 3,
    "W": 0,
    "V": 1,
    "A": 2,
    "°C": 1,
    "°": 0,
    "%": 0,
    "hPa": 1,
    "mm/h": 1,
    "L/min": 3,
    "puls/kWh": 0,
    "puls": 0,
    "x": 0,
    "s": 0,
    "puls/m³": 0,
    "€/kWh": 3,
    "€/m³": 3,
    "m³/h": 3,
    "m/s": 1,
    "W/m²": 0,
}

TARIFF_LABEL_MAP = {
    "T1": "Tariff 1",
    "-T1": "Tariff 1 (Returned)",
    "T2": "Tariff 2",
    "-T2": "Tariff 2 (Returned)",
    "€ T1": "Cost Tariff 1",
    "€ -T1": "Cost Tariff 1 (Returned)",
    "€ T2": "Cost Tariff 2",
    "€ -T2": "Cost Tariff 2 (Returned)",
    "€ Gas": "Cost Gas",
    "Pulses / kW·h": "Pulses/kWh",
}


class IungoSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Iungo sensor."""

    def __init__(
        self,
        coordinator,
        unique_id,
        name,
        unit,
        object_id,
        object_name,
        object_type,
        prop_id,
        entry_id,
    ):
        super().__init__(coordinator)
        self._unique_id = unique_id
        self._unit = unit
        self._object_id = object_id
        self._object_name = object_name
        self._object_type = object_type
        self._prop_id = prop_id
        self._entry_id = entry_id
        # Default mapping
        self._device_class = DEVICE_CLASS_MAP.get(unit)
        # Override for water meters
        if unit == "m³" and object_type == "water":
            self._device_class = SensorDeviceClass.WATER
        self._state_class = STATE_CLASS_MAP.get(unit)
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._attr_has_entity_name = True
        self._attr_suggested_display_precision = DISPLAY_PRECISION_MAP.get(
            unit, 2)

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def device_class(self):
        """Return the device class."""
        return self._device_class

    @property
    def state_class(self):
        """Return the state class."""
        return self._state_class

    @property
    def device_info(self):
        """Return device information for this sensor."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._object_id)},
            name=self._object_name,
            manufacturer="Iungo",
            model=self._object_type,
            # Link child devices to the hub device created in __init__.py.
            via_device=(DOMAIN, self._entry_id),
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        object_values = self.coordinator.data.get("object_values", {})
        value = object_values.get(self._object_id, {}).get(self._prop_id)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return value
        return value


class IungoBreakoutEnergySensor(IungoSensor):
    """Special sensor for calculated energy from breakout device."""

    def __init__(self, coordinator, object_id, object_name, entry_id):
        unique_id = f"{object_id}_calculated_energy"
        name = "Calculated Energy"
        super().__init__(
            coordinator,
            unique_id,
            name,
            "kWh",
            object_id,
            object_name,
            "breakout",
            "calculated_energy",
            entry_id,
        )
        self._attr_has_entity_name = True
        self._attr_suggested_display_precision = 3

    @property
    def native_value(self):
        """Return the calculated energy state."""
        object_values = self.coordinator.data.get("object_values", {})
        obj = object_values.get(self._object_id, {})
        try:
            offset = float(obj.get("offset", 0))
            totalimport = float(obj.get("pulstotal", 0))
            pulses = float(obj.get("ppkwh", 1))
            if pulses == 0:
                return None
            return round(offset + totalimport / pulses, 3)
        except (ValueError, TypeError):
            return None


class IungoBreakoutWaterSensor(IungoSensor):
    """Special sensor for calculated water from breakout_water device."""

    def __init__(self, coordinator, object_id, object_name, entry_id):
        unique_id = f"{object_id}_calculated_water"
        name = "Calculated Water"
        super().__init__(
            coordinator,
            unique_id,
            name,
            "m³",
            object_id,
            object_name,
            "breakout_water",
            "calculated_water",
            entry_id,
        )
        self._device_class = SensorDeviceClass.WATER
        self._attr_has_entity_name = True
        self._attr_suggested_display_precision = 3

    @property
    def device_class(self):
        """Return the device class."""
        return self._device_class

    @property
    def native_value(self):
        """Return the calculated water state."""
        object_values = self.coordinator.data.get("object_values", {})
        obj = object_values.get(self._object_id, {})
        try:
            offset = float(obj.get("offset", 0))
            totalwater = float(obj.get("pulstotal", 0))
            pulses = float(obj.get("kfact", 1))
            if pulses == 0:
                return None
            return round(offset + totalwater / pulses, 3)
        except (ValueError, TypeError):
            return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Iungo sensors based on a config entry."""
    data_coordinator: IungoDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]["data"]
    firmware_coordinator: IungoFirmwareUpdateCoordinator = hass.data[
        DOMAIN][entry.entry_id]["firmware"]
    object_info = data_coordinator.data.get("object_info", {})
    sensor_defs = extract_sensors_from_object_info(object_info)
    sensors = []
    object_values = data_coordinator.data.get("object_values", {})
    breakout_energy_added = False
    breakout_water_added = False

    def _get_friendly_name(obj_id: str, fallback: str) -> str:
        obj_val = object_values.get(obj_id, {})
        return obj_val.get("name") or fallback

    for sensor_def in sensor_defs:
        unique_id = f"{sensor_def['object_id']}_{sensor_def['prop_id']}"
        friendly_name = _get_friendly_name(
            sensor_def["object_id"], sensor_def["object_name"]
        )
        prop_label = sensor_def['prop_label']
        name = TARIFF_LABEL_MAP.get(prop_label, prop_label)
        unit = sensor_def['unit']

        sensors.append(
            IungoSensor(
                data_coordinator,
                unique_id,
                name,
                unit,
                sensor_def['object_id'],
                friendly_name,
                sensor_def['object_type'],
                sensor_def['prop_id'],
                entry.entry_id,
            )
        )

        _LOGGER.debug("object_id: %s - %s - %s - %s - %s - %s",
                      sensor_def['object_id'],
                      sensor_def["object_type"],
                      sensor_def["object_name"],
                      sensor_def["unit"],
                      sensor_def['prop_id'], sensor_def['unit'])

        if sensor_def["object_name"] == "energy-breakout" and not breakout_energy_added:
            sensors.append(
                IungoBreakoutEnergySensor(
                    data_coordinator,
                    sensor_def["object_id"],
                    friendly_name,
                    entry.entry_id,
                )
            )
            breakout_energy_added = True
        if sensor_def["object_name"] == "water-breakout" and not breakout_water_added:
            sensors.append(
                IungoBreakoutWaterSensor(
                    data_coordinator,
                    sensor_def["object_id"],
                    friendly_name,
                    entry.entry_id,
                )
            )
            breakout_water_added = True

    sensors.append(
        IungoFirmwareVersionSensor(firmware_coordinator, entry.entry_id)
    )
    sensors.append(
        IungoLatestFirmwareVersionSensor(firmware_coordinator, entry.entry_id)
    )
    async_add_entities(sensors)


class IungoFirmwareVersionSensor(CoordinatorEntity, SensorEntity):
    """Sensor for the current firmware version."""

    def __init__(self, coordinator: IungoFirmwareUpdateCoordinator, entry_id: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_name = "Iungo Firmware Version"
        self._attr_unique_id = f"{entry_id}_firmware_version"
        self._attr_icon = "mdi:tag"

    @property
    def native_value(self):
        """Return the current firmware version."""
        version = self.coordinator.data.get("sysinfo", {}).get(
            "version", {}) if self.coordinator.data else {}
        v = version.get("version", "")
        b = version.get("build", "")
        return f"{v} build {b}".strip()

    @property
    def device_info(self):
        """Return device information for this sensor."""
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "Iungo Hub",
            "manufacturer": "Iungo",
            "model": "Iungo",
        }


class IungoLatestFirmwareVersionSensor(CoordinatorEntity, SensorEntity):
    """Sensor for the latest firmware version available."""

    def __init__(self, coordinator: IungoFirmwareUpdateCoordinator, entry_id: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_name = "Iungo Latest Firmware Version"
        self._attr_unique_id = f"{entry_id}_latest_firmware_version"
        self._attr_icon = "mdi:tag-arrow-up"

    @property
    def native_value(self):
        """Return the latest firmware version available."""
        fw = self.coordinator.data.get("latest_version", {}).get(
            "fw", {}) if self.coordinator.data else {}
        v = fw.get("version", "")
        b = fw.get("build", "")
        return f"{v} build {b}".strip()

    @property
    def device_info(self):
        """Return device information for this sensor."""
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "Iungo Hub",
            "manufacturer": "Iungo",
            "model": "Iungo",
        }
