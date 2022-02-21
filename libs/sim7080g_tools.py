'''
sim7080g tools and control module

written by Mark Wottreng
'''

import RPi.GPIO as GPIO
import serial
import time
import os

try:
    from libs.tools import fileTools
    #from libs.tools import timeTools
    from libs import config
except:
    from tools import fileTools
    #from tools import timeTools
    import config


class sim7080_tools_c():

    def __init__(self):
        self.power_key = config.power_key

    def power_on(self):
        fileTools.debug_log("power on")
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.power_key, GPIO.OUT)
        time.sleep(0.1)
        GPIO.output(self.power_key, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(self.power_key, GPIO.LOW)
        time.sleep(1)


    def power_down_via_PWR_GPIO(self):
        # NOTE: this is finicky and unreliable, use software command: sim7080_cmd.power_down()
        fileTools.debug_log("power down")
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.power_key, GPIO.OUT)
        time.sleep(0.1)
        GPIO.output(self.power_key, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(self.power_key, GPIO.LOW)
        time.sleep(1)

    def send_serial_cmd(self, command_to_send="", timeout=10, success="OK", failure=None, echo_cmd=False):
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
    def AT(self, cmd="", timeout=10, success="OK", failure="+CME ERROR"):
        cmd = 'AT' + cmd
        fileTools.debug_log(f"----------- {cmd} -----------")
        if config.verbose: print(f"verbose --- {cmd} ----")
        response = self.send_serial_cmd(command_to_send=cmd, timeout=timeout, success=success, failure=failure, echo_cmd=False)
        return response

    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    #           METHODS   
    # --------------------------------------------------------

    # check for a response, if none then toggle power pin 
    def start_sim7080g_module(self):
        self.AT(timeout=5)
        self.AT(timeout=5)
        response = self.AT(timeout=5) # test if its on
        if "Timeout" in response[0]: # if off
            self.power_on() # toggle PWR pin
            index = 0
            while True: # wait for ready response
                response = self.AT(success="PSUTTZ")
                if "Success" in response[0]:
                    break
                if index > 4:
                    fileTools.debug_log("[!] failed to start")
                    return False
                index += 1
        fileTools.debug_log("[*] module started")
        return True

    # check for network connection 
    def connect_to_network(self, new_connection:bool=True):
        if new_connection:
            self.AT("+CNMP=2") #
            self.AT("+CMNB?")
            self.AT(f"+CNCFG=0,1,\"{config.APN}\"") # config network APN
            self.AT(f"+CGDCONT=1,\"IP\",\"{config.APN}\"") # config connection type
        response = self.AT("+CNACT?") # check for ip addr
        if(len(response[1][0])<22): # if no public IP, then connect
            self.AT("+CNACT=0,1") # connect to network
            index = 0
            while(len(response[1][0])<22):
                time.sleep(2)
                response = self.AT("+CNACT?")
                index +=1
                if index == 4:
                    if config.verbose: print("[!] ERROR, no cellular connection")
                    fileTools.debug_log("[!] cellular failed to connect")
                    # free memory
                    index = None
                    response = None
                    return False
        config.public_IP_address = response[1][0]
        self.AT("+CSQ") # cellular quality
        # free memory
        index = None
        response = None
        #
        return True

    #
    def ping_server(self):
        self.AT("+SNPDPID=0") # select PDP index for ping
        if config.verbose: print("verbose -- [*] sleep 1")
        time.sleep(1)
        response = self.AT(f"+SNPING4=\"{config.url_domain_name}\",2,16,1000")
        fileTools.debug_log(f"ping resp: {response}")
        return response

    # 
    def https_request(self):
        if config.verbose: print("start https get request")
        self.AT("+CSSLCFG=\"sslversion\",1,3")
        self.AT(f"+SHSSL=1,\"{config.https_cert_name}\"")  # load ssl cert
        self.AT(f"+shconf=\"url\",\"https://{config.url_domain_name}:443\"") # config url endpoint
        self.AT(f"+shconf=\"timeout\",60") # default timeout in seconds
        self.AT("+shconf=\"bodylen\",1024")
        self.AT("+shconf=\"HEADERLEN\",350")
        self.AT("+shconf=\"pollcnt\",6") # number of connection attempts, max 15
        self.AT("+shconf=\"POLLINTMS\",500") # timeout for each attempt, max 500 ms
        self.AT("+shconf=\"ipver\",0") # use IPv4
        response = self.AT("+SHCONN") # connect to server
        if config.verbose: print(f"-- verbose -- {response}")
        index = 0
        while "OK" not in response[1][0]:
            fileTools.debug_log(f'server not connected. waiting...{index}')
            time.sleep(3)
            response = self.AT("+SHCONN") # output: ['Success', ['OK'], 1.033]
            index+=1
            if index == 3:
                fileTools.debug_log("[!] Failed to connect to server [!]")
                if config.verbose: print("[!] Failed to connect to server")
                index = None
                response = None
                return False
        if "OK" in response[1][0]:
            self.AT("+SHSTATE?") # return https connection state: 1 or 0
            self.AT("+SHCHEAD") # clear request header
            response = self.AT(f"+SHREQ=\"{config.url_path}\",1", success="SHREQ")  # (path, req) req types: 1:GET,2:PUT,3:POST,4:PATCH,5:HEAD
            if config.verbose: print(f'server resp: {response}') # +SHREQ: <type string>,<StatusCode>,<DataLen>
            fileTools.debug_log(f"server resp: {response}")
            self.AT("+shread=0,23", success="ip") # read response bytes from (x,y)
            self.AT("+shdisc") # disconnect
            #
            index = None
            response = None
            return True

    # not tested
    def get_ntp_time(self):
        if config.verbose: print("[*] get NTP time")
        self.AT('+CNTP="pool.ntp.org",0,1,2') # config: <ntp server>[,<time zone>][,<cid>][,<mode>]
        self.AT('+CNTP', timeout=6, success="+CNTP") # request. output 1:success, 61:network error, 62:dns error, 63:connect error
        return True

    '''
    // GPS - needs network connection
- ref: https://www.techstudio.design/wp-content/uploads/simcom/SIM7070_SIM7080_SIM7090_Series_GNSS_Application_Note_V1.02.pdf
- note: takes time to acquire signal, when GPS is cold started

gps data output example: 
AT+CGNSINF ->  +CGNSINF: 1,1,20220213,23:15:59.000,23.357118,-56.470442,125.412,0.00,,0,,1.1,1.3,0.8,,12,,4.5,6.0
<GNSS run status>,<Fix status>,<UTC date & Time>,<Latitude>,<Longitude>,<MSL(mean sea level) Altitude>,<Speed Over Ground>,<Course Over Ground>,<Fix Mode>,<Reserved1>,<HDOP>,<PDOP>,<VDOP>,<Reserved2>,<GN SS Satellites in View>,<Reserved3>,<HPA>,<VPA>
    '''
    def get_GPS_Position(self):
        # check for network connection:
        network_connection = self.connect_to_network(new_connection=False)
        if network_connection == False:
            if config.verbose: print("[!] no network connection for GPS")
            fileTools.debug_log("[!] no network connection for GPS")
            return False
        # start gps
        gps_output = ""
        data_received = False
        if config.verbose: print('Start GPS session...')
        self.AT('+CGNSPWR=1', success="OK", timeout=1)
        time.sleep(1)
        self.AT("+cgnscold") # cold start
        time.sleep(2)
        # get gps data
        counter = 0
        while True:
            response:list = self.AT('+CGNSINF',success='+CGNSINF: ',timeout=1)
            if ',,,,,,' in response[1][0]:
                if config.verbose: print('no GPS signal yet')
                fileTools.debug_log(f"no GPS signal yet: {counter}")
                time.sleep(1)
            elif "1" in response[1][0]: 
                if config.verbose: print("GPS data received, data stored in data folder")
                fileTools.writeStrToFile(data=response[1][0], path=f"{os.getcwd()}/data", filename="gps_data", method="a")
                fileTools.debug_log(f"GPS data received, counter: {counter}")
                self.AT('+CGNSPWR=0',timeout=1)
                return True
            else:
                if config.verbose: print(f'[!] ERROR: {response}')
                fileTools.debug_log(f"[!] ERROR: gps resp: {response}")
                self.AT('+CGNSPWR=0',timeout=1)
                return False
            counter+=1
            if counter > 6: 
                self.AT('+CGNSPWR=0',timeout=1)
                return False

    # NOT TESTED
    def http_request(self):
        if config.verbose: print("[*] http request")
        self.AT('+HTTPINIT')
        self.AT('+HTTPPARA="CID",1')
        self.AT(f'+HTTPPARA="URL","http://{config.url_domain_name}"')
        self.AT('+HTTPACTION=0', timeout=30, success="+HTTPACTION: 0,200")
        self.AT('+HTTPREAD')
        self.AT('+HTTPTERM')

    # NOT TESTED
    def get_gprs_info(self):
        self.AT("+CGREG?") # Get network registration status
        self.AT("+CGACT?") # Show PDP context state
        self.AT('+CGPADDR') # Show PDP address
        self.AT("+CGCONTRDP") # Get APN and IP address
        self.AT('+CGNAPN') # Check nb-iot Status

    # from waveShare, NOT TESTED
    def mqtt_req(self):
        Message = "test"
        self.AT('+CSQ',timeout=1)
        self.AT('+CPSI?',timeout=1)
        self.AT('+CGREG?',success='+CGREG: 0,1',timeout=0.5)
        self.AT('+CNACT=0,1',timeout=1)
        self.AT('+CACID=0', timeout=1)
        self.AT('+SMCONF=\"URL\",broker.emqx.io,1883',timeout=1)
        self.AT('+SMCONF=\"KEEPTIME\",60',timeout=1)
        self.AT('+SMCONN',timeout=5)
        self.AT('+SMSUB=\"waveshare_pub\",1',timeout=1)
        self.AT('+SMPUB=\"waveshare_sub\",17,1,0',timeout=1)
        self.send_serial_cmd(command_to_send=Message)
        time.sleep(10);
        if config.verbose: print('send message successfully!')
        self.AT('AT+SMDISC', timeout=1)
        self.AT('AT+CNACT=0,0', timeout=1)

    def Hardware_Info(self):
        self.AT("+CPIN?") # Check sim card is present and active
        self.AT("+CGMM") # Check module name
        self.AT("+CGMR") # Firmware version
        self.AT('+GSN') # Get IMEI number
        self.AT('+CCLK?') # Get system time
        return True

    def signal_info(self):
        self.AT("+COPS?") # Check operator info
        self.AT("+CSQ") # Get signal strength
        self.AT('+CPSI?') # Get more detailed signal info
        self.AT('+CBAND?') # Get band
        return True

# --------------------------------------------------
