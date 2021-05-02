#!/bin/bash

# Add the following to root's crontab:
# */1 * * * * /home/kkellner/rpi-ha-ceiling-display/monitor_display.sh >> /var/log/monitor_display.log 2>&1


now=$(date)
display_identifier=$(ls /sys/class/drm/*/edid | xargs -i{} sh -c "echo {}; parse-edid -q 2> /dev/null < {}" | grep Identifier)

echo "$now Identifier: $display_identifier"
