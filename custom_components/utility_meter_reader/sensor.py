from homeassistant.components.sensor import (SensorDeviceClass, SensorEntity, SensorStateClass)
from homeassistant.const import UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.components.camera import async_get_image
from homeassistant.helpers.aiohttp_client import async_get_clientsession

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    if not config.get("entity"):
      hass.components.persistent_notification.create("Error", "Camera entity not specified for utility_meter_reader.")
      return False

    add_entities([UtilityMeterReaderSensor(hass, config)])

class UtilityMeterReaderSensor(SensorEntity):
    def __init__(self, hass, config):
        self.hass = hass
        self._camera_entity = config.get("entity")
        self._decimals = config.get("decimals", 0)
        self._attr_name = config.get("name", "Watermeter")
        self._attr_device_class = config.get("device_class", SensorDeviceClass.WATER)
        self._attr_state_class = config.get("state_class", SensorStateClass.TOTAL_INCREASING)
        self._attr_native_unit_of_measurement = config.get("unit_of_measurement", UnitOfVolume.CUBIC_METERS)

    async def async_update(self) -> None:
        image = await async_get_image(self.hass, self._camera_entity)
        session = async_get_clientsession(self.hass)
        response = await session.post("http://digitizer:8000/detect", data=image.content)
        result = await response.text()

        self._attr_native_value = float(result) / 10 ** self._decimals
