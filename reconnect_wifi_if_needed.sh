#!/bin/bash

# Add the following to root's crontab:
# */10 * * * * /home/kkellner/rpi-ha-ceiling-display/reconnect_wifi_if_needed.sh >> /var/log/wifi_reconnect.log 2>&1

# Docs for: https://developer.gnome.org/NetworkManager/stable/nmcli.html
# nmcli general status
# nmcli connection show --active
# nmcli dev wifi

# For ceiling optiplex:
# nmcli device disconnect wlx1cbfce55b322; sleep 2; nmcli device connect wlx1cbfce55b322


# Option to restart the entire networking service:
# sudo service network-manager restart

outputRows=$(nmcli connection show --active | wc -l)

# We use "less then 2" here because there is a header row in addition
# to the active wifi connection row (if wifi is connected)
if [ "$outputRows" -lt  2 ]
then
  echo "### WIFI is NOT connected at: $(date)"
  # Show general status
  echo "Status before restart of WIFI:"
  nmcli connection show --active 
  nmcli general status

  # Try to reconnect to wifi
  nmcli device disconnect wlx1cbfce55b322; sleep 5; nmcli device connect wlx1cbfce55b322; sleep 2

  # Show status after reconnect
  echo "Status after restart of WIFI:"
  nmcli connection show --active 
  nmcli general status
else
  echo "WIFI is OK at: $(date)"
fi
