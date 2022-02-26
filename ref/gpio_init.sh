#!/bin/bash
# setup RPI gpio 4 pin on boot
# run on boot with /etc/rc.local
echo "4" > /sys/class/gpio/export
sleep 0.1
echo "out" > /sys/class/gpio/gpio4/direction
sleep 0.2
echo "0" > /sys/class/gpio/gpio4/value
sleep 2
#echo -e "at+cpowd=1\r" > /dev/serial0
echo -e "at+cpowd=1\r" | picocom -b 115200 -qrx 1000 /dev/serial0
#
