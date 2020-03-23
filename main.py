# python3
# pip install paho-mqtt


import paho.mqtt.client as mqtt #import the client1

BROKER_ADDRESS = "10.10.10.30"
BROKER_USER = "mqtt_user"
BROKER_PASS = "mqtt_pass"

print("Starting HomeAssistant MQTT LPD8806 Broker")
#broker_address="iot.eclipse.org" #use external broker
CLIENT = mqtt.Client() #create new instance
CLIENT.username_pw_set(BROKER_USER, BROKER_PASS)

print("Connecting...", end="")
CLIENT.connect(BROKER_ADDRESS) #connect to broker
print("Done")

print("Setting state to OFF")
CLIENT.publish("gaming/backlight/light/status", "OFF") #publish
