import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import discovery

from .api import SmartThingsOAuth2API

DOMAIN = "samsung_windfree"
_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required("client_id"): cv.string,
        vol.Required("client_secret"): cv.string,
        vol.Required("refresh_token"): cv.string,
        vol.Required("device_id"): cv.string,
    })
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    if DOMAIN not in config:
        return True

    conf = config[DOMAIN]
    
    api = SmartThingsOAuth2API(
        client_id=conf["client_id"],
        client_secret=conf["client_secret"],
        initial_refresh_token=conf["refresh_token"],
        device_id=conf["device_id"]
    )

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["api"] = api

    hass.async_create_task(discovery.async_load_platform(hass, "climate", DOMAIN, {}, config))
    hass.async_create_task(discovery.async_load_platform(hass, "switch", DOMAIN, {}, config))

    return True