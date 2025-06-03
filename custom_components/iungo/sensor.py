from homeassistant.helpers.entity import Entity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .coordinator import IungoDataUpdateCoordinator
from .iungo import extract_sensors_from_object_info
import logging

_LOGGER = logging.getLogger(__name__)

class IungoSensor(Entity):
    def __init__(self, coordinator, unique_id, name, unit):
        self.coordinator = coordinator
        self._unique_id = unique_id
        self._name = name
        self._unit = unit

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
    def state(self):
        # Extract object_id and prop_id from unique_id
        object_id, prop_id = self._unique_id.split("_", 1)
        values = self.coordinator.data.get("object_values", {})
        # The values JSON is expected to be: {object_id: {prop_id: value, ...}, ...}
        return values.get(object_id, {}).get(prop_id)

    async def async_update(self):
        await self.coordinator.async_request_refresh()

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator = hass.data["iungo"][entry.entry_id]
    sensors = []
    object_info = coordinator.data.get("object_info", {})
    sensor_defs = extract_sensors_from_object_info(object_info)
    for sensor_def in sensor_defs:
        unique_id = f"{sensor_def['object_id']}_{sensor_def['prop_id']}"
        name = f"{sensor_def['object_name']} {sensor_def['prop_label']}"
        sensors.append(IungoSensor(coordinator, unique_id, name, sensor_def['unit']))
    async_add_entities(sensors)