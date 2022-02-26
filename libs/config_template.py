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
PORT:str = "/dev/ttyS0"
BAUD:int = 115200
power_key:int = 4  # gpio 4 to pin 7 on sim 7080g

# https and ssl
confirm_cert = False
#
url_domain_name_0:str = "dev.example.net"
url_domain_name_1:str = "example.net"
#
url_path_0:str = "/api"
url_path_1:str = "/some_path"
#
https_cert_name_0:str = f"{url_domain_name_0.split('.')[0]}.crt" # assuming you uploaded endpoint ssl cert into flash as `example.crt`
https_cert_name_1:str = f"{url_domain_name_1.split('.')[0]}.crt"

# custom
post_req_parameter:str = "data_name"
gps_data:dict = {}
status:str = ""

# nework/cellular
APN:str = "Mobilenet"
public_IP_address:str = "0.0.0.0" # this is updated when connecting to cellular network

def init(): # on Start
    if change_UART_port_permission:
        # change uart port permissions, usually not needed
        # make sure your user name is added to dialout group
        if verbose: print("change uart port permission")
        os.system("sudo chmod 777 /dev/ttyS0")

    if clear_debug_log_on_start:
        if verbose: print("new log file")
        fileTools.debug_log("new log", "w")
