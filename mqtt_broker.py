#!/usr/bin/env python
# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import json
import base64
import os


global image_big_path
image_big_path = 1
# 一旦连接成功，回调此方法
def on_connect(mqttc, obj, flags, rc):
    print(" connect success")
# 一旦订阅到消息，回调此方法
def on_message(mqttc, obj, msg):
     global image_big_path 
     playload = json.loads(msg.payload)
     print(playload["targets"][0]["id"])
     for key,value in playload.items():
        if key == "source":
            value = value.replace("data:image/jpeg;base64,","")
            decode_jpg = base64.b64decode(value)
            img_name = "image/%06d.jpg"%(image_big_path)
            if not os.path.exists("image/%s"%image_big_path):
                os.mkdir("image/%s"%image_big_path)
            with open(img_name,'wb')as f:
                f.write(decode_jpg)
            print(img_name)
            
        if key == "targets":
            k = 1
            for face_dict in value:
                bin_img = face_dict["image"].replace("data:image/jpeg;base64,","")
                new_image = "image/%s/%06d.jpg"%(image_big_path,k)
                if not os.path.exists("image/%s"%image_big_path):
                     os.mkdir("image/%s"%image_big_path)
                imgdata = base64.b64decode(bin_img)
                with open(new_image,'wb')as f:
                    f.write(imgdata)
                k = k + 1
     image_big_path += 1
    
# 一旦订阅成功，回调此方法
def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

# 一旦有log，回调此方法
def on_log(mqttc, obj, level, string):
        print("")

# 新建mqtt客户端，默认没有clientid，clean_session=True, transport="tcp"
mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
mqttc.on_log = on_log

# 连接broker，心跳时间为60s
mqttc.connect("192.168.0.181", 1883, 60)
# 订阅该主题，QoS=0
#mqttc.subscribe("senscape/facecapture/#", 0)
mqttc.publish("requests/math/add","hello",0)
#mqttc.loop_forever()
