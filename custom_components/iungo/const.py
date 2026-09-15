"""Constants for the iungo integration."""

DOMAIN = "iungo"

CONF_HOST = "host"

DEFAULT_HOST = "192.168.x.x"
DEFAULT_UPDATE_INTERVAL = 30
DEFAULT_FIRMWARE_UPDATE_INTERVAL = 3600

OBJECT_INFO_URL = "http://{host}/iungo/api_request/object_info"
OBJECT_VALUES_URL = "http://{host}/iungo/api_request/objmgr_list_objects_props_values"
OBJECT_SYSINFO_URL = "http://{host}/iungo/api_request/sysinfo_version"
OBJECT_HWINFO_URL = "http://{host}/iungo/api_request/sysinfo_hw_revision"
OBJECT_LATEST_VERSION = "http://{host}/iungo/api_request/fw_get_remote_info"
FW_UPDATE_URL = "http://{host}/iungo/api_request/fw_update"
FW_UPDATE_STATUS_URL = "http://{host}/iungo/api_request/fw_get_update_status"

RELEASE_NOTES_URL = "https://atedec.com/iungo/releasenotes?ver={build}"

FIRMWARE_UPDATE_POLL_INTERVAL = 5
