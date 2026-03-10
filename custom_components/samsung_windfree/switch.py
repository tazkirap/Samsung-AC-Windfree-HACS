import logging
from homeassistant.components.switch import SwitchEntity

DOMAIN = "samsung_windfree"
_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the switch platform."""
    api = hass.data[DOMAIN]["api"]
    async_add_entities([WindFreeSwitch(api)], True)


class WindFreeSwitch(SwitchEntity):
    def __init__(self, api):
        self._api = api
        self._attr_name = "WindFree Mode"
        self._attr_is_on = False
        
        # --- KTP YANG SAMA PERSIS DENGAN CLIMATE.PY ---
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._api.device_id)},
            "name": "Samsung WindFree AC",
            "manufacturer": "Samsung",
        }

    async def async_update(self):
        """Update state dari API SmartThings (Polling)."""
        status = await self._api.get_status()
        if not status:
            return
            
        try:
            optional_mode = status.get("components", {}).get("main", {}).get("custom.airConditionerOptionalMode", {}).get("acOptionalMode", {}).get("value")
            self._attr_is_on = (optional_mode == "windFree")
        except Exception as e:
            _LOGGER.error(f"Error parsing switch status: {e}")

    async def async_turn_on(self, **kwargs):
        """Nyalakan WindFree."""
        commands = [{
            "component": "main",
            "capability": "custom.airConditionerOptionalMode",
            "command": "setAcOptionalMode",
            "arguments": ["windFree"]
        }]
        if await self._api.send_command(commands):
            self._attr_is_on = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Matikan WindFree."""
        commands = [{
            "component": "main",
            "capability": "custom.airConditionerOptionalMode",
            "command": "setAcOptionalMode",
            "arguments": ["off"]
        }]
        if await self._api.send_command(commands):
            self._attr_is_on = False
            self.async_write_ha_state()