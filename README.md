# ha-mqtt-lpd8806
Integrates Home Asssitant and LPD8806 LED strips via MQTT

NOTE: My RPi is running a very old version of Rasbian (which I can't upgrade for various reasons). As such, this is running in python 2.7 but should theoretically work on python 3.x.

## Prerequsistes

1. Install `paho-mqtt` using pip:    
    ```
    pip install paho-mqtt
    ```

2. The RPi-LPD8806 package is installed, configured, and working as per https://github.com/longjos/RPi-LPD8806

3. Home Assitant is configured with the MQTT addon and a configured username/password.


## Home Assistant Configuration

Update `configuration.yaml` with a light as per https://www.home-assistant.io/integrations/light.mqtt/#brightness-and-rgb-support. Example:    
```
light
  - platform: mqtt
    name: "Computer Backlight"
    state_topic: "computer/backlight/light/status"
    command_topic: "computer/backlight/light/switch"
    brightness_state_topic: "computer/backlight/brightness/status"
    brightness_command_topic: "computer/backlight/brightness/set"
    rgb_state_topic: "computer/backlight/rgb/status"
    rgb_command_topic: "computer/backlight/rgb/set"
    state_value_template: "{{ value_json.state }}"
    brightness_value_template: "{{ value_json.brightness }}"
    rgb_value_template: "{{ value_json.rgb | join(',') }}"
    qos: 0
    payload_on: "ON"       
    payload_off: "OFF"               
    optimistic: false  
```

## Raspberry Pi configuration

1. Navigate to `/usr/local/bin/`
2. Checkout this repository
    ```
    sudo git clone https://github.com/klagroix/ha-mqtt-lpd8806.git
    cd ha-mqtt-lpd8806/
    ```

2. Create a config.json file within the `ha-mqtt-lpd8806` folder. Replace the variables as needed:
    ```
    {
        "BrokerAddress": "192.168.1.1",
        "BrokerUser": "mqtt_username",
        "BrokerPass": "mqtt_password",
        "ClientName": "BacklightClient",
        "TopicPrefix": "computer/backlight",
        "NumLeds": 56
    }
    ```
3. Run `python main.py`

## Running as a service

NOTE: As stated earlier, I'm on an old OS. This isn't based on systemd. If I had systemd, I'd run something like this https://tecadmin.net/setup-autorun-python-script-using-systemd/

I followed this guide: http://blog.scphillips.com/posts/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/

1. Copy `backlight` from `/usr/local/bin/ha-mqtt-lpd8806/` to `/etc/init.d/`
    ```
    sudo cp /usr/local/bin/ha-mqtt-lpd8806/backlight /etc/init.d/backlight
    ```

2. Edit the permissions:
    ```
    sudo chmod 755 /etc/init.d/backlight.sh
    sudo chmod 755 /usr/local/bin/ha-mqtt-lpd8806/main.py
    ```

3. Execute:
    ```
    sudo update-rc.d backlight.sh defaults
    ```

4. Stop and Start the service as needed
    ```
    sudo service backlight stop
    sudo service backlight start
    ```

## Troubleshooting

Optional: Stop the service above (`sudo service backlight stop`)

Run the script in shell. Debug info is output to STDOUT


## TODO items:
* Add Logging
* Support individually addressable LED applications. Examples:
    * Progress bar
    * VU meter