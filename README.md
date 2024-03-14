# Utility Meter Digitizer platform integration for Home Assistant

Provides integration with utility meter digitizer webservice:
https://github.com/laurynas/utility-meter-digitizer

## Installation

Copy `custom_components/utility-meter-digitizer` to your homeassistant `config/` folder.

Add sensors to confguration.yaml

```yaml
sensor:
  - platform: utility_meter_digitizer
    entity: camera.your_meter_camera_entity
    decimals: 3
    name: "Watermeter"
    digitizer_url: http://utility-meter-digitizer:8000/digitize
```

### Sensor attributes

* `digitizer_url` - the url of the digitizer which accepts image and returns the number
* `decimals` - (optional, int) number of decimal places
* `max_increase` - (optional, float) maximum increase between readings. Can be used to eliminate wrong readings.
* `initial_state` - (optional, float) number to start from
