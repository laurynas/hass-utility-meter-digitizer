# Utility Meter Digitizer for Home Assistant

Provides integration with [utility meter digitizer webservice](https://github.com/laurynas/utility-meter-digitizer).

## Installation

### Manual
Copy `custom_components/utility-meter-digitizer` to your home assistant `config/` folder.

### HACS
Add repository to HACS
- Repository: `laurynas/hass-utility-meter-digitizer`
- Type: `Integration`

### Sensor example
Add sensors to your home assistant configuration.yaml

```yaml
sensor:
  - platform: utility_meter_digitizer
    entity_id: camera.your_meter_camera_entity
    name: "Watermeter"
    digitizer_url: http://utility-meter-digitizer:8000/meter/demometer?decimals=3&max_increase=0.1
    scan_interval: 60
    flashlight_entity_id: light.test_cam_board_led
    flashlight_brightness: 70
    flashlight_duration: 3
```


## ESPHome

ESP32-Cam device [configuration examples](https://github.com/laurynas/esphome-devices/).
