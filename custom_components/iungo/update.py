from homeassistant.components.update import UpdateEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .coordinator import IungoDataUpdateCoordinator
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([IungoUpdateEntity(coordinator)])

class IungoUpdateEntity(UpdateEntity):
    def __init__(self, coordinator: IungoDataUpdateCoordinator):
        super().__init__()
        self.coordinator = coordinator
        self._attr_name = "Iungo Firmware"
        self._attr_unique_id = f"{coordinator.entry.entry_id}_firmware"

    @property
    def installed_version(self):
        version = self.coordinator.sysinfo.get("version", {}) if self.coordinator.sysinfo else {}
        return version.get("version")

    @property
    def latest_version(self):
        version = self.coordinator.latest_version.get("fw", {}) if self.coordinator.latest_version else {}
        return  version.get("version")

    @property
    def device_info(self):
        sysinfo = getattr(self.coordinator, "sysinfo", {}) or {}
        version = sysinfo.get("version", {})
        sw_version = version.get("version") or ""
        build = version.get("build") or ""
        serial_number = version.get("serial") or ""
        hwinfo = self.coordinator.hwinfo.get("hardware", {}) if self.coordinator.hwinfo else {}
        return {
            "identifiers": {(DOMAIN, self.coordinator.entry.entry_id)},
            "name": "Iungo Hub",
            "manufacturer": "Iungo",
            "model": "Iungo",
            "hw_version": hwinfo.get("revision", ""),
            "sw_version": f"{sw_version} build {build}".strip(),
            "serial_number": serial_number
        }