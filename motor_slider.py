import RPi.GPIO as GPIO
from time import sleep
import paho.mqtt.client as mqtt
import json

# GPIO setup
in1 = 24
in2 = 23
en = 25

GPIO.setmode(GPIO.BCM)
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(en, GPIO.OUT)
GPIO.output(in1, GPIO.LOW)
GPIO.output(in2, GPIO.LOW)
p = GPIO.PWM(en, 1000)
p.start(25)

# Initialize global variable for temperature
temperature = None

# MQTT setup
broker = "test.mosquitto.org"
topic = "climate_control"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(topic)

def on_message(client, userdata, message):
    global temperature
    try:
        payload = message.payload.decode("utf-8")
        data = json.loads(payload)  # Convert JSON string to dictionary
        temperature = data.get("temperature", 0)
        print("Received message: {}".format(payload))
        print("Extracted temperature: {}".format(temperature))
    except Exception as e:
        print("Error processing message: {}".format(e))

# Setup MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to the broker
client.connect(broker, 1883, 60)

# Start the MQTT client loop
client.loop_start()

try:
    while True:
        if temperature is not None:
            try:
                temp = int(temperature)
                if 25 <= temp < 30:
                    print("medium")
                    p.ChangeDutyCycle(50)
                    GPIO.output(in1, GPIO.LOW)
                    GPIO.output(in2, GPIO.HIGH)

                elif 20 <= temp < 25:
                    print("low")
                    p.ChangeDutyCycle(25)
                    GPIO.output(in1, GPIO.LOW)
                    GPIO.output(in2, GPIO.HIGH)

                    print("Motor stopped or moving in another direction")
                elif temp >= 30:
                    print("high")
                    p.ChangeDutyCycle(100)
                    GPIO.output(in1, GPIO.LOW)
                    GPIO.output(in2, GPIO.HIGH)
                    print("Motor stopped or moving in the opposite direction")
                else:
                    print("Temperature too low")
                    p.ChangeDutyCycle(15)
                    GPIO.output(in1, GPIO.LOW)
                    GPIO.output(in2, GPIO.LOW)
                    print("Motor stopped")
            except ValueError:
                print("Invalid temperature value received")
                
        sleep(1)  # Adjust sleep time as needed

except KeyboardInterrupt:
    print("Exiting...")	
    GPIO.cleanup()
finally:
    # Cleanup GPIO and MQTT client
    p.stop()
    GPIO.cleanup()
    client.loop_stop()
    client.disconnect()
