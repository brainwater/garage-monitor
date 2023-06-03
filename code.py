

import time
import ssl
import json
#import alarm
import board
import digitalio
#import socketpool
import socket
#import wifi
import adafruit_minimqtt.adafruit_minimqtt as MQTT
# pylint: disable=no-name-in-module,wrong-import-order
try:
    from secrets import secrets
except ImportError as ex:
    print("Secrets are kept in secrets.py, please add them there!")
    raise ex

PUBLISH_DELAY = 10
EXPIRE_DELAY = 20 # How long since a sensor update before the sensor is declared offline
SLEEP_TIME = 1
topic = "homeassistant/binary_sensor/garagedoor/"
CONFIG_TOPIC = topic + "config"
STATE_TOPIC = topic + "state"
#MQTT_TOPIC = "homeassistant/sensor/"

print(dir(board))
garageDoorIn = digitalio.DigitalInOut(board.D17)
def prep():
    garageDoorIn.direction = digitalio.Direction.INPUT
    garageDoorIn.pull = digitalio.Pull.UP
def publish_sensor(mqtt_client):
    payload = {
        "name": "Garage Door",
        "device_class": "door",
        "payload_on": "ON",
        "payload_off": "OFF",
        "state_topic": STATE_TOPIC,
        "expire_after": EXPIRE_DELAY,
        "unique_id": "garagedoor",
        "value_template": "{{ value_json.state }}"}
    mqtt_client.publish(CONFIG_TOPIC, json.dumps(payload))

def run():
    prep()
    # Set up a MiniMQTT Client
    mqtt_client = MQTT.MQTT(
        broker=secrets["mqtt_broker"],
        port=secrets["mqtt_port"],
        username=secrets["mqtt_username"],
        password=secrets["mqtt_password"],
        socket_pool=socket,
        ssl_context=ssl.create_default_context(),
    )
    mqtt_client.connect()
    publish_sensor(mqtt_client)
    lastupdate = 0
    while True:
        if time.monotonic() > lastupdate + PUBLISH_DELAY:
            lastupdate = time.monotonic()
            if garageDoorIn.value:
                state = "ON"
                #print("ON")
            else:
                state = "OFF"
                #print("OFF")
            output = {
                "state": state}
            mqtt_client.publish(STATE_TOPIC, json.dumps(output))
            #print("Published state")
        time.sleep(SLEEP_TIME)

while True:
    run()
