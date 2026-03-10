import logging
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVACMode, ClimateEntityFeature, FAN_AUTO, FAN_LOW, FAN_MEDIUM, FAN_HIGH, FAN_OFF,
    PRESET_NONE
)
from homeassistant.const import UnitOfTemperature, ATTR_TEMPERATURE

DOMAIN = "samsung_windfree"
_LOGGER = logging.getLogger(__name__)

# Pemetaan (Mapping) Mode SmartThings ke Home Assistant
ST_TO_HA_MODE = {"cool": HVACMode.COOL, "dry": HVACMode.DRY, "wind": HVACMode.FAN_ONLY, "auto": HVACMode.AUTO}
HA_TO_ST_MODE = {v: k for k, v in ST_TO_HA_MODE.items()}

ST_TO_HA_FAN = {"auto": FAN_AUTO, "low": FAN_LOW, "medium": FAN_MEDIUM, "high": FAN_HIGH}
HA_TO_ST_FAN = {v: k for k, v in ST_TO_HA_FAN.items()}

# Konstanta untuk Preset WindFree
PRESET_WINDFREE = "WindFree"

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the climate platform."""
    api = hass.data[DOMAIN]["api"]
    async_add_entities([SamsungWindFreeClimate(api)], True)


class SamsungWindFreeClimate(ClimateEntity):
    def __init__(self, api):
        self._api = api
        self._attr_name = "Samsung AC"
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        
        # --- KTP UNTUK MENGGABUNGKAN DEVICE DI HOME ASSISTANT & HOMEKIT ---
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._api.device_id)},
            "name": "Samsung WindFree AC",
            "manufacturer": "Samsung",
        }
        
        # --- PERBAIKAN BUG APPLE HOMEKIT ---
        self._attr_min_temp = 16
        self._attr_max_temp = 30
        self._attr_target_temperature_step = 1
        
        # --- FITUR YANG DIDUKUNG ---
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE | 
            ClimateEntityFeature.FAN_MODE |
            ClimateEntityFeature.PRESET_MODE
        )
        self._attr_hvac_modes = [HVACMode.OFF, HVACMode.COOL, HVACMode.DRY, HVACMode.FAN_ONLY, HVACMode.AUTO]
        self._attr_fan_modes = [FAN_OFF, FAN_AUTO, FAN_LOW, FAN_MEDIUM, FAN_HIGH]
        self._attr_preset_modes = [PRESET_NONE, PRESET_WINDFREE]
        
        # State Internal Awal
        self._attr_hvac_mode = HVACMode.OFF
        self._attr_current_temperature = None
        self._attr_target_temperature = None
        self._attr_fan_mode = FAN_OFF
        self._attr_preset_mode = PRESET_NONE

    async def async_update(self):
        """Update state dari API SmartThings (Polling)."""
        status = await self._api.get_status()
        if not status:
            return

        try:
            main_comp = status.get("components", {}).get("main", {})
            
            # --- BACA STATUS POWER ---
            power = main_comp.get("switch", {}).get("switch", {}).get("value")
            
            if power == "off":
                self._attr_hvac_mode = HVACMode.OFF
                self._attr_fan_mode = FAN_OFF  # Beritahu HomeKit bahwa kipas 0% (Mati)
            else:
                # Jika AC Nyala, baca Mode dan Kipas
                st_mode = main_comp.get("airConditionerMode", {}).get("airConditionerMode", {}).get("value")
                self._attr_hvac_mode = ST_TO_HA_MODE.get(st_mode, HVACMode.AUTO)
                
                st_fan = main_comp.get("airConditionerFanMode", {}).get("fanMode", {}).get("value")
                self._attr_fan_mode = ST_TO_HA_FAN.get(st_fan, FAN_AUTO)

            # --- BACA SUHU (Tetap dibaca meskipun AC mati) ---
            self._attr_current_temperature = main_comp.get("temperatureMeasurement", {}).get("temperature", {}).get("value")
            self._attr_target_temperature = main_comp.get("thermostatCoolingSetpoint", {}).get("coolingSetpoint", {}).get("value")
            
            # --- LOGIKA BACA STATUS WINDFREE (PRESET) ---
            optional_mode = main_comp.get("custom.airConditionerOptionalMode", {}).get("acOptionalMode", {}).get("value")
            if optional_mode == "windFree":
                self._attr_preset_mode = PRESET_WINDFREE
            else:
                self._attr_preset_mode = PRESET_NONE

        except Exception as e:
            _LOGGER.error(f"Error parsing data status: {e}")

    async def async_set_hvac_mode(self, hvac_mode):
        """Kirim perintah On/Off dan Mode."""
        commands = []
        if hvac_mode == HVACMode.OFF:
            commands.append({"component": "main", "capability": "switch", "command": "off"})
        else:
            commands.append({"component": "main", "capability": "switch", "command": "on"})
            st_mode = HA_TO_ST_MODE.get(hvac_mode)
            if st_mode:
                commands.append({"component": "main", "capability": "airConditionerMode", "command": "setAirConditionerMode", "arguments": [st_mode]})
        
        if await self._api.send_command(commands):
            self._attr_hvac_mode = hvac_mode
            self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs):
        """Kirim perintah ubah suhu."""
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is None:
            return
        commands = [{"component": "main", "capability": "thermostatCoolingSetpoint", "command": "setCoolingSetpoint", "arguments": [temp]}]
        if await self._api.send_command(commands):
            self._attr_target_temperature = temp
            self.async_write_ha_state()

    async def async_set_fan_mode(self, fan_mode):
        """Kirim perintah ubah kecepatan kipas."""
        if fan_mode == FAN_OFF:
            return # Abaikan jika mencoba set FAN_OFF dari UI, karena ini diatur otomatis oleh Power Off
            
        st_fan = HA_TO_ST_FAN.get(fan_mode)
        if not st_fan:
            return
        commands = [{"component": "main", "capability": "airConditionerFanMode", "command": "setFanMode", "arguments": [st_fan]}]
        if await self._api.send_command(commands):
            self._attr_fan_mode = fan_mode
            self.async_write_ha_state()

    async def async_set_preset_mode(self, preset_mode):
        """Kirim perintah untuk mengaktifkan/mematikan WindFree."""
        if preset_mode == PRESET_WINDFREE:
            arg = "windFree"
        else:
            arg = "off"

        commands = [{
            "component": "main",
            "capability": "custom.airConditionerOptionalMode",
            "command": "setAcOptionalMode",
            "arguments": [arg]
        }]
        
        if await self._api.send_command(commands):
            self._attr_preset_mode = preset_mode
            self.async_write_ha_state()