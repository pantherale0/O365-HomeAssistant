"""Do configuration setup."""

from homeassistant.const import CONF_ENABLED
from homeassistant.helpers import discovery

from .const import (
    CONF_ACCOUNT,
    CONF_ACCOUNT_NAME,
    CONF_AUTO_REPLY_SENSORS,
    CONF_CHAT_SENSORS,
    CONF_CLIENT_ID,
    CONF_CONFIG_TYPE,
    CONF_COORDINATOR_EMAIL,
    CONF_COORDINATOR_SENSORS,
    CONF_EMAIL_SENSORS,
    CONF_ENABLE_UPDATE,
    CONF_KEYS_EMAIL,
    CONF_KEYS_SENSORS,
    CONF_PERMISSIONS,
    CONF_QUERY_SENSORS,
    CONF_STATUS_SENSORS,
    CONF_TODO_SENSORS,
    CONF_TRACK_NEW_CALENDAR,
    DOMAIN,
)
from .coordinator import O365EmailCordinator, O365SensorCordinator


async def do_setup(hass, config, account, account_name, conf_type, perms):
    """Run the setup after we have everything configured."""
    email_sensors = config.get(CONF_EMAIL_SENSORS, [])
    query_sensors = config.get(CONF_QUERY_SENSORS, [])
    status_sensors = config.get(CONF_STATUS_SENSORS, [])
    chat_sensors = config.get(CONF_CHAT_SENSORS, [])
    todo_sensors = config.get(CONF_TODO_SENSORS, [])
    auto_reply_sensors = config.get(CONF_AUTO_REPLY_SENSORS, [])
    enable_update = config.get(CONF_ENABLE_UPDATE, True)

    account_config = {
        CONF_CLIENT_ID: config.get(CONF_CLIENT_ID),
        CONF_ACCOUNT: account,
        CONF_EMAIL_SENSORS: email_sensors,
        CONF_QUERY_SENSORS: query_sensors,
        CONF_STATUS_SENSORS: status_sensors,
        CONF_CHAT_SENSORS: chat_sensors,
        CONF_TODO_SENSORS: todo_sensors,
        CONF_AUTO_REPLY_SENSORS: auto_reply_sensors,
        CONF_ENABLE_UPDATE: enable_update,
        CONF_TRACK_NEW_CALENDAR: config.get(CONF_TRACK_NEW_CALENDAR, True),
        CONF_ACCOUNT_NAME: config.get(CONF_ACCOUNT_NAME, ""),
        CONF_CONFIG_TYPE: conf_type,
        CONF_PERMISSIONS: perms,
    }
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    hass.data[DOMAIN][account_name] = account_config

    sensor_coordinator = O365SensorCordinator(hass, account_config)
    sensor_keys = await sensor_coordinator.async_setup_entries()
    await sensor_coordinator.async_config_entry_first_refresh()
    email_coordinator = O365EmailCordinator(hass, account_config)
    email_keys = await email_coordinator.async_setup_entries()
    await email_coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][account_name][CONF_KEYS_SENSORS] = sensor_keys
    hass.data[DOMAIN][account_name][CONF_COORDINATOR_SENSORS] = sensor_coordinator
    hass.data[DOMAIN][account_name][CONF_KEYS_EMAIL] = email_keys
    hass.data[DOMAIN][account_name][CONF_COORDINATOR_EMAIL] = email_coordinator

    _load_platforms(hass, account_name, config, account_config)


def _load_platforms(hass, account_name, config, account_config):
    hass.async_create_task(
        discovery.async_load_platform(
            hass, "calendar", DOMAIN, {CONF_ACCOUNT_NAME: account_name}, config
        )
    )
    if account_config[CONF_ENABLE_UPDATE]:
        hass.async_create_task(
            discovery.async_load_platform(
                hass, "notify", DOMAIN, {CONF_ACCOUNT_NAME: account_name}, config
            )
        )
    if (
        len(account_config[CONF_EMAIL_SENSORS]) > 0
        or len(account_config[CONF_QUERY_SENSORS]) > 0
        or len(account_config[CONF_STATUS_SENSORS]) > 0
        or len(account_config[CONF_CHAT_SENSORS]) > 0
    ):
        hass.async_create_task(
            discovery.async_load_platform(
                hass, "sensor", DOMAIN, {CONF_ACCOUNT_NAME: account_name}, config
            )
        )

    if len(account_config[CONF_TODO_SENSORS]) > 0 and account_config[
        CONF_TODO_SENSORS
    ].get(CONF_ENABLED, False):
        hass.async_create_task(
            discovery.async_load_platform(
                hass, "todo", DOMAIN, {CONF_ACCOUNT_NAME: account_name}, config
            )
        )
