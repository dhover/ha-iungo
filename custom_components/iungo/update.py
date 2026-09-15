"""Support for Iungo firmware updates."""

import asyncio
import logging

from homeassistant.components.update import UpdateEntity, UpdateEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import _hub_configuration_url
from .const import CONF_HOST, DOMAIN, FIRMWARE_UPDATE_POLL_INTERVAL, RELEASE_NOTES_URL
from .coordinator import IungoFirmwareUpdateCoordinator
from .iungo import (
    IungoError,
    async_get_firmware_update_status,
    async_start_firmware_update,
)

_LOGGER = logging.getLogger(__name__)


def _parse_percentage(value) -> int | None:
    """Parse the percentage value returned by the Iungo update status API."""
    if value is None:
        return None
    try:
        return int(float(str(value).strip()))
    except ValueError:
        return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Iungo update entity."""
    firmware_coordinator = entry.runtime_data.firmware
    async_add_entities(
        [
            IungoUpdateEntity(firmware_coordinator, entry),
        ]
    )


class IungoUpdateEntity(CoordinatorEntity, UpdateEntity):
    """Defines an Iungo update entity."""

    _attr_supported_features = (
        UpdateEntityFeature.INSTALL | UpdateEntityFeature.PROGRESS
    )

    def __init__(
        self,
        coordinator: IungoFirmwareUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the Iungo update entity."""
        super().__init__(coordinator)
        self._attr_name = "Iungo Firmware"
        self._attr_unique_id = f"{entry.entry_id}_firmware"
        self._attr_in_progress = False
        self._attr_update_percentage = None

    @property
    def installed_version(self) -> str | None:
        """Version installed and in use."""
        if not self.coordinator.data or not self.coordinator.data.get("sysinfo"):
            return None
        version = self.coordinator.data["sysinfo"].get("version", {})
        v = version.get("version", "")
        b = version.get("build", "")
        return f"{v}.{b}".strip()

    @property
    def latest_version(self) -> str | None:
        """Latest version available for install."""
        if not self.coordinator.data or not self.coordinator.data.get("latest_version"):
            return None
        fw = self.coordinator.data["latest_version"].get("fw", {})
        v = fw.get("version", "")
        b = fw.get("build", "")
        return f"{v}.{b}".strip()

    @property
    def release_url(self) -> str | None:
        """URL to the release notes of the latest available version."""
        if not self.coordinator.data or not self.coordinator.data.get("latest_version"):
            return None
        fw = self.coordinator.data["latest_version"].get("fw", {})
        build = fw.get("build")
        if not build:
            return None
        return RELEASE_NOTES_URL.format(build=build)

    async def async_install(self, version: str | None, backup: bool, **kwargs) -> None:
        """Install the latest firmware update."""
        host = self.coordinator.entry.data.get(CONF_HOST)
        session = async_get_clientsession(self.hass)

        self._attr_in_progress = True
        self._attr_update_percentage = None
        self.async_write_ha_state()

        try:
            await async_start_firmware_update(session, host)
            while True:
                await asyncio.sleep(FIRMWARE_UPDATE_POLL_INTERVAL)
                status = await async_get_firmware_update_status(session, host)
                percentage = _parse_percentage(status.get("percentage"))
                if percentage is not None:
                    self._attr_update_percentage = percentage
                    self.async_write_ha_state()
                if not status.get("in_progress", False):
                    if not status.get("success", False):
                        raise HomeAssistantError(
                            "Iungo firmware update did not complete successfully"
                        )
                    break
        except IungoError as err:
            raise HomeAssistantError(
                f"Error communicating with Iungo during firmware update: {err}"
            ) from err
        finally:
            self._attr_in_progress = False
            self._attr_update_percentage = None
            self.async_write_ha_state()

        await self.coordinator.async_request_refresh()

    @property
    def device_info(self) -> DeviceInfo | None:
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
            name="Iungo Hub",
            manufacturer="Iungo",
            model="Iungo",
            configuration_url=_hub_configuration_url(
                self.coordinator.entry.data.get(CONF_HOST)
            ),
            hw_version=hardware.get("revision", ""),
            sw_version=f"{sw_version} build {build}".strip(),
            serial_number=serial_number,
        )
