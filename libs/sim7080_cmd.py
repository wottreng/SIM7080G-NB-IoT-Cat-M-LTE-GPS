'''
sim7080g commands module

written by Mark Wottreng
'''
import os

try:
    from libs.sim7080g_tools import AT, send_serial_cmd
except:
    from sim7080g_tools import AT, send_serial_cmd


def restart_board(_timeout:int=30):
    AT('+CFUN=1,1', timeout=_timeout, success="*PSUTTZ")

def power_down():
    AT("+CPOWD=1", success="NORMAL POWER DOWN")
    # alt: os.system('echo -e "at+cpowd=1\r" > /dev/serial0')

def power_up_via_terminal():
    os.system('echo "1" > /sys/class/gpio/gpio4/value && sleep 1 && echo "0" > /sys/class/gpio/gpio4/value')

def send_AT_cmd_via_terminal(cmd:str=""):
    # cmd need to be in form like: '+CNACT?'
    response = os.popen(f'echo -e "at{cmd}\r" | picocom -b 115200 -qrx 1000 /dev/serial0').read()
    return response

def turn_off_echo():
    send_serial_cmd("ATE0")

def set_debug_level():
    # more verbose debug output
    AT("+CMEE=2") 

# --------------------------------
    