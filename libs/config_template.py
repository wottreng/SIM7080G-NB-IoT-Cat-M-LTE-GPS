'''
config file for various settings

written by Mark Wottreng
'''
import os

try:
    from libs.tools import fileTools
except:
    from tools import fileTools

# run time configs
verbose:bool = True
clear_debug_log_on_start:bool = True
change_UART_port_permission:bool = False

# GPIO and UART
PORT:str = "/dev/serial0"
BAUD:int = 115200
power_key:int = 4  # gpio 4 to pin 7 on sim 7080g

# https and ssl
url_domain_name:str = "example.net" # for DNS resolution
url_path:str = "/path"
https_cert_name:str = f"{url_domain_name.split('.')[0]}.crt" # assuming you uploaded endpoint ssl cert into flash as `example.crt`

# nework/cellular
APN:str = "Mobilenet"
public_IP_address:str = "0.0.0.0" # this is updated when connecting to cellular network

def init(): # on Start
    if change_UART_port_permission:
        # change uart port permissions
        if verbose: print("change uart port permission")
        os.system("sudo chmod 777 /dev/serial0")

    if clear_debug_log_on_start:
        if verbose: print("new log file")
        fileTools.debug_log("new log", "w")
