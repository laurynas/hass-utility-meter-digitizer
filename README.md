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

### Standalone device example

This example can work as standalone device without Home Assistant integration - periodically sending pictures to the digitizer directly.

```yaml
esphome:
  name: test-cam
  friendly_name: test-cam
  includes:
    - src/base64.hpp
  on_boot: 
    then:
      - lambda: |-
          id(camera).add_image_callback([](std::shared_ptr<esp32_camera::CameraImage> image) {
            if (image->was_requested_by(esp32_camera::WEB_REQUESTER)) {
              const char* data = reinterpret_cast<char*>(image->get_data_buffer());    
              id(image_data) = base64_encode(&data[0], image->get_data_length());
              ESP_LOGD("main", "encoded requested image, len %d", id(image_data).length());
            }
          });

esp32:
  board: esp32dev
  framework:
    type: arduino

# Enable logging
logger:

# Enable Home Assistant API
api:
  encryption:
    key: "REPLACETHIS!!!"

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

http_request:

globals:
  - id: image_data
    type: std::string

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
  idle_framerate: 0.25 fps
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

esp32_camera_web_server:
  - port: 8080
    mode: stream
  - port: 8081
    mode: snapshot

interval:
  - interval: 10m
    then:
      - light.turn_on: 
          id: onboard_led
          transition_length: 0s
          brightness: 70%
      - delay: 5s
      - lambda: |-
          id(camera).request_image(esp32_camera::WEB_REQUESTER);
      - wait_until:
          condition:
            lambda: return id(image_data).length() > 0;
      - http_request.post:
          url: http://utility-meter-digitizer:8000/meter/demometer?decimals=3&max_increase=0.1
          body: !lambda |-
            return "data:image/jpeg;base64," + id(image_data);
      - lambda: id(image_data) = "";
      - light.turn_off: 
          id: onboard_led
          transition_length: 0s
```
