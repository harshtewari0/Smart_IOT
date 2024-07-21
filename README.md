# Readme for Fire Alert and Climate Control System
## Overview
This project consists of two main systems: a Fire Alert System and a Climate Control System. Both systems are implemented using Python and various libraries to interact with hardware components and MQTT for communication.

## Fire Alert System
The Fire Alert System monitors a room for fire incidents and sends an alert email when a fire is detected. It uses a button and a PIR sensor for detection, and it triggers a buzzer and an LED as visual and auditory alerts.

## Climate Control System
The Climate Control System monitors and controls the temperature and humidity of an environment. It receives data from sensors, writes the data to a CSV file, generates PDDL (Planning Domain Definition Language) files for planning actions, and communicates actions via MQTT.

## Example Usage
- When the button is pressed, the buzzer, LED, and relay will activate.
- An email alert will be sent to the specified destination email address.
- The PIR sensor will activate the second LED if motion is detected.

- Sensor data will be received via MQTT and written to a CSV file.
- PDDL files will be generated based on the sensor data.
- The planner will determine the actions to be taken, such as turning on/off a fan or humidifier, and these actions will be published to an MQTT topic.
- the planner also control the speed of heater based on difference between the set value and actual temperature value
