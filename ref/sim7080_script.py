#!/usr/bin/python3

# version 1.1

#import sys

import serial
import time
import os
from datetime import datetime
import RPi.GPIO as GPIO
#
from libs import config

#
verbose = True
clear_debug_log_on_start = True    

# change uart permissions
os.system("sudo chmod 777 /dev/ttyS0")




def power_on(power_key):
	debug_log("power on")
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(power_key,GPIO.OUT)
	time.sleep(0.1)
	GPIO.output(power_key,GPIO.HIGH)
	time.sleep(1)
	GPIO.output(power_key,GPIO.LOW)
	time.sleep(1)

def power_down(power_key):
    debug_log("power down")
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(power_key,GPIO.OUT)
    time.sleep(0.1)
    GPIO.output(power_key,GPIO.HIGH)
    time.sleep(2)
    GPIO.output(power_key,GPIO.LOW)
    time.sleep(2)

def send_cmd_new(command_to_send="", timeout=10, success="OK", failure=None, echo_cmd=False):
    with serial.Serial(config.PORT, config.BAUD, timeout=1) as ser:
        byte_command = f"{command_to_send}\r\n".encode('utf-8')
        ser.write(byte_command)
        t_start = time.time()
        reply = list()
        while True:
            if ser.in_waiting:
                line = ser.readline()
                debug_log(str(line))
                echo = False
                if echo_cmd:
                    echo = line.decode('utf-8').strip() #.endswith(echo_cmd)
                    #print(echo)
                    return ("Success", reply, time.time()-t_start)
                if (line != b"\r\n"):
                    line = line.decode('utf-8').strip()
                    #print(line)
                    # reply.append('\t' + line)
                    reply.append(line)
                    if success in line: # and line.startswith(success):
                        return ("Success", reply, time.time()-t_start)
                    if failure and line.startswith(failure):
                        return ("Error", reply, time.time()-t_start)
            if (time.time()-t_start) > timeout:
                return ("Timeout", reply, time.time()-t_start)
            time.sleep(0.01)

def AT(cmd="", timeout=10, success="OK", failure="+CME ERROR"):
    cmd = 'AT' + cmd
    debug_log(f"----------- {cmd} -----------")
    if verbose: print(f"verbose --- {cmd} ----")
    reply = send_cmd_new(command_to_send=cmd,timeout=timeout, success=success, failure=failure, echo_cmd=False)
    return reply

# Restart board: AT('+CFUN=1,1', timeout=30, success="*PSUTTZ")

# start ----------
if clear_debug_log_on_start:
    debug_log("new log", "w")
#
reply = AT(timeout=5)
if "Timeout" in reply[0]:
    power_on(config.power_key)
    index = 0
    #while index < 3:
    #    time.sleep(1)
    #    index +=1
else:
    debug_log("already powered on")
AT(success="PSUTTZ")
send_cmd_new("ATE0")
AT("+CNMP=2")
#AT("+CMNB=3")
AT("+CNCFG=0,1,'Mobilenet'")
AT("+CGDCONT=1,\"IP\",\"Mobilenet\"")
reply = AT("+CNACT?") # check for ip addr
if(len(reply[1][0])<22): # if no public IP, then connect
    AT("+CNACT=0,1")
index = 0
while(len(reply[1][0])<22):
    time.sleep(2)
    reply = AT("+CNACT?")
    index +=1
    if index == 4:
        debug_log("[!] cellular failed to connect")
        quit()
AT("+CSQ")
AT("+SNPDPID=0")
if verbose: print("verbose -- [*] sleep 5")
time.sleep(5)
reply = AT("+SNPING4=\"wotthome.net\",2,16,1000")
if "ERROR" not in reply[1][1]:
    if verbose: print("continue")
    time.sleep(1)
    AT("+CSSLCFG=\"sslversion\",1,3")
    AT("+SHSSL=1,\"example.crt\"")
    AT("+shconf=\"url\",\"https://wotthome.net\"")
    AT("+shconf=\"bodylen\",1024")
    AT("+SHCONF=\"HEADERLEN\",350")
    reply = AT("+SHCONN")
    if verbose: print(f"-- verbose -- {reply}")
    index = 0
    while "OK" not in reply[1][0]:
        debug_log(f'server not connected. waiting...{index}')
        time.sleep(3)
        reply = AT("+SHCONN")
        index+=1
        if index == 3:
            debug_log("[!] Failed to connect to server [!]")
            quit()
    if "OK" in reply[1][0]:  #('Success', ['OK'], 1.033165454864502)
        AT("+SHSTATE?")
        AT("+SHCHEAD")
        AT("+SHREQ=\"/ip\",1")
        if verbose: print("verbose -- [*] sleep 5")
        time.sleep(5)
        AT("+SHREAD=0,23", success="ip")
        AT("+shdisc")
        AT("+CNACT=0,0")
        AT("+CPOWD=1", success="NORMAL POWER DOWN")
        debug_log("[+] script complete")
        quit()
else:
    debug_log("[!] Ping Failed [!]")
    quit()



quit()
# ----------------------------------------------------

# AT('+CMNB=3') # Set preference for nb-iot (doesn't work with nb-iot)
#AT() # Check modem is responding
#AT("+CMEE=2") # Set debug level
# Hardware Info
#AT("+CPIN?") # Check sim card is present and active
#AT("+CGMM") # Check module name
#AT("+CGMR") # Firmware version
#AT('+GSN') # Get IMEI number
#AT('+CCLK?') # Get system time
# Signal info
#AT("+COPS?") # Check operator info
#AT("+CSQ") # Get signal strength
#AT('+CPSI?') # Get more detailed signal info
#AT('+CBAND?') # Get band
# GPRS info
#AT("+CGREG?") # Get network registration status
#AT("+CGACT?") # Show PDP context state
#AT('+CGPADDR') # Show PDP address
#cgcontrdp = AT("+CGCONTRDP") # Get APN and IP address
# Check nb-iot Status
#AT('+CGNAPN')

#APN = cgcontrdp[1][0].split(",")[2]
#IP = cgcontrdp[1][0].split(",")[3]

############################### PING/NTP ##################################
'''

# Ping - works :-)
if sys.argv[1] == "ping":
    print("++++++++++++++++++++ PING +++++++++++++++++++++\n")
    cstt = AT('+CSTT?')
    if APN not in cstt[1][0]:
        AT('+CSTT="{}"'.format(APN))
        AT('+CIICR')
    AT('+CIFSR', success=IP)
    AT('+CIPPING="www.google.com.au"')

# Get NTP time - working :-)
if sys.argv[1] == "ntp":
    print("++++++++++++++++++++ NTP +++++++++++++++++++++\n")
    AT('+SAPBR=3,1,"APN","{}"'.format(APN))
    AT('+SAPBR=1,1')
    AT('+SAPBR=2,1')
    AT('+CNTP="pool.ntp.org",0,1,1')
    AT('+CNTP', timeout=3, success="+CNTP")
    AT('+SAPBR=0,1')

############################### HTTP/MQTT ##################################

# HTTP Get example - working :-)
if sys.argv[1] == "http1":
    print("++++++++++++++++++++ HTTP1 +++++++++++++++++++++\n")
    AT('+SAPBR=3,1,"APN","{}"'.format(APN))
    AT('+SAPBR=1,1')
    AT('+SAPBR=2,1')
    AT('+HTTPINIT')
    AT('+HTTPPARA="CID",1')
    AT('+HTTPPARA="URL","http://minimi.ukfit.webfactional.com"')
    AT('+HTTPACTION=0', timeout=30, success="+HTTPACTION: 0,200")
    AT('+HTTPREAD')
    AT('+HTTPTERM')
    AT('+SAPBR=0,1')

# HTTP Get example - Working :-)
if sys.argv[1] == "http2":
    print("++++++++++++++++++++ HTTP2 +++++++++++++++++++++\n")
    AT('+CNACT=1')
    AT("+CNACT?")
    AT('+SHCONF="URL","http://minimi.ukfit.webfactional.com"')
    AT('+SHCONF="BODYLEN",350')
    AT('+SHCONF="HEADERLEN",350')
    AT('+SHCONN',timeout=30, success="OK")
    AT('+SHSTATE?')
    AT('+SHREQ="http://minimi.ukfit.webfactional.com",1', timeout=30, success="+SHREQ:")
    AT('+SHREAD=0,1199', timeout=30, success="</html>")
    AT('+SHDISC')

# MQTT (No SSL) - Working :-)
if sys.argv[1] == "mqtt-nossl":
    print("++++++++++++++++++++ MQTT - NO SSL +++++++++++++++++++++\n")
    AT("+CNACT=1") # Open wireless connection
    AT("+CNACT?") # Check connection open and have IP
    AT('+SMCONF="CLIENTID",1233')
    AT('+SMCONF="KEEPTIME",60') # Set the MQTT connection time (timeout?)
    AT('+SMCONF="CLEANSS",1')
    AT('+SMCONF="URL","{}","1883"'.format(MQTT_URL)) # Set MQTT address
    smstate = AT('+SMSTATE?') # Check MQTT connection state
    if smstate[1][0].split(":")[1].strip() == "0":
        AT('+SMCONN', timeout=30) # Connect to MQTT
    msg = "Hello Moto {}".format(datetime.now())
    AT('+SMPUB="test001","{}",1,1'.format(len(msg)), timeout=30, success=">") # Publish command
    send(msg.encode('utf-8'))
    watch(timeout=10)
    #AT('+SMSUB="test1234",1')
    AT('+SMDISC') # Disconnect MQTT
    AT("+CNACT=0") # Close wireless connection

############################### SSL/TLS ##################################

# Check certs on device - working :-)
if sys.argv[1] == "certs-check":
    print("++++++++++++++++++++ CERTS - CHECK +++++++++++++++++++++\n")
    AT('+CFSINIT')
    AT('+CFSGFIS=3,"{}"'.format(CA_NAME))
    AT('+CFSGFIS=3,"{}"'.format(CERT_NAME))
    AT('+CFSGFIS=3,"{}"'.format(KEY_NAME))
    AT('+CFSTERM')

# Delete certs on device - working :-)
if sys.argv[1] == "certs-delete":
    print("++++++++++++++++++++ CERTS - DELETE +++++++++++++++++++++\n")
    AT('+CFSINIT')
    AT('+CFSDFILE=3,"{}"'.format(CA_NAME))
    AT('+CFSDFILE=3,"{}"'.format(CERT_NAME))
    AT('+CFSDFILE=3,"{}"'.format(KEY_NAME))
    AT('+CFSTERM')

# Load a cert from a file on computer - working :-)
if sys.argv[1] == "certs-load":
    print("++++++++++++++++++++ CERTS - LOAD +++++++++++++++++++++\n")
    AT('+CFSINIT')
    with open(os.path.join(CERTS_FOLDER, CA_NAME),'rb') as f:
        data = f.read()
        AT('+CFSWFILE=3,"{}",0,{},5000'.format(CA_NAME, len(data)), success="DOWNLOAD")
        send(data)
    with open(os.path.join(CERTS_FOLDER, CERT_NAME),'rb') as f:
        data = f.read()
        AT('+CFSWFILE=3,"{}",0,{},5000'.format(CERT_NAME, len(data)), success="DOWNLOAD")
        send(data)
    with open(os.path.join(CERTS_FOLDER, KEY_NAME),'rb') as f:
        data = f.read()
        AT('+CFSWFILE=3,"{}",0,{},5000'.format(KEY_NAME, len(data)), success="DOWNLOAD")
        send(data)
    AT('+CFSTERM')

# MQTT (SSL) - CA and client certs, working for Mosquitto.org :-(
if sys.argv[1] == "mqtt-bothcerts":
    print("++++++++++++++++++++ MQTT - CA and Client Cert +++++++++++++++++++++\n")
    AT("+CNACT=1") # Open wireless connection
    AT("+CNACT?") # Check connection open and have IP
    AT('+SMCONF="CLIENTID", "TOMTEST01"')
    AT('+SMCONF="KEEPTIME",60') # Set the MQTT connection time (timeout?)
    AT('+SMCONF="CLEANSS",1')
    AT('+SMCONF="URL","{}","8884"'.format(MQTT_URL)) # Set MQTT address
    AT('+CSSLCFG="ctxindex", 0') # Use index 1
    AT('+CSSLCFG="sslversion",0,3') # TLS 1.2
    AT('+CSSLCFG="convert",2,"{}"'.format(CA_NAME))
    AT('+CSSLCFG="convert",1,"{}","{}"'.format(CERT_NAME, KEY_NAME))
    AT('+SMSSL=1, {}, {}'.format(CA_NAME, CERT_NAME))
    AT('+SMSSL?')
    AT('+SMSTATE?') # Check MQTT connection state
    AT('+SMCONN', timeout=60, success="OK") # Connect to MQTT, this can take a while
    AT('+SMSTATE?', timeout=5) # Check MQTT connection state
    msg = "Hello Moto {}".format(datetime.now())
    AT('+SMPUB="test001","{}",1,1'.format(len(msg)), success=">") # Publish command
    send(msg.encode('utf-8'))
    watch(timeout=10)
    #AT('+SMSUB="test1234",1')
    AT('+SMDISC') # Connect to MQTT
'''
