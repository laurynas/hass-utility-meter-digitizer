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
    camera_entity = config.get("entity")
  
    if not camera_entity:
      hass.components.persistent_notification.create(
          "Error", "Camera entity not specified for utility_meter_reader."
      )
      return False

    add_entities([UtilityMeterReaderSensor(hass, camera_entity)])

class UtilityMeterReaderSensor(SensorEntity):
    _attr_name = "Watermeter"
    _attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS
    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    
    def __init__(self, hass, camera_entity):
        self.hass = hass
        self._camera_entity = camera_entity

    async def async_update(self) -> None:
        image = await async_get_image(self.hass, self._camera_entity)
        session = async_get_clientsession(self.hass)
        response = await session.post("http://digitizer:8000/detect", data=image.content)
        result = await response.text()

        self._attr_native_value = float(result) / 1000
