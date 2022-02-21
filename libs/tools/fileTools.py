import os
import datetime
'''
module for reading and writing data
Version 1.1
written by Mark Wottreng
'''
def writeStrToFile(data: str, path: str = os.getcwd(), filename: str = "data.txt", method: str = "w"):
    with open(f"{path}/{filename}", method) as file:
        file.write(f"{data}\n")
    print(f"data writen to: {filename}")

def writeListToFile(data: list, path: str = os.getcwd(), filename: str = "dataList.txt", method: str = "w"):
    with open(f"{path}/{filename}", method) as file:
        for line in data:
            file.write(f"{line}\n")
    print(f"data list written to: {filename}")

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
    date = datetime.datetime.now()
    dateFormat = date.strftime("%d-%b-%Y %H:%M:%S")
    with open(f"{os.getcwd()}/debug_log.txt", mode) as log:
        log.write(f"{dateFormat} >< {data}\n")

#