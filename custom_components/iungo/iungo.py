import aiohttp
import async_timeout
import logging
from .const import OBJECT_INFO_URL, OBJECT_VALUES_URL, OBJECT_SYSINFO_URL, OBJECT_HWINFO_URL, OBJECT_LATEST_VERSION

_LOGGER = logging.getLogger(__name__)


async def async_get_object_info(session, host: str):
    """Fetch object info from the Iungo."""
    try:
        url = OBJECT_INFO_URL.format(host=host)
        async with session.get(url) as response:
            response.raise_for_status()
            # Accept any content type
            data = await response.json(content_type=None)
            _LOGGER.debug("Fetched object info: %s", data)
            return data.get("rv", {})
    except Exception as err:
        _LOGGER.error(f"Error fetching object info from {url}: {err}")
        return {}


async def async_get_object_values(session, host: str):
    """Fetch object values from the Iungo."""
    try:
        url = OBJECT_VALUES_URL.format(host=host)
        async with session.get(url) as response:
            response.raise_for_status()
            # Accept any content type
            data = await response.json(content_type=None)
            _LOGGER.debug("Fetched object values: %s", data)
            return data.get("rv", {})
    except Exception as err:
        _LOGGER.error(f"Error fetching object values from {url}: {err}")
        return {}


async def async_get_sysinfo(session: aiohttp.ClientSession, host: str):
    """Fetch system info from Iungo."""
    try:
        url = OBJECT_SYSINFO_URL.format(host=host)
        # async with async_timeout.timeout(10):
        async with session.get(url) as response:
            response.raise_for_status()
            # Accept any content type
            data = await response.json(content_type=None)
            _LOGGER.debug("Fetched sysinfo: %s", data)
            return data.get("rv", {})
    except Exception as err:
        _LOGGER.error(f"Error fetching sysinfo values from {url}: {err}")
        return {}


async def async_get_hwinfo(session: aiohttp.ClientSession, host: str):
    """Fetch system info from Iungo."""
    try:
        url = OBJECT_HWINFO_URL.format(host=host)
        # async with async_timeout.timeout(10):
        async with session.get(url) as response:
            response.raise_for_status()
            # Accept any content type
            data = await response.json(content_type=None)
            _LOGGER.debug("Fetched hw info: %s", data)
            return data.get("rv", {})
    except Exception as err:
        _LOGGER.error(f"Error fetching hardware info values from {url}: {err}")
        return {}


async def async_get_latest_version(session: aiohttp.ClientSession, host: str) -> str | None:
    """Fetch the latest firmware version from the Iungo."""
    try:
        url = OBJECT_LATEST_VERSION.format(host=host)
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json(content_type=None)
            _LOGGER.debug("Fetched latest version: %s", data)
            return data.get("rv", {})
    except Exception as err:
        _LOGGER.error(f"Error fetching latest version from {url}: {err}")
        return None


def parse_object_values(values_json: dict) -> dict:
    """Convert the values JSON to {object_id: {prop_id: value}} format."""
    lookup = {}
    objects = values_json.get("objects", [])
    for obj in objects:
        oid = obj.get("oid")
        propsval = obj.get("propsval", [])
        if not oid:
            continue
        lookup[oid] = {prop["id"]: prop["value"]
                       for prop in propsval if "id" in prop and "value" in prop}
    return lookup


def extract_sensors_from_object_info(object_info: dict):
    """Extract sensor definitions from Iungo object_info JSON, avoiding duplicates and skipping numeric keys."""
    sensors = []
    for obj_id, obj in object_info.items():
        info = obj.get("info", {})
        driver = info.get("driver", {})
        props = driver.get("props", {})
        obj_type = info.get("type", "unknown")
        obj_name = driver.get("name", obj_id)
        obj_description = driver.get("description", None)
        seen_ids = set()
        for prop_key, prop in props.items():
            # Skip numeric keys (only use named keys)
            if prop_key.isdigit():
                continue
            prop_id = prop.get("id", prop_key)
            if prop_id in seen_ids:
                continue  # Skip duplicate
            seen_ids.add(prop_id)
            # Only add properties with type 'number' or log == True
            if prop.get("type") == "number" and prop.get("unit", None) != None:
                sensor = {
                    "object_id": obj_id,
                    "object_type": obj_type,
                    "object_name": obj_name,
                    "object_description": obj_description,
                    "prop_id": prop_id,
                    "prop_label": prop.get("label", prop_key),
                    "unit": prop.get("unit"),
                }
                sensors.append(sensor)
    return sensors
