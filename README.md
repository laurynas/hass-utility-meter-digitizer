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
Set digitiser url via http://watermeter-test.local

```yaml
esphome:
  name: watermeter-test
  friendly_name: watermeter-test
  on_boot: 
    then:
      - lambda: |-
          id(camera).add_image_callback([](std::shared_ptr<esp32_camera::CameraImage> image) {
            if (image->was_requested_by(esp32_camera::WEB_REQUESTER)) {
              id(image_data).length = image->get_data_length();
              id(image_data).data = image->get_data_buffer();
              ESP_LOGD("main", "got requested image, len %d", id(image_data).length);
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
    key: "REPLACE THIS!!"

ota:
  password: "REPLACE THIS!!"

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

  # Enable fallback hotspot (captive portal) in case wifi connection fails
  ap:
    ssid: "Watermeter-Test Fallback"
    password: "REPLACE THIS!!"

captive_portal:

# Just loading dependencies, will issue request manually via HTTPClient
http_request:

globals:
  - id: image_data
    type: esp32_camera::CameraImageData

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

web_server:
  port: 80

text:
  - platform: template
    id: digitizer_url
    name: "Digitizer URL"
    optimistic: true
    mode: text
    restore_value: true

number:
  - platform: template
    id: digitizer_interval
    name: "Digitizer interval (seconds)"
    min_value: 10
    max_value: 3600
    step: 10
    initial_value: 60
    optimistic: true
    restore_value: true

interval:
  - interval: 1sec
    then:
      if: 
        condition:
          not: 
            script.is_running: digitize
        then: 
          - script.execute: digitize    

script:
  - id: digitize
    then:
      - light.turn_on: 
          id: onboard_led
          transition_length: 0s
          brightness: 80%
      - delay: 5s
      - lambda: id(camera).request_image(esp32_camera::WEB_REQUESTER);
      - wait_until:
          condition:
            lambda: return id(image_data).length > 0;
      - lambda: |-
          WiFiClient wifiClient;
          WiFiClientSecure wifiClientSecure;
          wifiClientSecure.setInsecure();
          HTTPClient http;

          http.setConnectTimeout(1000);
          http.setTimeout(3000);

          std::string url = id(digitizer_url).state;

          if (url.rfind("https://", 0) == 0) {
            http.begin(wifiClientSecure, url.c_str());
          } else {
            http.begin(wifiClient, url.c_str());
          }

          int http_code = http.POST(id(image_data).data, id(image_data).length);

          ESP_LOGD("HTTPClient", "completed; URL: %s; Code: %d", url.c_str(), http_code);

          http.end();
      - lambda: id(image_data) = {};
      - light.turn_off: 
          id: onboard_led
          transition_length: 0s
      - delay: !lambda |-
          return id(digitizer_interval).state * 1000;
```
