import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.OUT)
out = 21 # GPIO Pin dariSolenoid Door Lock-nya

def solonoid_open(pin):  # Pintu terbuka
    GPIO.output(pin, GPIO.HIGH) 

def solonoid_closed(pin):  # Pintu tertutup
    GPIO.output(pin, GPIO.LOW)

def main():

    solonoid_open(out)
    time.sleep(1)

if __name__ == '__main__' :
    try :
        main()
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
