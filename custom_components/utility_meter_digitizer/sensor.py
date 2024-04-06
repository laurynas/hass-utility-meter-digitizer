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
import json
import asyncio

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required("entity_id"): cv.entity_id,
    vol.Optional("unique_id"): cv.string,
    vol.Optional("name"): cv.string,
    vol.Optional("device_class"): cv.string,
    vol.Optional("state_class"): cv.string,
    vol.Optional("unit_of_measurement"): cv.string,
    vol.Optional("digitizer_url"): cv.url,
    vol.Optional("flashlight_entity_id"): cv.entity_id,
    vol.Optional("flashlight_brightness"): cv.positive_int,
    vol.Optional("flashlight_duration"): cv.positive_int,
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
        self._camera_entity_id = config.get("entity_id")
        self._digitizer_url = config.get("digitizer_url")
        self._flashlight_entity_id = config.get("flashlight_entity_id")
        self._flashlight_brightness = config.get("flashlight_brightness", 100)
        self._flashlight_duration = config.get("flashlight_duration", 3)
        self._attr_unique_id = config.get("unique_id")
        self._attr_name = config.get("name")
        self._attr_device_class = config.get("device_class", SensorDeviceClass.WATER)
        self._attr_state_class = config.get("state_class", SensorStateClass.TOTAL_INCREASING)
        self._attr_native_unit_of_measurement = config.get("unit_of_measurement", UnitOfVolume.CUBIC_METERS)

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        old_state = await self.async_get_last_state()

        if old_state is not None and old_state.state != STATE_UNKNOWN:
            self._attr_native_value = old_state.state

    async def async_update(self) -> None:
        await self.__turn_on_flashlight()
        image = await async_get_image(self.hass, self._camera_entity_id)
        await self.__turn_off_flashlight()

        session = async_get_clientsession(self.hass)
        response = await session.post(self._digitizer_url, data=image.content)

        if response.status != 200:
            _LOGGER.warning(f"Failed to digitize image. Response: {response.status}")
            return

        result = await response.text()
        data = json.loads(result)

        self._attr_native_value = data['value']

    async def __turn_on_flashlight(self):
        if self._flashlight_entity_id is None:
            return

        await self.hass.services.async_call(
            "light",
            "turn_on",
            {
                "entity_id": self._flashlight_entity_id,
                "brightness": self._flashlight_brightness,
                "transition": 0,
            },
        )

        await asyncio.sleep(self._flashlight_duration)

    async def __turn_off_flashlight(self):
        if self._flashlight_entity_id is None:
            return

        await self.hass.services.async_call(
            "light",
            "turn_off",
            {
                "entity_id": self._flashlight_entity_id,
                "transition": 0,
            },
        )
