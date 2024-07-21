import paho.mqtt.client as mqtt
import csv
import os
import requests
import time

mqttBroker = "test.mosquitto.org"
port = 1883

temp_sp = 2  # Desired temperature
humidity_sp = 1
 # Desired humidity

# Function to parse the plan from the Flask response
def parse_plan_response(plan_response):
    if not plan_response:
        print("No plan found in the response")
        return []
    print("The output of solver is", plan_response)
    lines = plan_response.splitlines()
    actions = []
    for line in lines:
        action = line.strip().split()[0]
        action = action.strip('()')
        actions.append(action)
    print("Parsed actions:", actions)
    return actions

# Function to send PDDL files and get the plan from the Flask API
def send_pddl_files_and_get_plan(domain_file_path, problem_file_path):
    url = 'http://127.0.0.1:5000/plan' 
    with open(domain_file_path, 'rb') as domain_file, open(problem_file_path, 'rb') as problem_file:
        files = {
            'domain': domain_file,
            'problem': problem_file
        }
        response = requests.post(url, files=files)
        if response.status_code == 200:
            result = response.json()
            print("Full API Response:", result)
            plan = result.get('plan')
            return plan
        else:
            print(f"Error: {response.json().get('error')}")
            return None

# Updated function to run the planner and parse the plan
def run_planner(domainname, problem):
    plan_response = send_pddl_files_and_get_plan(domainname, problem)
    actions = parse_plan_response(plan_response)
    return actions

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("climateControl")
    client.subscribe("setPoint") #########***********##########

def on_message(client, userdata, message):

    global temp_sp  #########***********##########

    topic = message.topic
    if topic == "setPoint":  #########***********##########
        temp_sp = float(message.payload.decode("utf-8"))  #########***********##########
        print(f"Updated temperature set point to {temp_sp}")  #########***********##########
        return  #########***********##########

    excel_data = {}
    s = str(message.payload.decode("utf-8"))
    print("Received message: ", s)
    payload_data = eval(s)
    print(payload_data)
    excel_data = {'Time': None, 'Temperature': None, 'Humidity': None, 'co': None}
    
    if 'Time' in payload_data and payload_data['Time'] is not None:
        excel_data['Time'] = payload_data['Time']
    if 'Temperature' in payload_data and payload_data['Temperature'] is not None:
        excel_data['Temperature'] = payload_data['Temperature']
    if 'Humidity' in payload_data and payload_data['Humidity'] is not None:
        excel_data['Humidity'] = payload_data['Humidity']
    if 'co' in payload_data and payload_data['co'] is not None:
        excel_data['co'] = payload_data['co']

    # Write data to CSV
    file_path = '/Users/neeharannavaram/Desktop/IOT/sensor/IOT_DATA1.csv'
    write_header = not os.path.exists(file_path) or os.path.getsize(file_path) == 0

    with open(file_path, 'a', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        if write_header:
            writer.writerow(['Time', 'Temperature', 'Humidity', 'CO2'])
        writer.writerow([excel_data['Time'], excel_data['Temperature'], excel_data['Humidity'], excel_data['co']])

    # Generate and run PDDL files
    domain_file_path = '/Users/neeharannavaram/Desktop/IOT/sensor/tempHum/climateDomain.pddl'
    problem_file_path = '/Users/neeharannavaram/Desktop/IOT/sensor/tempHum/climateProblem.pddl'
    
    with open(problem_file_path, 'w') as f:
        f.write(f"""
(define (problem ClimateProblem)
    (:domain climate)

    (:objects
        temp_high temp_low temp_ambient - temp
        hum_high hum_low hum_ambient - hum
        f_high f_low f_none - sensor
        h_high h_low h_none - sensor
    )

    (:init
        ; Temperature initial state
        (isTempHigh {'temp_high' if excel_data['Temperature'] > temp_sp else 'temp_low'})
        (isTempSensHigh {'f_high' if excel_data['Temperature'] > temp_sp else 'f_low'})
        (isTempLow {'temp_low' if excel_data['Temperature'] <= temp_sp else 'temp_high'})
        (isTempSensLow {'f_low' if excel_data['Temperature'] <= temp_sp else 'f_high'})

        ; Humidity initial state
        (isHumHigh {'hum_high' if excel_data['Humidity'] > humidity_sp else 'hum_low'})
        (isHumSensHigh {'h_high' if excel_data['Humidity'] > humidity_sp else 'h_low'})
        (isHumLow {'hum_low' if excel_data['Humidity'] <= humidity_sp else 'hum_high'})
        (isHumSensLow {'h_low' if excel_data['Humidity'] <= humidity_sp else 'h_high'})
    )

    (:goal
        (and
            ({"off_fan f_high" if excel_data['Temperature'] > temp_sp else "on_fan f_low"})
            ({"on_humidifier h_low" if excel_data['Humidity'] <= humidity_sp else "off_humidifier h_high"})
        )
    )
)
        """)


    action = {} # to store the actions from the run planner    
    actions = run_planner(domain_file_path, problem_file_path)


    print("Actions to be performed:", actions)
    #action['temp_action'] = actions[1]
    #action['hum_action'] = actions[0]

    #new change#####################################
    substring1 = "humidifier"
    #substring2 = "fan"
    action['temp_setpoint'] = temp_sp

    if substring1 in actions[0]:
        action['hum_action'] = actions[0]
        action['temp_action'] = actions[1]
    else:
        action['hum_action'] = actions[1]
        action['temp_action'] = actions[0]




    print("============", action['temp_action'])
    print("============", action['hum_action'])

    mqtt_payload = str(action)
    print("Publishing:", mqtt_payload)
    client.publish("climateControl_PDDL", mqtt_payload)
    print("Just published " + mqtt_payload + " to Topic climateControl_PDDL")
    

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqttBroker, port)
client.loop_forever()



