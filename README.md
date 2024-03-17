# Utility Meter Digitizer for Home Assistant

Provides integration with [utility meter digitizer webservice](https://github.com/laurynas/utility-meter-digitizer).

## Installation

1. Copy `custom_components/utility-meter-digitizer` to your home assistant `config/` folder.

2. Add sensors to your home assistant confguration.yaml

### Sensor example
```yaml
sensor:
  - platform: utility_meter_digitizer
    entity: camera.your_meter_camera_entity
    name: "Watermeter"
    digitizer_url: http://utility-meter-digitizer:8000/meter/demometer?decimals=3&max_increase=0.1
    scan_interval: 60
```
