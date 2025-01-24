# Utility Meter Digitizer for Home Assistant

Provides integration with [utility meter digitizer webservice](https://github.com/laurynas/utility-meter-digitizer).

## Installation

1. Copy `custom_components/utility-meter-digitizer` to your home assistant `config/` folder.

2. Add sensors to your home assistant confguration.yaml

### Sensor example
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
    rotation: 90
    sharpness: 2.5
    gamma: 0.8
    input_black: 40
    input_white: 220
```


## ESPHome

ESP32-Cam device [configuration examples](https://github.com/laurynas/esphome-devices/).
