'''
    GPS/GNSS
    // GPS - needs network connection
- ref: https://www.techstudio.design/wp-content/uploads/simcom/SIM7070_SIM7080_SIM7090_Series_GNSS_Application_Note_V1.02.pdf
- note: takes time to acquire signal, when GPS is cold started

gps data output example: 
AT+CGNSINF ->  +CGNSINF: 1,1,20220213,23:15:59.000,23.357118,-56.470442,125.412,0.00,,0,,1.1,1.3,0.8,,12,,4.5,6.0
<GNSS run status>,<Fix status>,<UTC date & Time>,<Latitude>,<Longitude>,<MSL(mean sea level) Altitude>,<Speed Over Ground>,<Course Over Ground>,<Fix Mode>,<Reserved1>,<HDOP>,<PDOP>,<VDOP>,<Reserved2>,<GN SS Satellites in View>,<Reserved3>,<HPA>,<VPA>
'''

import time
import os

try:
    from libs.tools import fileTools
    # from libs.tools import timeTools
    from libs.sim7080g_tools import AT
    from libs.network_tools import connect_to_network
    from libs import config
except:
    from tools import fileTools
    # from tools import timeTools
    from sim7080g_tools import AT
    from network_tools import connect_to_network
    import config


#
def toggle_RF_signal():
    # toggle phone functionality
    AT("+CFUN=0", success="OK", timeout=10)
    AT("+CFUN=1", success="OK", timeout=10)

# not used or tested ----------------
def get_GPS_Position(number_of_data_points: int = 20, time_between_data_points: int = 3):
    '''
    :param number_of_data_points: integer
    :param power_off_gps_when_finished: bool
    :param time_between_data_points: integer
    :return: bool for completed successfully or not
    '''
    # check for network connection:
    # network_connection = connect_to_network(new_connection=False)
    # if network_connection == False:
    #    if config.verbose: print("[!] no network connection for GPS")
    #    fileTools.debug_log("[!] no network connection for GPS")
    #    return False
    # -- disconnect from cellular network (cant do both, internal bug)
    connect_to_network(disconnect=True)
    # -- start gps
    if config.verbose: print('Start GPS session...')
    AT('+CGNSPWR=1', success="OK", timeout=1)
    time.sleep(1)
    AT("+cgnscold", timeout=15, success="OK")  # cold start
    time.sleep(10)
    # get gps data
    counter = 0
    while True:
        '''
        CGNSIF resp: 
            +CGNSINF: <[0] GNSS run status>,<[1] Fix status>,<[2] UTC date & Time>,<[3] Latitude>,<[4] Longitude>,<[5] MSL Altitude>,
            <[6] Speed Over Ground>,<[7] Course Over Ground>,<[8] Fix Mode>,<[9] Reserved1>,<[10] HDOP>,<[11] PDOP>,<[12] VDOP>,<[13] Reserved2>,
            <[14] GNSS Satellites in View>,<[15] Reserved3>,<[16] HPA>,<[17] VPA>

        ex. ['+CGNSINF: 1', '1', '20220225020342.000', '42.357098', '-83.470553', '239.132', '0.00', '', '0', '', '1.6', '1.9', '1.0', '', '6', '', '17.1', '24.0']
        42.357098, -83.470553
        https://www.mapquest.com/latlng/42.357098,-83.470553?zoom=20

        NOTES: 
            0:GNSS run status: 0 for off, 1 for on
            2: date & time: yyyyMMddhhmmss.sss
            5: Mean Sea Level Altitude: meters above sea level
            6: speed over ground: km/hour
            7:course over ground: direction of travel in degrees 0=North
            10: horizontal dilution of precision, lower the better,  range: 0 - 100
            11: position dilution of precision, lower the better, range 0 - 100
            12: veritical dilution of precision, lower the better, range: 0 - 100
            16: horizontal position accuracy, meters
            17: vertical position accuracy, meters
        '''
        response: list = AT('+CGNSINF', success='+CGNSINF: ', timeout=5)
        if ',,,,,,' in response[1][0]:
            if config.verbose: print('no GPS signal yet')
            fileTools.debug_log(f"no GPS signal yet: {counter}")
            time.sleep(time_between_data_points)
        elif "1" in response[1][0]:
            # bad resp ex: +CGNSINF: 1,,,0.000000,0.000000,-18.000,,,1,,0.1,0.1,0.1,,,,9999000.0,6144.0
            gps_data = response[1][0].split(",")
            fileTools.debug_log(f"gps_data: {gps_data}")
            if "1" in gps_data[1]:  # good data
                if config.verbose: print("GPS data received, data stored in data folder")
                fileTools.writeStrToFile(data=response[1][0], path=f"{os.getcwd()}/data", filename="gps_data.txt",
                                         method="a")
                config.gps_data.append(response[1][0])
                if config.verbose: print(f"gps data: {response[1][0]}")
                fileTools.debug_log(f"GPS data received, counter: {counter}")
            else:  # not accurate
                if config.verbose: print("GPS data is not accurate")
                fileTools.debug_log(f"GPS data received, not good, counter: {counter}, data: {response[1][0]}")
            time.sleep(time_between_data_points)
        else:
            if config.verbose: print(f'[!] ERROR: {response}')
            fileTools.debug_log(f"[!] ERROR: gps resp: {response}")
            AT('+CGNSPWR=0', timeout=1)
            return False
        counter += 1
        if counter > number_of_data_points:
            AT('+CGNSPWR=0', timeout=1)  # power off gps
            return True

# working
def single_GPS_point_req(number_of_attempts: int = 10):
    '''
    !!! possible bug fix: AT+SGNSCMD=1,0
    :return:

    :output data:
    1:gnss mode, 2:UTC time,3:latitude,4:longitude,5:msl accuracy (meters),6:msl altitude (meters),
    7:msl altitude sea level (meters), 8:speed over ground (km/hour), 9:direction over ground (degrees),
    10:time stamp (hex), 11:flag (?)
    :notes:
    ex. +SGNSCMD: 1,17:47:05,42.35724,-44.47087,37.25,99.74,135.00,0.00,0.00,0x17f31fe51a8,311\r\r\n
    1: 1-> on
    2: hh:mm:ss
    10: hex timestamp that equals epoch time measured in milliseconds
    '''
    if config.verbose: print("[+] start single gps point req...")
    counter = 0
    while True:
        resp = AT("+sgnscmd=1,0", success="+SGNSCMD", timeout=20, failure="+SGNSERR")
        if config.verbose: print(resp)
        if "Success" in resp[0]:
            fileTools.debug_log("[*] gps data received")
            for line in resp[1]:
                if "+SGNSCMD" in line:
                    sort_single_gps_data(line)
                    fileTools.writeDictToFile(data=config.gps_data, path=f"{os.getcwd()}/data", filename="gps_data",
                                              method="a")
            return True
        elif "Error" in resp[0]:
            fileTools.debug_log(f"[!] gps ERROR: {resp[1]}")
        if counter > number_of_attempts:
            fileTools.debug_log("Error: no response from GPS")
            return False
        counter += 1

# working
def sort_single_gps_data(gps_data: str):
    '''
    :param gps_data: ex. "+SGNSCMD: 1,17:47:05,42.35724,-44.47087,37.25,99.74,135.00,0.00,0.00,0x17f31fe51a8,311\r\r\n"
    :return: dictionary of key, values for gps data
    '''
    temp_string = gps_data.split(" ")[1].strip()  # cut off "+SGNSCMD: " and remove '\r\r\n'
    data_list = temp_string.split(",")
    keys = ["mode", "time", "lat", "long", "msl accuracy", "msl alt", "msl alt sea level",
            "speed", "direction", "hex_epoch", "flag"]
    #
    gps_data_dict = {}
    for index in range(10):
        gps_data_dict[keys[index]] = data_list[index]
    config.gps_data = gps_data_dict
    return True

# ---------------------
