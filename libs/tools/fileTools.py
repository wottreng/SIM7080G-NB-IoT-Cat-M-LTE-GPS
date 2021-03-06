import os
import datetime
'''
module for reading and writing data
Version 1.2

written by Mark Wottreng
'''
def writeStrToFile(data: str, path: str = os.getcwd(), filename: str = "data.txt", method: str = "w"):
    with open(f"{path}/{filename}", method) as file:
        file.write(f"{data}\n")
    #print(f"data writen to: {filename}")

def writeListToFile(data: list, path: str = os.getcwd(), filename: str = "dataList.txt", method: str = "w"):
    with open(f"{path}/{filename}", method) as file:
        for line in data:
            file.write(f"{line}\n")
    #print(f"data list written to: {filename}")

def writeDictToFile(data: dict, path: str = os.getcwd(), filename: str = "dataList.txt", method: str = "w"):
    with open(f"{path}/{filename}", method) as file:
        for key, value in data.items():
            file.write(f"{key}:{value},")
        file.write("\n")
    #print(f"data dict written to: {filename}")

def readFileList(path: str = os.getcwd(), filename: str = "dataList.txt"):
    dataList: list = []
    try:
        with open(f"{path}/{filename}", "r") as file:
            data: list = file.readlines()
        for line in data:
            dataList.append(line.strip())
    except:
        print(f"[!] file not found: {filename}")
    return dataList

def debug_log(data:str, mode:str = "a"):
    logging = True # turn defug logging on or off here --------------------------
    if logging:
        date = datetime.datetime.now()
        dateFormat = date.strftime("%d-%b-%Y %H:%M:%S")
        file_date = date.strftime("%d-%b-%Y")
        with open(f"{os.getcwd()}/data/debug_log_{file_date}.txt", mode) as log:
            log.write(f"{dateFormat} >< {data}\n")

#