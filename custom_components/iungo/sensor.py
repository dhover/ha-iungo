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
    "m³/h": SensorDeviceClass.GAS,
    "%": SensorDeviceClass.HUMIDITY,
    "hPa": SensorDeviceClass.PRESSURE,
    "mm/h": SensorDeviceClass.PRECIPITATION_INTENSITY,
    "l/min": SensorDeviceClass.WATER,
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
    "l/min": SensorStateClass.MEASUREMENT,
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
    "l/min": 3,
    "puls/kWh": 0,
    "puls": 0,
    "x": 0,
    "sec": 0,
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
    def __init__(self, coordinator, unique_id, name, unit, object_id, object_name, object_type):
        super().__init__(coordinator)
        self._unique_id = unique_id
        self._unit = unit.replace("¤", "€").replace(
            "m3", "m³").replace("m2", "m²") if unit else None
        self._object_id = object_id
        self._object_name = object_name
        self._object_type = object_type
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
            identifiers={(DOMAIN, self._object_id)},
            name=self._object_name,
            manufacturer="Iungo",
            model=self._object_type,
        )

    @property
    def state(self):
        object_id, prop_id = self._unique_id.split("_", 1)
        object_values = self.coordinator.data.get("object_values", {})
        value = object_values.get(object_id, {}).get(prop_id)
        return value


class IungoBreakoutEnergySensor(IungoSensor):
    def __init__(self, coordinator, object_id, object_name):
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
        )
        self._attr_has_entity_name = True
        self._attr_suggested_display_precision = 3

    @property
    def state(self):
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
    def __init__(self, coordinator, object_id, object_name):
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
        )
        self._device_class = SensorDeviceClass.WATER
        self._attr_has_entity_name = True
        self._attr_suggested_display_precision = 3

    @property
    def device_class(self):
        return self._device_class

    @property
    def state(self):
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
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: IungoDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    object_info = coordinator.data.get("object_info", {})
    sensor_defs = extract_sensors_from_object_info(object_info)
    sensors = []
    object_values = coordinator.data.get("object_values", {})
    breakout_energy_added = False
    breakout_water_added = False

    for sensor_def in sensor_defs:
        unique_id = f"{sensor_def['object_id']}_{sensor_def['prop_id']}"
        obj_val = object_values.get(sensor_def['object_id'], {})
        friendly_name = obj_val.get("name") or sensor_def['object_name']
        prop_label = sensor_def['prop_label']
        name = TARIFF_LABEL_MAP.get(prop_label, prop_label)
        unit = sensor_def['unit']
        if unit:
            unit = unit.replace("¤", "€").replace("m3", "m³").replace("m2", "m²")
        value = object_values.get(sensor_def['object_id'], {}).get(sensor_def['prop_id'])
        if value is None or value == "unknown":
            continue
        sensors.append(
            IungoSensor(
                coordinator,
                unique_id,
                name,
                unit,
                sensor_def['object_id'],
                friendly_name,
                sensor_def['object_type'],
            )
        )
        if sensor_def["object_type"] == "breakout" and not breakout_energy_added:
            sensors.append(
                IungoBreakoutEnergySensor(
                    coordinator,
                    sensor_def["object_id"],
                    friendly_name,
                )
            )
            breakout_energy_added = True
        if sensor_def["object_type"] == "water" and not breakout_water_added:
            sensors.append(
                IungoBreakoutWaterSensor(
                    coordinator,
                    sensor_def["object_id"],
                    friendly_name,
                )
            )
            breakout_water_added = True

    async_add_entities(sensors)
