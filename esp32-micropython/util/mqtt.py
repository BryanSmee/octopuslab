# function mqtt() for octopuLAB boards
# user is questioned in interactive mode
# from util.mqtt import mqtt

#TODO DRY for filename
import machine, time, uos, ubinascii, ujson
from umqtt.simple import MQTTClient
from util.mqtt_connect import read_mqtt_config
from util.wifi_connect import read_wifi_config, WiFiConnect
from util.pinout import set_pinout
ver = "2019/05 (c)octopusLAB"
esp_id = ubinascii.hexlify(machine.unique_id()).decode()

octopuASCII = [
"      ,'''`.",
"     /      \ ",
"     |(@)(@)|",
"     )      (",
"    /,'))((`.\ ",
"   (( ((  )) ))",
"   )  \ `)(' / ( ",
]

pinout = set_pinout()
pin_led = machine.Pin(pinout.BUILT_IN_LED, machine.Pin.OUT)
wifi_retries = 100  # for wifi connecting

def mainOctopus():
    for ol in octopuASCII:
        print(str(ol))
    print()

def simple_blink():
    pin_led.value(0)
    time.sleep(0.1)
    pin_led.value(1)
    time.sleep(0.1)     

def setupMenu():
    print()
    print('=' * 30)
    print('        S E T U P')
    print('=' * 30)
    print("[mq]  - set mqtt")
    print("[mqt] - mqtt simple test")
    print("[io]  - set mqtt i/o devices")
    print("[si]  - system info")
    print("[s]   - run setup()")
    print("[o]   - run octopus() demo")
    print("[e]   - exit setup")

    print('=' * 30)
    sel = input("select: ")
    return sel

# Define function callback for connecting event
def connected_callback(sta):
    simple_blink()
    #np[0] = (0, 128, 0)
    #np.write()
    simple_blink()
    print(sta.ifconfig())

def connecting_callback(retries):
    #np[0] = (0, 0, 128)
    #np.write()
    simple_blink()    

def mqtt():
    mainOctopus()
    print("Hello, this will help you initialize your ESP wit MQTT")
    print(ver)
    print(esp_id)
    print("Press Ctrl+C to abort")
    
    # TODO improve this
    # prepare directory
    if 'config' not in uos.listdir():
       uos.makedirs('config')

    run= True
    while run:
        sele = setupMenu()

        if sele == "e":
            print("Setup - exit >")
            time.sleep_ms(2000)
            print("all OK, press CTRL+D to soft reboot")
            run = False

        if sele == "si": #system_info()
            from util.sys_info import sys_info
            sys_info()

        if sele == "io":
            print("------- Set 0/1 for inpusts/outputs ------")
            print(" --> displays ---")
            wc = {}
            wc['oled'] = input("oled: ")
            wc['lcd'] = input("lcd: (2x16) ")
            wc['8x7'] = input("spi: (8x7 segment) ")
            wc['tft'] = input("tft: (128x64) ")
            wc['usm'] = input("UART: serial monitor ")
            wc['ws'] = input("ws1: [1/8/16/..]")
            print(" --> sensors ---")
            wc['temp'] = input("dallas temerature senzor: ")
            wc['adv1'] = input("adc: i36 - power: ")
            wc['adv2'] = input("adc: i35: ")
            wc['adv3'] = input("adc: i34 - light: ")
            wc['light'] = input("light i2c senzor: ")
            wc['button'] = input("button: ")
            wc['keyboard'] = input("keyboard: ")
            # servo1/2/3,motroA/B,stepper1/2

            print("Writing to file config/mqtt_io.json")
            with open('config/mqtt_io.json', 'w') as f:
                ujson.dump(wc, f)
                # ujson.dump(wc, f, ensure_ascii=False, indent=4)

        if sele == "mq":
            print("Set mqtt >")
            print()
            mq = {}
            mq['mqtt_broker_ip'] = input("BROKER IP: ")
            mq['mqtt_ssl'] = input("> SSL (0/1): ")
            mq['mqtt_port'] = input("> PORT (1883/8883/?): ")
            mq['mqtt_clientid_prefix'] = input("CLIENT PREFIX: ")
            mq['mqtt_root_topic'] = input("ROOT TOPIC: ")

            print("Writing to file config/mqtt.json")
            with open('config/mqtt.json', 'w') as f:
                ujson.dump(mq, f)

        if sele == "o":
            from util.octopus import octopus
            octopus() 

        if sele == "s":
            from util.setup import setup
            setup() 

        def mqtt_sub(topic, msg):  
            print("MQTT Topic {0}: {1}".format(topic, msg))                

        if sele == "mqt":
            print("mqtt simple test:")   

            print("wifi_config >")
            wifi_config = read_wifi_config()
            wifi = WiFiConnect(wifi_config["wifi_retries"] if "wifi_retries" in wifi_config else 250 )
            wifi.events_add_connecting(connecting_callback)
            wifi.events_add_connected(connected_callback)
            print("wifi.connect >")
            wifi_status = wifi.connect(wifi_config["wifi_ssid"], wifi_config["wifi_pass"])

            # url config: TODO > extern.

            print("mqtt_config >")
            mqtt_clientid_prefix = read_mqtt_config()["mqtt_clientid_prefix"]
            mqtt_host = read_mqtt_config()["mqtt_broker_ip"]
            mqtt_root_topic = read_mqtt_config()["mqtt_root_topic"]
            #mqtt_ssl  = False # Consider to use TLS!
            mqtt_ssl  = read_mqtt_config()["mqtt_ssl"]

            mqtt_clientid = mqtt_clientid_prefix + esp_id
            #c = MQTTClient(mqtt_clientid, mqtt_host, ssl=mqtt_ssl)
            c = MQTTClient(mqtt_clientid, mqtt_host)
            c.set_callback(mqtt_sub)
            print("mqtt.connect > ")
            c.connect()
            """
            # c.subscribe("/octopus/device/{0}/#".format(esp_id))
            subStr = mqtt_root_topic+"/"+esp_id+"/#"
            print("subscribe (root topic + esp id):" + subStr)
            c.subscribe(subStr)
            """

            print("mqtt log >")
            mqtt_log_topic = mqtt_root_topic+"/log"
            print(mqtt_log_topic)
            # mqtt_root_topic_temp = "octopus/device"
            c.publish(mqtt_log_topic,esp_id) # topic, message (value) to publish      

   