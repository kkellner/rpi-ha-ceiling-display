#!/bin/bash

# Add the following to root's crontab:
# */1 * * * * /home/kkellner/rpi-ha-ceiling-display/monitor_network.sh >> /var/log/wifi_monitor.log 2>&1

pingable=$(DEFAULT_ROUTE=$(ip route show default | awk '/default/ {print $3}'); ping -q -c 1 $DEFAULT_ROUTE 2>&1 >/dev/null; echo $?)
wifiInfo=$(nmcli --escape no --get-values IN-USE,CHAN,SIGNAL,RATE,BSSID dev wifi)

now=$(date)
if [ "$pingable" -gt  0 ]
then
    echo "$now Gateway NoPing"
    nmcli connection show --active
    nmcli dev wifi
    nmcli general status

else
    echo "$now Gateway OK wifi: $wifiInfo"
fi
