#!/bin/sh
# launcher.sh
#
# sudo crontab -e
# @reboot /home/pi/rpi-ha-ceiling-display/launcher.sh >> /var/log/ceiling.log 2>&1
#
cd /home/pi/rpi-ha-ceiling-display
sudo python3 /home/pi/rpi-ha-ceiling-display/ceiling_display.py
