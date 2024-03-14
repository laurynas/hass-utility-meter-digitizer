from homeassistant.components.sensor import (SensorDeviceClass, RestoreSensor, SensorStateClass)
from homeassistant.const import UnitOfVolume, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.components.camera import async_get_image
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
import logging

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required("entity"): cv.entity_id,
    vol.Optional("decimals", default=0): int,
    vol.Optional("unique_id"): cv.string,
    vol.Optional("name"): cv.string,
    vol.Optional("device_class"): cv.string,
    vol.Optional("state_class"): cv.string,
    vol.Optional("unit_of_measurement"): cv.string,
    vol.Optional("digitizer_url"): cv.url,
    vol.Optional("initial_state"): float,
    vol.Optional("max_increase"): float,
})

_LOGGER = logging.getLogger(__name__)

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    add_entities([UtilityMeterDigitizerSensor(hass, config)])

class UtilityMeterDigitizerSensor(RestoreSensor):
    def __init__(self, hass, config):
        self.hass = hass
        self._camera_entity = config.get("entity")
        self._decimals = config.get("decimals", 0)
        self._digitizer_url = config.get("digitizer_url", "http://utility-meter-digitizer:8000/digitize")
        self._initial_state = config.get("initial_state")
        self._max_increase = config.get("max_increase", float("inf"))
        self._attr_unique_id = config.get("unique_id")
        self._attr_name = config.get("name")
        self._attr_device_class = config.get("device_class", SensorDeviceClass.WATER)
        self._attr_state_class = config.get("state_class", SensorStateClass.TOTAL_INCREASING)
        self._attr_native_unit_of_measurement = config.get("unit_of_measurement", UnitOfVolume.CUBIC_METERS)
        self._reset_value = None

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        old_state = await self.async_get_last_state()

        if old_state is not None and old_state.state != STATE_UNKNOWN:
            self._attr_native_value = old_state.state

        if self._attr_native_value is None:
            self._attr_native_value = self._initial_state

    async def async_update(self) -> None:
        image = await async_get_image(self.hass, self._camera_entity)
        session = async_get_clientsession(self.hass)
        response = await session.post(self._digitizer_url, data=image.content)

        if response.status != 200:
            _LOGGER.warning(f"Failed to digitize image. Response: {response.status}")
            return

        result = await response.text()
        value = float(result) / 10 ** self._decimals

        self.update_value(value)

    def update_value(self, value):
        if self._attr_native_value is None:
            self._attr_native_value = value
            return

        old_value = float(self._attr_native_value)

        if value < old_value:
            _LOGGER.warning(f"Invalid value: {value}. Value is lower than the previous value.")
            return

        if value - old_value > self._max_increase:
            _LOGGER.warning(f"Invalid value: {value}. Value increase exceeds the maximum allowed increase.")
            return

        self._attr_native_value = value
