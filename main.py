#!/usr/bin/python
#
# Reqired installs:
#   pip install paho-mqtt
#   Follow: https://github.com/longjos/RPi-LPD8806
#     git clone https://github.com/adammhaile/RPi-LPD8806.git 
#     cd RPi-LPD8806
#     python setup.py install
#
# In configuration.yaml, set the following
#  - platform: mqtt
#    name: "Gaming Computer Backlight"
#    state_topic: "gaming/backlight/light/status"
#    command_topic: "gaming/backlight/light/switch"
#    brightness_state_topic: "gaming/backlight/brightness/status"
#    brightness_command_topic: "gaming/backlight/brightness/set"
#    rgb_state_topic: "gaming/backlight/rgb/status"
#    rgb_command_topic: "gaming/backlight/rgb/set"
#    state_value_template: "{{ value_json.state }}"
#    brightness_value_template: "{{ value_json.brightness }}"
#    rgb_value_template: "{{ value_json.rgb | join(',') }}"
#    qos: 0
#    payload_on: "ON"       
#    payload_off: "OFF"               
#    optimistic: false  

# Python 2.7/3 compatibility
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)
try:
    from future_builtins import ascii, filter, hex, map, oct, zip
except:
    pass

import paho.mqtt.client as mqtt # import the mqtt client
from raspledstrip.ledstrip import * # import RGB stuff
import json # config parsing
import sys
import os

CONFIG_FILE = "%s/config.json" % (os.path.dirname(os.path.realpath(__file__)))
try:
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
except:
    config = {}


BROKER_ADDRESS = config.get("BrokerAddress", None)
BROKER_USER = config.get("BrokerUser", None)
BROKER_PASS = config.get("BrokerPass", None)
CLIENT_NAME = config.get("ClientName", None)
PREFIX = config.get("TopicPrefix", None)
SUBSCRIBE_TOPICS = ["%s/#" % (PREFIX)]

STATE_TOPIC = "%s/light/status" % (PREFIX)
COMMAND_TOPIC = "%s/light/switch" % (PREFIX)

BRIGHTNESS_STATE_TOPIC = "%s/brightness/status" % (PREFIX)
BRIGHTNESS_COMMAND_TOPIC = "%s/brightness/set" % (PREFIX)

RGB_STATE_TOPIC = "%s/rgb/status" % (PREFIX)
RGB_COMMAND_TOPIC = "%s/rgb/set" % (PREFIX)

ON = "ON"
OFF = "OFF"

NUM_LEDS = config.get("NumLeds", 56)

# Verify config
if BROKER_ADDRESS is None:
    print("No Broker Address")
    sys.exit(1)
if PREFIX is None:
    print("No Topic Prefix")
    sys.exit(1)


print ("Subscribing to %s" % (SUBSCRIBE_TOPICS))
print ("STATE_TOPIC: %s" % (STATE_TOPIC))
print ("COMMAND_TOPIC: %s" % (COMMAND_TOPIC))
print ("BRIGHTNESS_STATE_TOPIC: %s" % (BRIGHTNESS_STATE_TOPIC))
print ("BRIGHTNESS_COMMAND_TOPIC: %s" % (BRIGHTNESS_COMMAND_TOPIC))
print ("RGB_STATE_TOPIC: %s" % (RGB_STATE_TOPIC))
print ("RGB_COMMAND_TOPIC: %s" % (RGB_COMMAND_TOPIC))

# #######################
# Class
# #######################
class Light:
    client = None

    # Tracking these for brightness changes. There's probably a way to set brightness without tracking colours but I haven't looked into it much yet
    r = 255
    g = 255
    b = 255
    brightness = 1
    
    def __init__(self, client, num_lights):
        """Provide the mqtt client to publish messages on and the number of lights in LED string"""
        self.client = client
        self.num_lights = num_lights
        self.led = LEDStrip(self.num_lights)

    def turn_on(self, r=None, g=None, b=None, brightness=None):
        """Turns the lights on"""
        print("Got request to turn on the lights on with values: (r=%s, g=%s, b=%s, brightness=%s)" %  (r, g, b, brightness))
        if r is not None:
            self.r = r
        if g is not None:
            self.g = g
        if b is not None:
            self.b = b
        if brightness is not None:
            self.brightness = brightness
        print("Turning on lights on with values: (r=%s, g=%s, b=%s, brightness=%s)" %  (self.r, self.g, self.b, self.brightness))
        self.led.fill(Color(self.r,self.g,self.b, self.brightness))

        self.led.update()
        self.client.publish(STATE_TOPIC, ON) #publish

    def turn_off(self):
        """Turns the lights off"""
        print("Turning the lights off")
        self.led.all_off()
        self.client.publish(STATE_TOPIC, OFF) #publish

    def set_brightness(self, level):
        """Sets the brighness to a certain level"""
        print("Got request to set brightness with level: %s" % (level))
        # Home assistant sets brightness on a scale of 0 to 255
        if level > 0 and level < 255:
            new_level = level / 255
        print("Setting brightness to %s" % (new_level))
        self.turn_on(r=self.r, g=self.g, b=self.b, brightness=new_level)
        self.client.publish(BRIGHTNESS_STATE_TOPIC, level) #publish



# #######################
# MQTT
# #######################

def on_connect(mqtt_client, obj, flags, rc):
    """Debug whether we've connected or not"""
    print("Connected")


def on_message(client, userdata, message):
    """Handles the message"""
    payload = str(message.payload.decode("utf-8"))
    print("message received: %s" % (payload))
    print("message topic: %s" % (message.topic))
    print("message qos: %s" % (message.qos))
    print("message retain flag: %s" % (message.retain))

    if message.topic == COMMAND_TOPIC:
        # We have a command
        if payload == ON:
            light.turn_on()
        if payload == OFF:
            light.turn_off()
    if message.topic == BRIGHTNESS_COMMAND_TOPIC:
        # We have a brighness command
        light.set_brightness(int(payload))
    if message.topic == RGB_COMMAND_TOPIC:
        r,g,b = payload.split(",")
        light.turn_on(r=int(r), g=int(g), b=int(b))

print("Starting HomeAssistant MQTT LPD8806 Broker")
#broker_address="iot.eclipse.org" #use external broker
client = mqtt.Client(CLIENT_NAME) #create new instance
if BROKER_USER is not None and BROKER_PASS is not None:
    client.username_pw_set(BROKER_USER, BROKER_PASS)
client.on_message = on_message #attach function to callback
client.on_connect = on_connect

print("Connecting...", end="")
client.connect(BROKER_ADDRESS) #connect to broker
print("Done")

light = Light(client, NUM_LEDS)

for topic in SUBSCRIBE_TOPICS:
    print("Subscribing to topic", topic)
    client.subscribe(topic)

print("Looping forever")
client.loop_forever() #start the loop
