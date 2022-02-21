'''
module for dealing with time stamps and dates
Version 1.1
written by Mark Wottreng
'''

import time
import datetime


def dateNow():
    date = datetime.date.today()
    dateFormat = date.strftime("%d-%b-%Y")
    return dateFormat


def dateTimeNow():
    date = datetime.datetime.now()
    dateFormat = date.strftime("%d-%b-%Y %H:%M:%S")
    return dateFormat


def epochTimeNow():
    return str(time.time()).split(".")[0]


def convertEpochTime(epochTime):
    date = datetime.datetime.fromtimestamp(epochTime)
    dateFormat = date.strftime("%d-%b-%Y %H:%M:%S")
    return dateFormat


if __name__ == "__main__":
    print(dateNow())  # 15-Feb-2022
    print(dateTimeNow())  # 15-Feb-2022 13:34:41
    print(epochTimeNow())  # 1644950081
    print(convertEpochTime(int(epochTimeNow())))  # 15-Feb-2022 13:35:50
