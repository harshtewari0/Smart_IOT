from grovepi import *
import time
import sys
import os
import re
from relay_lib_seeed import *

from smtplib import SMTP_SSL as SMTP       # this invokes the secure SMTP protocol (port 465, uses SSL)
# from smtplib import SMTP                  # use this for standard SMTP protocol   (port 25, no encryption)
# old version
# from email.MIMEText import MIMEText
from email.mime.text import MIMEText

SMTPserver = 'smtp.gmail.com'
sender = 'harshtewari12@gmail.com'
destination = ['harshtewari21@gmail.com']

USERNAME = "harshtewari12@gmail.com"
PASSWORD = "witd ucwf dqkn zkek"
# Define the pins
buzzer_pin = 2  # Port for buzzer
led = 3         # Port for LED
button = 4      # Port for Button
pir_sensor = 8
led1 = 5


pinMode(button, "INPUT")
pinMode(buzzer_pin, "OUTPUT")
pinMode(led, "OUTPUT")
pinMode(led1,"OUTPUT")
pinMode(pir_sensor,"INPUT")

content = """\
Fire has been detected in room number 28.
"""

subject = "FIRE ALERT!!"



def main():
    count = 0
    while True:
        try:
            button_status = digitalRead(button)
            motion_det = digitalRead(pir_sensor)
        
            if button_status:
                digitalWrite(buzzer_pin, 1)
                digitalWrite(led, 1)
                relay_on(1)
                print("----------", count)
                if count == 0:
                    
                    #try:
                        msg = MIMEText(content, "plain")
                        msg['Subject'] = subject
                        msg['From'] = sender  # some SMTP servers will do this automatically, not all

                        conn = SMTP(SMTPserver)
                        conn.set_debuglevel(False)
                        conn.login(USERNAME, PASSWORD)
                        
                        try:
                            conn.sendmail(sender, destination, msg.as_string())
                        finally:
                            print("connection quittttttt")
                            conn.quit()
                        count += 1
                    #except Exception as e:
                        #print("Error: unable to send email. Exception: " + str(e))
                    
            else:
                digitalWrite(buzzer_pin, 0)
                digitalWrite(led, 0)
                relay_off(1)
                count = 0
            if motion_det:
                digitalWrite(led1, 1)
            else:
                digitalWrite(led1, 0)
            time.sleep(1)
        except KeyboardInterrupt:
                digitalWrite(led1, 0)
                digitalWrite(led, 0)
                digitalWrite(buzzer_pin, 0)
                relay_off(1)
if __name__ == "__main__":
    main()
        
