from homeassistant.components.update import UpdateEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .coordinator import IungoFirmwareUpdateCoordinator

from .const import DOMAIN
from homeassistant.components.sensor import SensorEntity

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Iungo update entity."""
    firmware_coordinator = hass.data[DOMAIN][entry.entry_id]["firmware"]
    async_add_entities([IungoUpdateEntity(firmware_coordinator, entry)])


class IungoUpdateEntity(CoordinatorEntity, UpdateEntity):
    """Defines an Iungo update entity."""

    _attr_supported_features = UpdateEntityFeature.LATEST_VERSION

    def __init__(
        self,
        coordinator: IungoFirmwareUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the Iungo update entity."""
        super().__init__(coordinator)
        self._attr_name = "Iungo Firmware"
        self._attr_unique_id = f"{entry.entry_id}_firmware"

    @property
    def installed_version(self) -> str | None:
        """Version installed and in use."""
        if not self.coordinator.data or not self.coordinator.data.get("sysinfo"):
            return None
        version = self.coordinator.data["sysinfo"].get("version", {})
        return version.get("version")

    @property
    def latest_version(self) -> str | None:
        """Latest version available for install."""
        if not self.coordinator.data or not self.coordinator.data.get("latest_version"):
            return None
        version = self.coordinator.data["latest_version"].get("fw", {})
        return version.get("version")

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        if not self.coordinator.data:
            return None

        sysinfo = self.coordinator.data.get("sysinfo", {})
        version = sysinfo.get("version", {})
        sw_version = version.get("version") or ""
        build = version.get("build") or ""
        serial_number = version.get("serial") or ""

        hwinfo = self.coordinator.data.get("hwinfo", {})
        hardware = hwinfo.get("hardware", {})

        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.entry.entry_id)},
            name="Iungo",
            manufacturer="Iungo",
            model="Iungo",
            hw_version=hardware.get("revision", ""),
            sw_version=f"{sw_version} build {build}".strip(),
            serial_number=serial_number,
        )
