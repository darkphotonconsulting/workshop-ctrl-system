# Arduino Management (development)

This directory contains artifacts related to building Firmata and uploading it to the connected Arduino.

In order to accomplish this, a few things are needed.

- Arduino (tested with mega2560)
- USB cable (for connecting the Arduino to the Raspberry Pi via USB)
- arduino (ide), platformio,  and arduino-mk installed on raspberry pi

Technically, the only file in this directory ACTUALLY used in the software is `StandardFirmata.ino`, however the other folder components are used in development to:

- use make for building & uploading arduino code with arduino-mk
- use platform.io to build & upload to arduino
