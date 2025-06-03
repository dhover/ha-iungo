import logging
from .const import OBJECT_INFO_URL, OBJECT_VALUES_URL

_LOGGER = logging.getLogger(__name__)

async def async_get_object_info(session, host: str):
    """Fetch object info from the Iungo device."""
    url = OBJECT_INFO_URL.format(host=host)
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json(content_type=None)  # Accept any content type
            return data.get("rv", {})
    except Exception as e:
        _LOGGER.error(f"Error fetching object info from {url}: {e}")
        return {}

async def async_get_object_values(session, host: str):
    """Fetch object values from the Iungo device."""
    url = OBJECT_VALUES_URL.format(host=host)
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json(content_type=None)  # Accept any content type
            return data.get("rv", {})
    except Exception as e:
        _LOGGER.error(f"Error fetching object values from {url}: {e}")
        return {}

def parse_object_values(values_json: dict) -> dict:
    """Convert the values JSON to {object_id: {prop_id: value}} format."""
    lookup = {}
    objects = values_json.get("objects", [])
    for obj in objects:
        oid = obj.get("oid")
        propsval = obj.get("propsval", [])
        if not oid:
            continue
        lookup[oid] = {prop["id"]: prop["value"] for prop in propsval if "id" in prop and "value" in prop}
    return lookup

def extract_sensors_from_object_info(object_info: dict):
    """Extract sensor definitions from Iungo object_info JSON."""
    sensors = []
    for obj_id, obj in object_info.items():
        info = obj.get("info", {})
        driver = info.get("driver", {})
        props = driver.get("props", {})
        obj_type = info.get("type", "unknown")
        obj_name = driver.get("name", obj_id)
        for prop_key, prop in props.items():
            # Only add properties with type 'number' or log == True
            if prop.get("type") == "number" or prop.get("log") is True:
                sensor = {
                    "object_id": obj_id,
                    "object_type": obj_type,
                    "object_name": obj_name,
                    "prop_id": prop.get("id", prop_key),
                    "prop_label": prop.get("label", prop_key),
                    "unit": prop.get("unit"),
                }
                sensors.append(sensor)
    return sensors