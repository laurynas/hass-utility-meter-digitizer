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

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required("entity"): cv.entity_id,
    vol.Optional("unique_id"): cv.string,
    vol.Optional("name"): cv.string,
    vol.Optional("device_class"): cv.string,
    vol.Optional("state_class"): cv.string,
    vol.Optional("unit_of_measurement"): cv.string,
    vol.Optional("digitizer_url"): cv.url,
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
        self._digitizer_url = config.get("digitizer_url")
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
        image = await async_get_image(self.hass, self._camera_entity)
        session = async_get_clientsession(self.hass)
        response = await session.post(self._digitizer_url, data=image.content)

        if response.status != 200:
            _LOGGER.warning(f"Failed to digitize image. Response: {response.status}")
            return

        result = await response.text()
        data = json.loads(result)

        self._attr_native_value = data['value']
