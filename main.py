#!/usr/bin/python3

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
from libs.sim7080g_tools import sim7080_tools_c
from libs.tools import fileTools
import libs.sim7080_cmd as sim_cmd
#
config.init()
#
sim_tools:object = sim7080_tools_c()
#
sim_tools.start_sim7080g_module()
#
sim_tools.connect_to_network()
#
response = sim_tools.ping_server()
#
if "ERROR" not in response[1][1]:
    #
    sim_tools.https_request()
    #
    sim_tools.get_GPS_Position()
    #
    sim_tools.get_ntp_time()
    #
    sim_tools.get_gprs_info()
    #
    sim_cmd.disconnect_from_network()
    #
    sim_cmd.power_down()
    #
    fileTools.debug_log("[+] script complete")
    quit()
else:
    fileTools.debug_log("[!] Ping Failed [!]")
    quit()


# ----------------------------------------------------
