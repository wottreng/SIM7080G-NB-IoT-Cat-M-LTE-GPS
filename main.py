#!/usr/bin/python3
from os import stat
import time

'''
main script for sim7080g module testing
controlled via UART on Rpi Zero W

Version 1.0
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
from libs.network_tools import https_post_request, setup_dns, connect_to_network, https_get_request, \
    get_ntp_time, ping_server
from libs.gps_tools import get_GPS_Position, single_GPS_point_req

# from libs.tools import fileTools
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
    Hardware_Info()
    #
    # connected = connect_to_network()
    #
    return True
# ------------------


def main_loop():
    send_to_server_counter: int = 6
    send_to_server_at_count_number: int = 6  # update server with location every hour
    #
    while True:
        status = False
        while not status:
            status = setup()
            if not status:
                power_down()
                time.sleep(10)
        # connect_to_network(disconnect=True)
        status = single_GPS_point_req()
        if status == True:
            time.sleep(1)
            #
            # get_GPS_Position(number_of_data_points=5)
            #
            # ping_server(domain_name="1.1.1.1")
            #
            # https_get_request(confirm_cert=False)
            #
            if send_to_server_counter == send_to_server_at_count_number:
                connected = connect_to_network()
                if connected:
                    setup_dns()
                    https_post_request(confirm_cert=False, parameter_dict=config.gps_data)
                    send_to_server_counter = 0
                connect_to_network(disconnect=True)
                #
            send_to_server_counter+=1
        #
        power_down()  # shut down sim7080 module
        deepSleep(600)  # 10 min
        # --------------------

main_loop()

# ----------------------------------------------------
