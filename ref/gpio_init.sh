#!/bin/bash
# setup RPI gpio 4 pin on boot
# run on boot with /etc/rc.local
echo "4" > /sys/class/gpio/export
sleep 0.1
echo "out" > /sys/class/gpio/gpio4/direction
echo "1" > /sys/class/gpio/gpio4/value
#
