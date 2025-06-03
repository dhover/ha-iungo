from homeassistant.helpers.entity import Entity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from .coordinator import IungoDataUpdateCoordinator
from .iungo import extract_sensors_from_object_info
import logging

_LOGGER = logging.getLogger(__name__)

# Simple mapping for device_class and state_class based on unit/label/id
DEVICE_CLASS_MAP = {
    "W": SensorDeviceClass.POWER,
    "kWh": SensorDeviceClass.ENERGY,
    "V": SensorDeviceClass.VOLTAGE,
    "A": SensorDeviceClass.CURRENT,
    "°C": SensorDeviceClass.TEMPERATURE,
    "m³": SensorDeviceClass.GAS,
    "m³/h": SensorDeviceClass.GAS,
    "%": SensorDeviceClass.HUMIDITY,
    "hPa": SensorDeviceClass.PRESSURE,
    "mm/h": SensorDeviceClass.PRECIPITATION,
    "l/min": SensorDeviceClass.WATER,
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
    "l/min": SensorStateClass.MEASUREMENT,
}

class IungoSensor(Entity):
    def __init__(self, coordinator, unique_id, name, unit, object_id, object_name, object_type):
        self.coordinator = coordinator
        self._unique_id = unique_id
        self._name = name
        self._unit = unit
        self._object_id = object_id
        self._object_name = object_name
        self._object_type = object_type

        # Guess device_class and state_class from unit
        self._device_class = DEVICE_CLASS_MAP.get(unit)
        self._state_class = STATE_CLASS_MAP.get(unit)

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def native_unit_of_measurement(self):
        return self._unit

    @property
    def device_class(self):
        return self._device_class

    @property
    def state_class(self):
        return self._state_class

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers = {("iungo", self._object_id)},
            name = self._object_name,
            manufacturer = "Iungo",
            model = self._object_type,
        )

    @property
    def state(self):
        object_id, prop_id = self._unique_id.split("_", 1)
        values = self.coordinator.data.get("object_values", {})
        return values.get(object_id, {}).get(prop_id)

    async def async_update(self):
        await self.coordinator.async_request_refresh()

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator = hass.data["iungo"][entry.entry_id]
    object_info = coordinator.data.get("object_info", {})
    _LOGGER.warning("Iungo object_info: %s", object_info)
    sensor_defs = extract_sensors_from_object_info(object_info)
    _LOGGER.warning("Iungo sensor_defs: %s", sensor_defs)
    sensors = []
    for sensor_def in sensor_defs:
        unique_id = f"{sensor_def['object_id']}_{sensor_def['prop_id']}"
        name = f"{sensor_def['object_name']} {sensor_def['prop_label']}"
        sensors.append(
            IungoSensor(
                coordinator,
                unique_id,
                name,
                sensor_def['unit'],
                sensor_def['object_id'],
                sensor_def['object_name'],
                sensor_def['object_type'],
            )
        )
    _LOGGER.warning("Iungo sensors: %s", sensors)
    async_add_entities(sensors)