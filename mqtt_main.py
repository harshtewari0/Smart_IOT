#code to publish temp data
from grovepi import *
import RPi.GPIO as GPIO
import time
import datetime
#from dateutil.relativedelta import *
#from dateutil.easter import *
#from dateutil.rrule import *
#from dateutil.parser import *
from math import isnan
#import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import threading
from random import randrange
import grovepi
from relay_lib_seeed import *



####My implementation

broker = "test.mosquitto.org"
port = 1883


dht_sensor_port = 7
dht_sensor_type = 0

###for motor########
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


def co2():
    payload_data = None
    payload_data = {}
    time.sleep(2)
    payload_data ['co'] = 426
    print("CO2 is",payload_data ['co'])
    return payload_data
    
def tempHum():
    payload_data = None
    payload_data = {}
    time.sleep(2)
    temp=0
    hum=0
    [temp1,hum1] = dht(dht_sensor_port,dht_sensor_type)  
    if math.isnan(temp1) or  math.isnan(hum1) or temp1 <0 :
        temp = 24.0
        hum = 43.0 
        print("VALUE IS NAN")
    else:
        temp = temp1
        hum = hum1
        #print(temp)
        #print(hum)

    payload_data ['Temperature'] = temp       # Temperature sensed value stored in variable
    print("TEMP IS",payload_data ['Temperature'])
    #time.sleep(1)

    payload_data ['Humidity'] = hum             # Humidity sensed value stored in variable
    print("HUM IS",payload_data ['Humidity'])

    return payload_data

def MQTTDataSend():  
    print("Data sending started")
    while True:
        payload_data = {}
        '''
        timeStamp = time.time()
        tm = datetime. datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H: %M:%S')
        payload_data['Time'] = tm
        '''
        now = datetime.datetime.now()
        tm = now.strftime('%Y-%m-%d %H:%M:%S')
        payload_data['Time'] = tm
        
        payload_dht = tempHum()
        payload_co = co2()
        if payload_dht is not None:
            if 'Temperature' in payload_dht:
                payload_data['Temperature'] = payload_dht['Temperature']    # Temprature sensor data stored
            if 'Humidity' in payload_dht:
                payload_data['Humidity'] = payload_dht['Humidity']  # Humidity sensor data stored
            if 'co' in payload_co:
                payload_data['co'] = payload_co['co']

################### to publish data  ###############################

        mqtt_payload = str(payload_data)  #Convert payload_data to string
        client.publish("climateControl", mqtt_payload)                
        print("Just published " + mqtt_payload + " to Topic climateControl")
        time.sleep(5)


#########################actutation functions#####################
    
def humidity_actuation(hum_output):

        if hum_output == 'switchonhumidifier':
            print("Humidifier ON")
            relay_on(2) #controls the relay to the humidifier fan
        else:
            print("Humidifier OFF")
            relay_off(2)
        hum_output = None
        
def temperature_actuation(temp_output,set_point):
    
    if temp_output == 'switchonfan':
        print("Heater ON")
        
        #######adding motor here############
        
        temp = tempHum()
        temp_difference = set_point - temp['Temperature']
        if  temp_difference >= 10 :
            print("Heater is on full")
            p.ChangeDutyCycle(100)
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.HIGH)
        elif 5 <= temp_difference < 10 :
            print("Heater is on medium")
            p.ChangeDutyCycle(50)
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.HIGH)
                        
        elif 1 <= temp_difference < 5 :
            print("Heater is on low")
            p.ChangeDutyCycle(25)
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.HIGH)
            
        
    else:
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.LOW)
        print("Heater OFF")


###############receieving data from laptop###########################
def on_message(client, userdata, messege):
    action = str(messege.payload.decode("utf-8"))
    print("recieved messege:++++++++++++++++++++++++++++++++++++", action)
    payload_pddl = eval(action)
    
################ Actuation code #################################
    
    if 'hum_action' in payload_pddl and payload_pddl['hum_action'] is not None:
        hum_output = payload_pddl['hum_action']
    
    if 'temp_action' in payload_pddl and payload_pddl['temp_action'] is not None:
        temp_output = payload_pddl['temp_action']
        set_point = payload_pddl['temp_setpoint']
    
    
    print("-------------------------------", set_point)
    humidity_actuation(hum_output)
    temperature_actuation(temp_output, set_point)    



##################################MQTT ###################################
            
def on_connect(client, userdata, flags, rc):
    print("Connected with the result code" + str(rc))
    client.subscribe("climateControl_PDDL")

def MQTTDataRecieve():
    #print("Connected to the broker")
    #client.subscribe("climateControl_PDDL")
    client.loop_forever()
    
try: 
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port, 60)

    t1 = threading.Thread(target = MQTTDataSend)
    t2 = threading.Thread(target = MQTTDataRecieve)
    t1.start()
    t2.start()
except (IOError, TypeError) as e:
    grovepi.digitalWrite(led,0)
except KeyboardInterrupt:
    print("Program terminated by user.")


