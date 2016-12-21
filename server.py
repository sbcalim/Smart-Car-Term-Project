from flask import Flask, render_template, jsonify
import time
import RPi.GPIO as gpio
import smbus

gpio.setwarnings(False)
gpio.setmode(gpio.BOARD)

trigger = 11
echo = 16
motor_control = 22

bus = smbus.SMBus(1)
address = 0x68
pmr = 0x6b

bus.write_byte_data(address, pmr, 0)

gpio.setup(trigger, gpio.OUT)
gpio.setup(echo, gpio.IN)
gpio.setup(motor_control, gpio.OUT)

gpio.output(motor_control, True)

app = Flask(__name__)
@app.route('/_process')
def process():
    gpio.output(trigger, False)
    time.sleep(1)
    while(True):

        distance = distance_calculator()

        gyro_x = read_word(0x43)
        gyro_y = read_word(0x45)
        gyro_z = read_word(0x47)

	send = str(distance) + " cm" + "  " + str(gyro_x) + "  " + str(gyro_y) + "  " + str(gyro_z)

	if(distance>5 and distance<50):
            print "Dikatttt!!!!"
            while distance<50:
                bef = distance
                after = distance_calculator()
                if after-0.01<=bef:
                    continue
                else:
                    halt_motor()
                    distance = distance_calculator()
            return jsonify(result="!!! GO BACK !!! " + str(gyro_x) + " " + str(gyro_y) + " " + str(gyro_z))
	else:
            return jsonify(result=send)

@app.route('/')
def main():
    try:
        return render_template('main.html')
    except Exception, e:
        return str(e)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high<<8) + low

    if val>=0x80000:
        return int(-((65535-val) + 1)*0.00549)
    else:
        return int(val*0.00549)

def halt_motor():
    gpio.output(motor_control, False)
    time.sleep(1)
    gpio.output(motor_control, True)

def distance_calculator():
    gpio.output(trigger, True)
    time.sleep(0.0001)
    gpio.output(trigger, False)

    while gpio.input(echo) == 0:
	start_time = time.time();

    while gpio.input(echo) == 1:
	end_time = time.time();

    signal_time = end_time - start_time
    distance = round((signal_time * 17150), 2)

    return distance

app.run(host='0.0.0.0', port=5000, debug=True)