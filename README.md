# Utility Meter Reader platform integration for Home Assistant

Provides integration with utility meter reader webservice:
https://github.com/laurynas/utility-meter-reader

## Installation

Copy `custom_components/utility-meter-reader` to your homeassistant `config/` folder.

Add sensors to confguration.yaml

```yaml
sensor:
  - platform: utility_meter_reader
    entity: camera.your_meter_camera_entity
```