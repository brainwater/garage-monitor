import json
import ssl
import socket
import adafruit_minimqtt.adafruit_minimqtt as MQTT

def publish_sensor(mqtt_client, name, device_class, unique_id, config_topic, state_topic, expire_delay):
    payload = {
        "name": name,
        "device_class": device_class,
        "payload_on": "ON",
        "payload_off": "OFF",
        "state_topic": state_topic,
        "expire_after": expire_delay,
        "unique_id": unique_id,
        "value_template": "{{ value_json.state }}"}
    mqtt_client.publish(config_topic, json.dumps(payload))

def initMqtt(mqtt_client):
    try:
        mqtt_client.connect()
        publish_sensor(mqtt_client)
        return True
    except Exception as ex:
        print("Failed to initialize mqtt, will retry")
        print(ex)
        return False

def advertiseAndPublishOnce(secrets, value, name="Garage Door", device_class="door", unique_id="garagedoor", mqtt_topic="homeassistant/binary_sensor/garagedoor", expire_delay=60*3):
    state_topic = mqtt_topic.rstrip("/") + "/state"
    config_topic = mqtt_topic.rstrip("/") + "/config"
    mqtt_client = MQTT.MQTT(
        broker=secrets["mqtt_broker"],
        port=secrets["mqtt_port"],
        username=secrets["mqtt_username"],
        password=secrets["mqtt_password"],
        socket_pool=socket,
        ssl_context=ssl.create_default_context(),
    )
    if mqtt_client is None:
        raise Exception("Unable to initialize mqtt client!")
    mqtt_client.connect()
    publish_sensor(mqtt_client, name=name, device_class=device_class, unique_id=unique_id,
                   config_topic=config_topic, state_topic=state_topic, expire_delay=expire_delay)
    mqtt_client.publish(state_topic, json.dumps(value))

if __name__ == "__main__":
    try:
        from secrets import secrets
    except ImportError as ex:
        print("Secrets are kept in secrets.py, please add them there!")
        raise ex
    import board
    import digitalio
    garageDoorIn = digitalio.DigitalInOut(board.D17)
    garageDoorIn.direction = digitalio.Direction.INPUT
    garageDoorIn.pull = digitalio.Pull.UP
    if garageDoorIn.value:
        state = "ON"
    else:
        state = "OFF"
    output = {"state": state}
    advertiseAndPublishOnce(secrets, output)

