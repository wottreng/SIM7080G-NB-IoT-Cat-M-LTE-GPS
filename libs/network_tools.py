'''
networking related tools and functions

written by Mark Wottreng
'''
import time

from libs.sim7080_cmd import restart_board

try:
    from libs.tools import fileTools
    # from libs.tools import timeTools
    from libs.sim7080g_tools import AT, send_serial_cmd
    from libs import config
except:
    from tools import fileTools
    # from tools import timeTools
    from sim7080g_tools import AT, send_serial_cmd
    import config


# check for network connection
def connect_to_network(disconnect: bool = False) -> bool:
    if disconnect:
        AT("+CNACT=0,0")
        time.sleep(1)
        return True
    # -- connect
    AT("+CNMP=2")  # auto
    AT("+CMNB?")  # default is 3: cat-m and nb-iot
    AT("+CPSMS?")  # power saving mode
    AT(f"+CNCFG=0,1,\"{config.APN}\"")  # config network APN
    AT("+cgdcont?") # range for PDP values
    AT(f"+CGDCONT=1,\"IP\",\"{config.APN}\"")  # config connection type
    response = AT("+CNACT?")  # check for ip addr
    AT("+cgnapn")
    if (len(response[1][0]) < 24):  # if no public IP, then connect
        AT("+CNACT=0,1")  # connect to network
        index = 0
        while (len(response[1][0]) < 24):
            time.sleep(2)
            AT("+CSQ")  # cellular quality
            AT("+cgpaddr?") # show pdp address
            response = AT("+CNACT?")
            index += 1
            if index == 8:
                fileTools.debug_log(f"ip addr output: {response}")
                if config.verbose: print("[!] ERROR, no cellular connection")
                fileTools.debug_log("[!] cellular failed to connect")
                return False
    config.public_IP_address = response[1][0]
    #
    get_gprs_info()

    #
    return True


#
def ping_server(domain_name: str = config.url_domain_name_1, number_of_pings: int = 2) -> bool:
    AT("+SNPDPID=0")  # select PDP index for ping
    response = AT(f"+SNPING4=\"{domain_name}\",{number_of_pings},16,1000", timeout=30)
    if "Success" in response[0]:
        fileTools.debug_log(f"ping resp: {response}")
        return True
    else:
        fileTools.debug_log("[!] Ping ERROR")
        return False


# GET req.  parameters ex. "?this=that"
def https_get_request(domain_name: str = config.url_domain_name_1, path: str = config.url_path_1,
                      cert_name: str = config.https_cert_name_1, parameters: str = "",
                      confirm_cert: bool = config.confirm_cert) -> bool:
    if config.verbose: print("start https GET request")
    AT("+csslcfg=\"sslversion\",1,3")
    if confirm_cert:
        AT(f"+shssl=1,\"{cert_name}\"")  # load ssl cert
    else:
        AT('+shssl=1,""')  # wont confirm ssl cert for url
    AT(f"+shconf=\"url\",\"https://{domain_name}:443\"")  # config url endpoint
    AT(f"+shconf=\"timeout\",60")  # default timeout in seconds
    AT("+shconf=\"bodylen\",1024")
    AT("+shconf=\"HEADERLEN\",350")
    AT("+shconf=\"pollcnt\",6")  # number of connection attempts, max 15
    AT("+shconf=\"POLLINTMS\",500")  # timeout for each attempt, max 500 ms
    AT("+shconf=\"ipver\",0")  # use IPv4
    response = AT("+SHCONN")  # connect to server
    if config.verbose: print(f"-- verbose -- {response}")
    index = 0
    if "OK" not in response[1][0]:  # if no connection to server
        while "OK" not in response[1][0]:
            fileTools.debug_log(f'server not connected. waiting...{index}')
            time.sleep(3)
            response = AT("+SHCONN")  # ex. output: ['Success', ['OK'], 1.033]
            index += 1
            if index == 3:
                fileTools.debug_log("[!] Failed to connect to server [!]")
                if config.verbose: print("[!] Failed to connect to server")
                index = None
                response = None
                return False
    if "OK" in response[1][0]:  # if connection to server is successful
        AT("+SHSTATE?")  # return https connection state: 1 or 0
        AT("+SHCHEAD")  # clear request header
        # you can add header statements here but I choose not too. works fine without.
        #
        response = AT(f"+SHREQ=\"{path}{parameters}\",1",
                      success="SHREQ")  # (path, req) req types: 1:GET,2:PUT,3:POST,4:PATCH,5:HEAD
        if config.verbose: print(
            f'server resp: {response}')  # +SHREQ: <type string>,<StatusCode>,<DataLen> ie. '+SHREQ: "GET",200,31\r\n'
        fileTools.debug_log(f"server resp: {response}")
        response_list = response[1][1].strip().split(" ")[1].split(",")  # ["GET",200,31]
        status_code = response_list[1]  # ie. 200
        response_length = response_list[2]  # ie. 31
        fileTools.debug_log(f"response_list: {response_list}")
        resp = AT(f"+shread=0,{response_length}", success="ip")  # read response bytes from x,y
        # config.public_IP_address = resp[1][0]
        print(f"public addr: {resp[1]}")
        AT("+shdisc")  # disconnect
        #
        index = None
        response = None
        response_list = None
        response_length = None
        fileTools.debug_log("end https_GET_request")
        return True


# POST req
def https_post_request(domain_name: str = config.url_domain_name_0, path: str = config.url_path_0,
                       cert_name: str = config.https_cert_name_0, parameter_dict=None,
                       confirm_cert: bool = config.confirm_cert) -> bool:

    if parameter_dict is None:
        parameter_dict = {"this":"that"}
    if config.verbose: print("[+] start POST req...")
    AT("+csslcfg=\"sslversion\",1,3")
    if confirm_cert:
        AT(f"+shssl=1,\"{cert_name}\"")  # load ssl cert
    else:
        AT('+shssl=1,""')  # wont confirm ssl cert for url
    AT(f"+shconf=\"url\",\"https://{domain_name}:443\"")  # config url endpoint
    AT(f"+shconf=\"timeout\",60")  # default timeout in seconds
    AT("+shconf=\"bodylen\",1024")
    AT("+shconf=\"HEADERLEN\",350")
    AT("+shconf=\"pollcnt\",6")  # number of connection attempts, max 15
    AT("+shconf=\"POLLINTMS\",500")  # timeout for each attempt, max 500 ms
    AT("+shconf=\"ipver\",0")  # use IPv4
    response = AT("+SHCONN", timeout=15)  # connect to server
    if config.verbose: print(f"-- verbose -- {response}")
    index = 0
    if "Success" not in response[0]:  # if no connection to server
        while "Success" not in response[0]:
            fileTools.debug_log(f'server not connected. waiting...{index}')
            time.sleep(3)
            response = AT("+SHCONN")  # ex. output: ['Success', ['OK'], 1.033]
            index += 1
            if index == 3:
                fileTools.debug_log("[!] Failed to connect to server [!]")
                if config.verbose: print("[!] Failed to connect to server")
                index = None
                response = None
                restart_board()
                return False
    if "OK" in response[1][0]:  # if connection to server is successful
        AT("+SHSTATE?")  # return https connection state: 1 or 0
        AT("+SHCHEAD")  # clear request header
        # AT("+SHAHEAD=\"Content-Type\",\"application/x-www-form-urlencoded\"")
        # -- add data  ---
        #  -- body --
        # AT("+SHBOD=7,10000", timeout=1) # set body content
        # send_serial_cmd("reciept", timeout=1)
        #  -- parameters --
        AT("+shcpara")  # clear body content
        # add data to req
        AT(f"+shpara=\"gps\",\"1\"")
        for key, value in parameter_dict.items():
            if len(value) > 64:
                fileTools.debug_log("[!] error: data is too long. chopping to 64 bytes")
                value = value[:63]
            AT(f"+shpara=\"{key}\",\"{value}\"")  # add body content
        # -- send data --
        response = AT(f"+SHREQ=\"{path}\",3", success="+SHREQ", timeout=20)  # (path, req)
        if config.verbose: print(
            f'server resp: {response}')  # +SHREQ: <type string>,<StatusCode>,<DataLen> ie. '+SHREQ: "GET",200,31\r\n'
        if response[0] != "Success":
            fileTools.debug_log(f"[!] Error, data not sent, server resp: {response}")
            return False
        fileTools.debug_log(f"server resp: {response}")
        response_list = response[1][1].strip().split(" ")[1].split(",")  # ["GET",200,31]
        status_code = response_list[1]  # ie. 200
        response_length = response_list[2]  # ie. 31
        fileTools.debug_log(f"response_list: {response_list}")
        AT(f"+shread=0,{response_length}", success="ip", timeout=2)  # read response bytes from x,y
        AT("+shdisc")  # disconnect
        #
        index = None
        response = None
        response_list = None
        response_length = None
        fileTools.debug_log("end https_POST_request")
        return True


# not working. keep getting code 63 for connection problem
def get_ntp_time() -> bool:
    if config.verbose: print("[*] get NTP time")
    fileTools.debug_log("[*] get NTP time")
    AT('+cntpcid?')
    AT('+CNTPCID=0')
    AT('+CNTP=\"pool.ntp.org\",0,1,1')  # config: <ntp server>[,<time zone>][,<cid>][,<mode>]
    AT('+CNTP', timeout=10,
       success="+CNTP")  # request. output 1:success, 61:network error, 62:dns error, 63:connect error
    time.sleep(4)
    AT('+CNTP', timeout=10, success="+CNTP")
    time.sleep(2)
    resp = AT('+CCLK')  # get time output
    if "+CCLK" in resp[1][0]:
        return True
    else:
        return True


# signal debug output
def signal_info() -> bool:
    AT("+COPS?")  # Check operator info
    AT("+CSQ")  # Get signal strength
    AT('+CPSI?')  # Get more detailed signal info
    AT('+CBAND?')  # Get band
    AT('+cnbs?')  # band scan optimization
    return True


#
def setup_dns(dns_req_for_domain_name=False, domain_name=config.url_domain_name_1) -> bool:
    AT('+cdnspdpid?')  # pdp index for dns
    AT('+cdnspdpid=0')  # define pdp index
    AT('+cdnscfg="1.1.1.1","8.8.8.8"')  # config dns
    if dns_req_for_domain_name:
        resp = AT(f'+cdnsgip="{domain_name}"', success="+cdnsgip")  # get ip for url
        if "Success" in resp[0]:
            return True
        else:
            return False
    else:
        return True


# NOT TESTED
def http_request(domain_name=config.url_domain_name_0):
    if config.verbose: print("[*] http request")
    AT('+HTTPINIT')
    AT('+HTTPPARA="CID",1')
    AT(f'+HTTPPARA="URL","http://{domain_name}"')
    AT('+HTTPACTION=0', timeout=30, success="+HTTPACTION: 0,200")
    AT('+HTTPREAD')
    AT('+HTTPTERM')


# from waveShare, NOT TESTED
def mqtt_req():
    Message = "test"
    AT('+CSQ', timeout=1)
    AT('+CPSI?', timeout=1)
    AT('+CGREG?', success='+CGREG: 0,1', timeout=0.5)
    AT('+CNACT=0,1', timeout=1)
    AT('+CACID=0', timeout=1)
    AT('+SMCONF=\"URL\",broker.emqx.io,1883', timeout=1)
    AT('+SMCONF=\"KEEPTIME\",60', timeout=1)
    AT('+SMCONN', timeout=5)
    AT('+SMSUB=\"waveshare_pub\",1', timeout=1)
    AT('+SMPUB=\"waveshare_sub\",17,1,0', timeout=1)
    send_serial_cmd(command_to_send=Message)
    time.sleep(10);
    if config.verbose: print('send message successfully!')
    AT('AT+SMDISC', timeout=1)
    AT('AT+CNACT=0,0', timeout=1)


# works
def get_gprs_info() -> bool:
    #AT("+cgatt=1")  # attach to gprs
    AT("+cgatt?")  # gprs status
    AT("+CSQ")  # cellular quality
    AT("+CGREG?")  # Get network registration status
    AT("+cops?")  # network info, network mode
    AT("+CGACT?")  # Show PDP context state
    # AT("+cgact=1") # not supported on network
    AT('+CGPADDR')  # Show PDP address
    AT("+CGCONTRDP")  # Get APN and IP address
    AT('+CGNAPN')  # Check nb-iot Status
    return True
