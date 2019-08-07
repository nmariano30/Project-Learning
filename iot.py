from base64 import b64encode, b64decode
from hashlib import sha256
from urllib import quote_plus, urlencode
from hmac import HMAC
import dht11
import RPi.GPIO as GPIO
import requests
import json
import time
import datetime

# Define GPIO

Temp_Sensor = 17

# SENSOR_DEVICE_ID = 'YOUR_DEVICE_ID'
URI = 'MyIoTHubLearning.azure-devices.net'
KEY = '+GsZCwKsColNzv2KqJISh+DYHz8mF53CVM5mmBd1l3s='
IOT_DEVICE_ID = 'RaspberryPi'
POLICY = 'iothubowner'

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

def generate_sas_token():
    expiry = 3600
    ttl = time.time() + expiry
    sign_key = "%s\n%d" % ((quote_plus(URI)), int(ttl))
    signature = b64encode(HMAC(b64decode(KEY), sign_key, sha256).digest())

    rawtoken = {
        'sr' : URI,
        'sig': signature,
        'se' : str(int(ttl))
    }
    rawtoken['skn'] = POLICY
    return 'SharedAccessSignature ' + urlencode(rawtoken)

def main():
    # Main program block
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbers
    instance = dht11.DHT11(pin=Temp_Sensor)
    token = generate_sas_token()

    # Initialise display

    while True:
        # get DHT11 sensor value
        result = instance.read()
        # Send some test

        if result.is_valid():
            message = { "Last valid input: " + str(datetime.datetime.now()),
                        "Temperature: %d C" % result.temperature,
                        "Temperature: %d F" % ((result.temperature * 9 / 5) + 32),
                        "Humidity: %-3.1f %%" % result.humidity
                        }

        data = json.dumps(message)
        print(data)
        send_message(token, message)
        time.sleep(30)


def send_message(token, message):
    url = 'https://{0}/devices/{1}/messages/events?api-version=2016-11-14'.format(URI, IOT_DEVICE_ID)
    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }

if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:

        GPIO.cleanup()
