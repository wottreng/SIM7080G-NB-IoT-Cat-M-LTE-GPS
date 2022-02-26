'''
sim7080g tools and control module

written by Mark Wottreng
'''

import RPi.GPIO as GPIO
import serial
import time

try:
    from libs.tools import fileTools
    #from libs.tools import timeTools
    from libs import config
except:
    from tools import fileTools
    #from sim7080_cmd import restart_board
    #from tools import timeTools
    import config

#
def power_on():
    fileTools.debug_log("power on")
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(config.power_key, GPIO.OUT)
    time.sleep(0.1)
    GPIO.output(config.power_key, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(config.power_key, GPIO.LOW)
    time.sleep(1)

#
def power_down_via_PWR_GPIO():
    # NOTE: this is finicky and unreliable, use software command: sim7080_cmd.power_down()
    fileTools.debug_log("power down")
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(config.power_key, GPIO.OUT)
    time.sleep(0.1)
    GPIO.output(config.power_key, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(config.power_key, GPIO.LOW)
    time.sleep(1)

#
def send_serial_cmd(command_to_send="", timeout=10, success="OK", failure=None, echo_cmd=False):
    with serial.Serial(config.PORT, config.BAUD, timeout=1) as ser:
        byte_command = f"{command_to_send}\r\n".encode('utf-8')
        ser.write(byte_command)
        t_start = time.time()
        response = []
        while True:
            if ser.in_waiting:
                line = ser.readline()
                fileTools.debug_log(str(line))
                if echo_cmd:
                    echo = line.decode('utf-8').strip()  # .endswith(echo_cmd)
                    if config.verbose: print(echo)
                    #return ("Success", response, time.time() - t_start)
                if (line != b"\r\n"):
                    line = line.decode('utf-8').strip()
                    # print(line)
                    # response.append('\t' + line)
                    response.append(line)
                    if success in line:  # and line.startswith(success):
                        return ("Success", response, time.time() - t_start)
                    if failure and line.startswith(failure):
                        return ("Error", response, time.time() - t_start)
            if (time.time() - t_start) > timeout:
                return ("Timeout", response, time.time() - t_start)
            time.sleep(0.01)

# send AT command, output: [(Success/Timeout/Error), (module resp), (cmd time)]
def AT(cmd="", timeout=10, success="OK", failure="ERROR"):
    cmd = 'AT' + cmd
    fileTools.debug_log(f"----------- {cmd} -----------")
    if config.verbose: print(f"verbose --- {cmd} ----")
    response = send_serial_cmd(command_to_send=cmd, timeout=timeout, success=success, failure=failure, echo_cmd=False)
    return response

# <><><><><><><><><><><><><><><><><><><><><><><><><><><><>
#           METHODS   
# --------------------------------------------------------

# check for a response, if none then toggle power pin 
def start_sim7080g_module():
    # from libs.sim7080_cmd import restart_board
    # restart_board(_timeout=10)
    AT(timeout=4)
    AT(timeout=4)
    response = AT(timeout=4) # test if its on
    if "Timeout" in response[0]: # if off
        power_on() # toggle PWR pin
        index = 0
        while True: # wait for ready response
            response = AT(success="*PSUTTZ", timeout=5)
            if "Success" in response[0]:
                break
            if index > 6:
                fileTools.debug_log("[!] failed to start")
                return False
            index += 1
    fileTools.debug_log("[*] module started")
    return True

#
def Hardware_Info() -> bool:
    AT("+CPIN?") # Check sim card is present and active
    AT("+CGMM") # Check module name
    AT("+CGMR") # Firmware version
    AT('+GSN') # Get IMEI number
    AT('+CCLK?') # Get system time
    return True

# when sim7080 becomes unresponsive, try reset then power toggle 
def regain_control() -> bool:
    pass

#
def deepSleep(how_long: int = 100):
    if config.verbose: print(f"[+] going into deep sleep for {how_long} sec")
    fileTools.debug_log(f"[+] going into deep sleep for {how_long} sec")
    time.sleep(how_long)
    fileTools.debug_log("[+] woke up from sleep")
    if config.verbose: print("[+] woke up from sleep")
# --------------------------------------------------
