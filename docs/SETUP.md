# HeadUnit Setup

## Overview

> What is the headunit project?

As a power DIY dude, the workshop build project should take electronic automation into account for powered devices, & components which will run. This may include the `headunit-z-table`, any power tools, 3d printers, CNC mills, shop-vacs, or otherwise.

- Use common microntrollers to maintain, monitor and manage line voltage to shop components. 
- Use sensors, AI/ML and other data to maintain safe operation of all shop components.
- Devices in the shop requiring AC electric power sources are connected via AC contactor and controllable AC relays
- provides metrics & performance analytics on power consumption
- monitors environment via arduino connection (temp, water detection, air quality)
- fully configurable
  - GPIO ports configurable from interface
    - support various pi bus protocols (i2c, spi, pwm, etc)

> What API interface(s) should be available?

- control a raspberry pi, and it's GPIOS
  - relay control should be a subset of this as it is cutting a line HIGH/LOW fundamentally
- control connected relay module

- metrics/state api
  - read data from connected Arduino Mega 
    - (USB serial or SDA data for example)
  - fetch, insert (backend), and read system metrics
  - fetch, insert and read gpio states
  - state tables

> Head Unit Backend
>
> [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

The backend is MongoDB, and this is problematic as recent versions of mongodb are not compatible with recent arm7l versions of raspbian. 
A supported 64-bit version of `Ubuntu 20.04` is available for installation on the pi, however the `pi-gen` tool does not currently support ubuntu. :ji

The backend services are python based and consists of

- metrics-server.py
  - provide metrics on connected devices/components
- gpio-server.py
  - control gpios, report state
- mongo-proxy.py  
  - crud for backend databases and collections

> Head Unit Frontend
>
> [![made-with-javascript](https://img.shields.io/badge/Made%20with-JavaScript-1f425f.svg)](https://www.javascript.com)

- headunit
  - Material React App
    - dashboard
      - display metrics
    - control GPIOs/relay
    - define metric schemas on backend

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