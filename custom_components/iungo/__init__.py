""" The iungo integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from .const import CONF_HOST, DOMAIN
from .coordinator import IungoDataUpdateCoordinator, IungoFirmwareUpdateCoordinator


PLATFORMS = [Platform.SENSOR, Platform.UPDATE]


def _hub_configuration_url(host: str | None) -> str | None:
    """Build the Iungo web interface URL from the configured host."""
    if not host:
        return None
    if "://" in host:
        return host
    return f"http://{host}"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a config entry for iungo."""
    device_registry = dr.async_get(hass)
    configuration_url = _hub_configuration_url(entry.data.get(CONF_HOST))
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        name="Iungo Hub",
        manufacturer="Iungo",
        model="Iungo",
        configuration_url=configuration_url,
    )

    data_coordinator = IungoDataUpdateCoordinator(hass, entry)
    firmware_coordinator = IungoFirmwareUpdateCoordinator(hass, entry)

    await data_coordinator.async_initialize()
    await data_coordinator.async_config_entry_first_refresh()

    await firmware_coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "data": data_coordinator,
        "firmware": firmware_coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
