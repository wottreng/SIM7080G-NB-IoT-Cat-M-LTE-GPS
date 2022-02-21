'''
sim7080g commands module

written by Mark Wottreng
'''
import os

try:
    from libs.sim7080g_tools import sim7080_tools_c
except:
    from sim7080g_tools import sim7080_tools_c


st = sim7080_tools_c()


def restart_board():
    st.AT('+CFUN=1,1', timeout=30, success="*PSUTTZ")

def power_down():
    st.AT("+CPOWD=1", success="NORMAL POWER DOWN")
    # alt: os.system('echo -e "at+cpowd=1\r" > /dev/serial0')

def power_up_via_terminal():
    os.system('echo "1" > /sys/class/gpio/gpio4/value && sleep 1 && echo "0" > /sys/class/gpio/gpio4/value')

def send_AT_cmd_via_terminal(cmd:str=""):
    # cmd need to be in form like: '+CNACT?'
    response = os.popen(f'echo -e "at{cmd}\r" | picocom -b 115200 -qrx 1000 /dev/serial0').read()
    return response

def turn_off_echo():
    st.send_serial_cmd("ATE0")

def disconnect_from_network():
    st.AT("+CNACT=0,0")

def set_debug_level():
    st.AT("+CMEE=2") 

# --------------------------------
    