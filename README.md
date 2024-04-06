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
```


## ESPHome

ESP32Cam device ESPHome configuration example:

```yaml
esphome:
  name: test-cam
  friendly_name: test-cam

esp32:
  board: esp32dev
  framework:
    type: arduino

# Enable logging
logger:

api:
  encryption:
    key: "REPLACE THIS!!!"

ota:
  password: "REPLACETHIS!!!"

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

  # Enable fallback hotspot (captive portal) in case wifi connection fails
  ap:
    ssid: "Test-Cam Fallback Hotspot"
    password: "REPLACETHIS!!!"

captive_portal:

esp32_camera:
  name: "Camera"
  id: camera
  external_clock:
    pin: GPIO0
    frequency: 20MHz
  i2c_pins:
    sda: GPIO26
    scl: GPIO27
  data_pins: [GPIO5, GPIO18, GPIO19, GPIO21, GPIO36, GPIO39, GPIO34, GPIO35]
  vsync_pin: GPIO25
  href_pin: GPIO23
  pixel_clock_pin: GPIO22
  power_down_pin: GPIO32
  idle_framerate: 0.5 fps
  resolution: 640x480
  jpeg_quality: 10

output:
  - platform: ledc
    pin: GPIO4
    id: onboard_led_output

light:
  - platform: monochromatic
    id: onboard_led
    output: onboard_led_output
    name: "Flashlight"
```