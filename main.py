#!/usr/bin/python3
from os import stat
import time

'''
main script for sim7080g module testing
controlled via UART on Rpi Zero W

Version 1.1
status: not tested
TODO: test and debug

written by Mark Wottreng
'''
#
try:
    from libs import config
except Exception as e:
    print(f"[!] No config file! use the config_template to build your config")
    quit()
from libs.sim7080g_tools import start_sim7080g_module, Hardware_Info, deepSleep
from libs.sim7080_cmd import turn_off_echo, power_down
from libs.network_tools import https_post_request, setup_dns, connect_to_network
from libs.gps_tools import single_GPS_point_req
from libs.tools import fileTools
#
config.init()


def setup():
    #
    status = start_sim7080g_module()
    if not status:
        return False
    #
    turn_off_echo()
    #
    #Hardware_Info()
    #
    return True
# ------------------


def main_loop():
    send_to_server_counter: int = 6
    send_to_server_at_count_number: int = 2  # update server with location every hour
    #
    while True:
        status = False
        while not status:
            status = setup()
            if not status:  # power cycle sim module
                power_down()
                time.sleep(10)
        status = single_GPS_point_req()
        if status is True:
            time.sleep(2)
            #
            if send_to_server_counter > send_to_server_at_count_number:  # every 30min
                fileTools.debug_log("send data to server")
                counter = 0
                while True:
                    connected = connect_to_network()
                    if connected:
                        setup_dns()
                        status = https_post_request(confirm_cert=False, parameter_dict=config.gps_data)
                        if status:
                            send_to_server_counter = 0
                            break
                    connect_to_network(disconnect=True)
                    counter+=1
                    if counter > 4:
                        fileTools.debug_log("[!] ERROR. FAILED TO CONNECT TO SERVER")
                        break
                #
            else:
                fileTools.debug_log(f"[^] dont send data to server. send_to_server_counter: {send_to_server_counter}")
            send_to_server_counter+=1
        #
        deepSleep(600)  # 10 min
        # --------------------

main_loop()

# ----------------------------------------------------
