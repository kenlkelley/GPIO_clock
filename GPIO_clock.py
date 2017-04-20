import RPi.GPIO
import time
import logging, logging.config
DISABLE_EXISTING_LOGGERS = True

GPIO_BUTTON=26
BUTTON_PRESSED = False
GPIO_SECS = [2, 3, 4, 14, 15, 18]
GPIO_MINS = [21, 20, 16]

#Change the status of the gpioref LED. If off, switch on. If on, switch off.
def led_toggle(gpioref):
    led_status = RPi.GPIO.input(gpioref)
    RPi.GPIO.setup(gpioref, RPi.GPIO.OUT)
    led_status = led_status ^ True
    RPi.GPIO.output(gpioref, led_status)
    return led_status

#Turn gpioref LED off
def led_off(gpioref):
    RPi.GPIO.setup(gpioref, RPi.GPIO.OUT)
    RPi.GPIO.output(gpioref, False)
    return 

#Turn gpioref LED on
def led_on(gpioref):
    RPi.GPIO.setup(gpioref, RPi.GPIO.OUT)
    RPi.GPIO.output(gpioref, True)
    return 

#This callback function is triggered by a GPIO event (falling edge)
#Oddly it gets triggered on first push (wait_for_edge) when logging.INFO but
#not when logging.DEBUG
def button_pressed(gpioref):
    if minute+second == 0:
        logging.info("Start. Press to Mark, Ctrl-C to end")
    else:    
        logging.info("Mark " + str(minute) + ":" + str(second))
    quit


if __name__ == "__main__":

# Create a logger using the config file. False doesn't disable existing loggers (in other modules)
#    logging.config.fileConfig("logging.conf",None,DISABLE_EXISTING_LOGGERS)
    
# This simple configuration creates a root logger and specifies some basic control
# They have no effect otherwise, since the root logger will already be configured
    LOGGING_LEVEL=logging.INFO
    logging.basicConfig(level=LOGGING_LEVEL,
                format='%(asctime)s -- %(message)s',
                datefmt='%H:%M:%S')
    
    RPi.GPIO.setwarnings(False)
    RPi.GPIO.setmode(RPi.GPIO.BCM)

# Set the button as an input device
    RPi.GPIO.setup(GPIO_BUTTON, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)

# Initialize the LEDs and turn them all off (they should be already)
    for gpio_id in GPIO_MINS:
        led_off(gpio_id)
    for gpio_id in GPIO_SECS:
            led_off(gpio_id)

    minute = 0
    second = 0

    logging.info("Press button to start stopwatch")
    RPi.GPIO.wait_for_edge(GPIO_BUTTON, RPi.GPIO.FALLING)
    RPi.GPIO.remove_event_detect(GPIO_BUTTON)
    RPi.GPIO.add_event_detect(GPIO_BUTTON, RPi.GPIO.BOTH, button_pressed, 300)

    try:
        while minute <= 7:
            logging.debug(str(minute) + ":" + str(second))
            while second <= 59:
                time.sleep(1)
                second=second + 1
                logging.debug(str(minute) + ":" + str(second))
                for gpio_id in GPIO_SECS:
                    led_lit = led_toggle(gpio_id)
                    logging.debug("    -  Led " + str(gpio_id) + ":" + str(led_lit))
                    if led_lit == True: break

            second = 0
            #At end of each minute, turn all remaining "second" leds off 
            for gpio_id in GPIO_SECS:
                led_off(gpio_id)

            minute = minute + 1    
            for gpio_id in GPIO_MINS:
                led_lit = led_toggle(gpio_id)
                logging.debug("    -  Led " + str(gpio_id) + ":" + str(led_lit))
                if led_lit == True: break
            

    except KeyboardInterrupt:
        pass
    
    finally:
        for gpio_id in GPIO_SECS:
            led_off(gpio_id)
        for gpio_id in GPIO_MINS:
            led_off(gpio_id)
        RPi.GPIO.cleanup       # clean up GPIO on CTRL+C exit  
        logging.info("Stop at " + str(minute) + ":" + str(second))
    
