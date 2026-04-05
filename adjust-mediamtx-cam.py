"""
adjust-mediamtx-cam.py

This script adjusts the gain of a MediaMTX hosted 
camera using it's API to stay just under the defined
TARGET_BRIGHTNESS for the scene.
"""

import cv2
import numpy as np
import requests
import time

# Camera stream URL (replace with your stream source)
STREAM_URL = "rtsp://localhost:8554/cam"
GET_URL = "http://localhost:9997/v3/config/paths/get/cam"
PATCH_URL = "http://localhost:9997/v3/config/paths/patch/cam"

# Define brightness-to-gain mapping parameters
MAX_BRIGHTNESS = 110 # Stop compensating
MIN_BRIGHTNESS = 100 # Begin compensating
INITIAL_GAIN = 1.0
MAX_GAIN = 10 # Stop compensating
UPDATE_INTERVAL = 5 # Seconds

def capture_frame():
    # Capture a frame from the stream
    cap = cv2.VideoCapture(STREAM_URL)
    ret, frame = cap.read()
    cap.release()

    return ret, frame

def get_brightness(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    avg_brightness = np.mean(gray)
    print(f"Average Brightness: {avg_brightness}")

    return avg_brightness

def get_gain():
    # Retrieve current gain
    response = requests.get(GET_URL)
    json = response.json()
    gain = json["rpiCameraGain"]

    print(f"Server gain is {gain}")

    return gain

def update_gain(gain):
    # Send API request to update gain
    payload = {"rpiCameraGain": gain}
    response = requests.patch(PATCH_URL, json=payload)

    return response


def adjust_gain(gain):
    ret, frame = capture_frame()

    if ret:
        brightness = get_brightness(frame)

        if(brightness > MAX_BRIGHTNESS and round(gain, 1) > 1):
            gain = gain - 0.1
            response = update_gain(round(gain,1))
            print(f"Set Gain to {round(gain, 1)}, Response: {response.status_code}")
        elif(brightness < MIN_BRIGHTNESS and round(gain,1) < MAX_GAIN):
            gain = gain + 0.2
            response = update_gain(round(gain,1))
            print(f"Set Gain to {gain}, Response: {response.status_code}")
        else:
            print(f"Gain of {round(gain,1)} unchanged")
    else:
        print("Failed to capture frame")

    return round(gain,1)


if __name__ == '__main__':
    gain = get_gain() or INITIAL_GAIN
    update_gain(gain)

    while True:
        gain = adjust_gain(gain)
        time.sleep(UPDATE_INTERVAL)
