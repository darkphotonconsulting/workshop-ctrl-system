# HeadUnit Setup

## Overview

> HeadUnit

To create an API driven interface for controlling a **master** raspberry pi which is the entrypoint to a smart workshop.

- Devices in the shop requiring AC electric power sources are connected via AC contactor and controllable AC relays
- provides metrics & performance analytics on power consumption
- monitors environment via arduino connection (temp, water detection, air quality)
- fully configurable
  - GPIO ports configurable from interface
    - support various pi bus protocols (i2c, spi, pwm, etc)

## TODO

- [ ] Improve Docs
- [x] ~~Infrastructure As Code for pi sd configuration~~
- [x] ~~Decide on backend design (influx, mongo, flux, telegraf, etc)~~ 
  - :📓 options are limited due to current supported raspian OS being 32 bit but raspberry pi being a 64 bit arm cpu. mongo, influx, and most k/v stores require a 64 bit OS to operate.
- [ ] ~~Create backend schema(s) and relational logic~~
  - [ ] Not complete but, WIP (work in progress)

## Prerequisites

> ### Hardware

|                Item                 |                                                     Description                                                      |
| :---------------------------------: | :------------------------------------------------------------------------------------------------------------------: |
|          Raspberry Pi 4 B           |                             Logic controller, manages relay module, receives sensor data                             |
|            Power Supply             |                      5v 3a power supply for raspberry pi (optional, many ways to skin this cat)                      |
|            Arduino Mega             |                                 Sensor controller, monitors power, environment, etc                                  |
|            Relay Module             |                   Appropriate relay module for controlling power to the desired number of outputs                    |
|   Rasperry Pi 4 DIN Rail Adapter    |                    Provides convenient mount option & sturdy screw terminal block for connections                    |
|      Arduino Mega DIN Adapter       |                    Provides convenient mount option & sturdy screw terminal block for connections                    |
|     20 - 22 AWG solid core wire     | For power and logic connections between pins on Pi, Arduino and smaller devices such as sensors or inline regulators |
| Display Module for Raspberry Pi 4 B |            Main UI interface, should be touch screen, DIS interface, and only require 5V power and ground            |
|  Screw Terminal Adapters (female)   |                       Rule: logic connections should be secured by screw terminal connections                        |

> ### OS & Config

- ✅ git clone git@github.com:darkphotonconsulting/pi-gen.git
- ✅ git checkout feature/headunit
- ✅ read README and create a `config` file appropriately for your environment
- ✅ run build.sh -c config
  - if running in docker run build-docker.sh -c config, but that's going to break =)

