# HeadUnit Setup

## Overview

> HeadUnit

To create an API driven interface interface for controlling a **master** raspberry pi which is the entrypoint to a smart workshop.

- Devices in the shop requiring AC electric power sources are connected via AC contactor and controllable AC relays
- provides robust metrics and performance analytics
- fully configurable
  - easily configure GPIO ports for connection changes.

## TODO  

- [ ] Improve Docs
- [ ] Infrastructure As Code for pi sd configuration
- [ ] Decide on backend design (influx, mongo, flux, telegraf, etc)
- [ ] Create backend schema(s) and relational logic

## Prerequisites

### **What You Need**

- Power Adapter for Raspberry Pi (5V 3A)
- Raspberry Pi 4 Model B
- Arduino or ELEGOO Mega board
- Display Module for Raspberry Pi (DSI)
- 22 AWG wire (for logic connections)
- Relay Module

## Raspberry Pi Setup

### **Boot Config Initialization**

- configure microsd card with modern raspian version
- mount microsd card
  - enable ssh by creating the empty ssh file `touch /boot/ssh`
  - set language and locale
  - configure wifi settings in `/boot/wpa_supplicant.conf`
    - this file will be copied to the correct location on first boot
    - validate pi boots with wifi enabled and can be connected to

### Dependencies

- 🔴 A modern version of python, you can use minicondas base environment on the raspberry pi
  - `curl -o /tmp/installer.sh http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-armv7l.sh`
  - `sh /tmp/installer.sh`
- 🔴 A modern version of node
  - `curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -`
- 🔴 A modern version of the `yarn` package manager
  - `curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | gpg --dearmor | sudo tee /usr/share/keyrings/yarnkey.gpg >/dev/null`
  - `echo "deb [signed-by=/usr/share/keyrings/yarnkey.gpg] https://dl.yarnpkg.com/debian stable main" | sudo tee /etc/apt/sources.list.d/yarn.list`
- 🍎 With the above steps taken, you can now run `apt-get update` to ensure all of your indexes are updated
- ℹ️ Node packages are managed by the yarn package manager, use `yarn install` in the repository root
- ℹ️ Python packages are managed within the requirements.txt and can be installed by executing `pip install -r requirements.txt` in the repository root
- ℹ️ For consistency, system packages installed with the `apt` package manager are stored in `apt.txt` and can be installed by executing `bash scripts/apt.sh`.

> **Dependency Map**

```yaml
---
deps:
    apt:
        - git
        - adduser 
        - libfontconfig1
        - gcc
        - gcc+
        - make
        - nodejs
        - npm
        - yarn
        - wiringpi
        - influxdb
        - influxdb-client
    pip:
        - RPi.GPIO
        - gpiozero
    node:
        - fortawesome/fontawesome-svg-core: 1.2.36
        - fortawesome/free-brands-svg-icons: 5.15.4
        - fortawesome/free-regular-svg-icons: 5.15.4
        - fortawesome/free-solid-svg-icons: 5.15.4
        - fortawesome/react-fontawesome: 0.1.15
        - material-ui/core: 4.12.3
        - material-ui/icons: 4.11.2
        - testing-library/jest-dom: 5.11.4
        - testing-library/react: 11.1.0
        - testing-library/user-event: 12.1.10
        - browserslist: 4.17.0
        - cors: 2.8.5
        - express: 4.17.1
        - influx: 5.9.2
        - node-os-utils: 1.3.5
        - react: 17.0.2
        - react-dom: 17.0.2
        - react-native: 0.65.1
        - react-router-dom: 5.3.0
        - react-scripts: 4.0.3
        - rpio: 2.4.2
        - web-vitals: 1.0.1
```
