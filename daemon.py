#!/usr/bin/python3
#
# Created by Matthijs Visser

import datetime
import time
import sys
import signal
import subprocess
import logging
import paho.mqtt.client as paho
import yaml
from kamstrup_meter import kamstrup
from mqtt_handler import MqqtHandler
from systemd.journal import JournalHandler


log = logging.getLogger("log")
log.addHandler(JournalHandler())
log.setLevel(logging.DEBUG)


with open("config.yaml", "r") as ymlfile:
	cfg = yaml.load(ymlfile, Loader=yaml.BaseLoader)

def main():
    log.info('initializing daemon')

    mqtt_cfg = cfg["mqtt"]
    serial_cfg = cfg["serial_device"]
    kamstrup_cfg = cfg["kamstrup"]

    if (mqtt_cfg["retain"].lower() == "true"):
        retain = True
    else:
        retain = False

    if (mqtt_cfg["authentication"].lower() == "true"):
        mqtt_handler = MqqtHandler(mqtt_cfg["host"], int(mqtt_cfg["port"]),
            mqtt_cfg["client"], mqtt_cfg["topic"], retain, int(mqtt_cfg["qos"]),
            True, mqtt_cfg["username"], mqtt_cfg["password"])
    else:
        mqtt_handler = MqqtHandler(mqtt_cfg["host"], int(mqtt_cfg["port"]),
            mqtt_cfg["client"], mqtt_cfg["topic"], retain, int(mqtt_cfg["qos"]))
    mqtt_handler.connect()
    mqtt_handler.loop_start()

    heat_meter = kamstrup(serial_cfg["com_port"], kamstrup_cfg["parameters"])

    values = heat_meter.run()
    mqtt_handler.publish("values", str(values).replace("'", "\""))


if  __name__ == '__main__':
	main()
