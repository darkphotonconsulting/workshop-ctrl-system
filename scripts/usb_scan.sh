#!/bin/bash -e

set -o pipefail 
find /sys/bus/usb/devices/usb*/ -name dev -print0 | while IFS= read -r -d '' sysdevpath; do 
    printf "top: %s\n" "$sysdevpath"
    (
        syspath="${sysdevpath%/dev}"

        devname="$(udevadm info -q name -p "$syspath")"
        [[ "$devname" == "bus/"* ]] && exit

        eval "$(udevadm info -q property --export -p "$syspath")"
        [[ -z "$ID_SERIAL" ]] && exit
        echo "/dev/$devname - $ID_SERIAL"
    )
done