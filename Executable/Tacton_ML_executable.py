"""
File: Tacton_ML_executable.py
Author: Dylan Turland Cowell
Date Created: 11-May-2024
Description: This code is designed to be used in the OpenMV IDE with the following hardware:
    Nicla Vision
    PCA9546A multiplexer
    DRV2605L motor driver x3
    Seeed Studio haptic motor x3
    Tactile button (and pull-up resistor) to pin D0
"""

from pyb import I2C, Pin, Timer
import machine
import sensor
import time
import tf
from vl53l1x import VL53L1X
import math
import motor
import uasyncio



# Define I2Cmotor and ToF comms
i2c = I2C(1, I2C.MASTER)
tof = VL53L1X(machine.I2C(2))

# Set up motor for each multiplexer output
multiplexer_outputs = [0x03, 0x06, 0x09]
for output in multiplexer_outputs:
    motor.select_multiplexer(0x70, output)
    motor.initialise_motor()
    motor.selectLibrary(0)
    motor.setMode(0x00)
    motor.useERM()


# Set up camera
sensor.reset()                      # Reset and initialise camera
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565
sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
sensor.set_windowing((240, 240))    # Set 240x240 window.
sensor.skip_frames(time=2000)       # Let the camera adjust.

# Initialise buttin and set state
button = Pin("D0", Pin.IN, Pin.PULL_UP)
state = False       # Initial state

# Flag to track whether tacton() is currently running
tacton_running = False
last_tacton_time = 0

# Set variables
smoothing_values = []
clicking = False    # Flag to indicate if a click operation is in progress


async def handle_button_press():
    """
    Coroutine to continously monitors the logic to the 'D0' pin. Global varaible 'state' is adjusted
    depending on the button press, which adjusts which co-routines run in the event loop.
    """

    global state
    while True:
        if button.value() == 0:                  # Button is pressed (since it's pulled-up)
            start_time = time.ticks_ms()         # Record the start time of button press
            while button.value() == 0:           # Keep checking if button is still pressed
                await uasyncio.sleep_ms(10)      # Check every 10ms
                                                 # Button released, calculate press duration
            press_duration = time.ticks_diff(time.ticks_ms(), start_time)
            if press_duration < 500:             # Short press
                print("Short press detected!")
                state = not state                # Toggle the state
                print("State changed to:", state)
                await uasyncio.sleep(0.5)
            else:                                # Long press - functionality not used in current design
                print("Long press detected!")

        await uasyncio.sleep_ms(10)              # Debouncing delay to handle button press


async def tacton(delay, detected_objects):
    """
    Coroutine to execute tactons based on detected objects. Tactons are executed on the detection of
    classes, which a hierachy of hazard > social > practical. These tactons are hard coded in this current
    version due to the program detecting only 5 objects.

    Args:
        delay (int): The delay between consecutive tactons in milliseconds. Adjustable 'detection_objects' function.
        detected_objects (list): A list of detected objects.

    """
    global tacton_running
    global last_tacton_time


    # Define a dictionary mapping objects to their respective waveforms and motor selection codes
    object_details = {
            "car": {"waveform": 84, "priority": 1, "motor_selection": 0x06},  # Hazard
            "dog": {"waveform": 85, "priority": 1, "motor_selection": 0x06},  # Hazard
            "person": {"waveform": 86, "priority": 2, "motor_selection": 0x09},  # Social
            "chair": {"waveform": 87, "priority": 3, "motor_selection": 0x70},  # Practical
            "sink": {"waveform": 88, "priority": 3, "motor_selection": 0x70}  # Practical
        }

    current_time = time.ticks_ms()
    if current_time - last_tacton_time >= delay: # Control frequencies of tactons (5 seconds)
        if detected_objects:
            # Initialise variables to store the highest priority object and its details
            highest_priority_object = None
            highest_priority_details = None

            # Iterate through the detected objects to find the highest priority object
            for obj in detected_objects:
                if obj in object_details:
                    # Update the highest priority object if it has not been set or if it has higher priority
                    if (highest_priority_object is None or
                        object_details[obj]["priority"] < object_details[highest_priority_object]["priority"]):
                        highest_priority_object = obj
                            highest_priority_details = object_details[obj]

            # Check if a highest priority object was found
            if highest_priority_details:
                # Select the motor based on the class of detection and execute tacton
                motor.select_multiplexer(0x70, highest_priority_details["motor_selection"])

                tacton_running = True
                motor.go()
                motor.setWaveform(0, highest_priority_details["waveform"])  # Use waveform number for the highest priority object
                await uasyncio.sleep(1) # Allow tacton to finish executing
                motor.stop()
                tacton_running = False
                last_tacton_time = current_time

     await uasyncio.sleep(0.05) # Leave short time gap for co-routines to be checked


async def detect_objects():
    """
    Coroutine to detect objects FOMO MobileNet model.

    Continuously captures images from the camera and detects objects in them.
    If objects are detected and the tacton function is not currently running, it starts a new tacton task.

    """
    min_confidence = 0.6
    labels, net = tf.load_builtin_model("fomo_face_detection")

    while True:
        if not state:
            img = sensor.snapshot()

            for i, detection_list in enumerate(
                net.detect(img, thresholds=[(math.ceil(min_confidence * 255), 255)])
            ):
                if i == 0:
                    continue  # background class
                if len(detection_list) == 0:
                    continue  # no detections for this class?

                print("********** %s **********" % labels[i])

                global tacton_running
                if tacton_running == False:  # Check if tacton() is not running
                    await uasyncio.sleep(0)  # Allow other tasks to run
                    uasyncio.create_task(tacton(5000, detection_list))  # Start tacton() in the background

        await uasyncio.sleep(0.05) # Leave short time gap for co-routines to be checked


async def click(period):
    """
    Coroutine executes a 'click' from centre motor to alert user of distances.

    Args:
            period (int): The duration of the motor tacton in milliseconds.
    """

    global clicking
    global current_wait_time
    motor.select_multiplexer(0x70, 0x06) # Use only centre motor

    if clicking:    # Check if a click operation is already in progress
        if period < current_wait_time:  # If new period is shorter than remaining wait time
            current_wait_time = period  # Update wait time
        return

    clicking = True                     # Set the flag to indicate that a click operation is in progress
    current_wait_time = period

    # Execute 'motor tacton'click' on center motor
    motor.setMode(0x00)
    motor.go()
    motor.setWaveform(0, 17)

    # Wait for the specified period
    while current_wait_time > 0:
           await uasyncio.sleep_ms(10)
           current_wait_time -= 10

    motor.stop()
    clicking = False  # Reset the flag after click operation is completed


async def sensor_reading():
    """
    Coroutine to read sensor data continuously and trigger motor tactons.
    """

    global smoothing_values
    while True:
        if state:
            tof_value = tof.read()          # Read ToF sensor
            period = calc_period(tof_value) # Calculate period
            uasyncio.create_task(click(period)) # Create task to run coroutine concurrently - sensor and motor run together
        await uasyncio.sleep_ms(10)         # Leave short time gap for co-routines to be checked


def calc_period(value):
    """
    Calculate the period between distance tactons given ToF readings.
    Distance of 4-0 metres maps to a period of 5-0.1 seconds

    Args:
        value (int): The ToF sensor reading.

    Returns:
        int: The calculated period.

    """

    global smoothing_values
    smoothing_values.append(value)
    smoothing_values = smoothing_values[-50:]   # Smoothing introduces a short delay in change of distances but also mitigates sudden changes which do not pose a threat
    average_value = sum(smoothing_values) / len(smoothing_values)

    # Apply linear interpolation to map the value to the new range (100-5000)
    new_value = round(((value - 200) / (4000 - 200)) * (3000 - 100) + 100)
    new_value = max(100, min(new_value, 3000))
    return new_value


async def main():
    """
    Main coroutine to run the event loop, executing multiple tasks concurrently.
    """

    await uasyncio.gather(detect_objects(), sensor_reading(), handle_button_press())

loop = uasyncio.get_event_loop() # Retrieve event loop
loop.run_until_complete(main())


"""

༼ つ ಥ_ಥ ༽つ  ~ Cheers for giving it a read!

"""
