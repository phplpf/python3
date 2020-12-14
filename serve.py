#!/usr/bin/python
# -*- coding: utf-8 -*-

# 这显示了MQTTv5远程过程调用（RPC）服务器的示例。
import json
import random,string
import paho.mqtt.client as mqtt
from paho.mqtt.packettypes import PacketTypes


#请记住，MQTTv5回调采用附加的“ props”参数。
def on_connect(mqttc, userdata, flags, rc, props):
    print("Connected: '"+str(flags)+"', '"+str(rc)+"', '"+str(props))
    if not flags["session present"]:
        print("Subscribing to math requests")
        mqttc.subscribe("requests/math/#")

#每条传入的消息都应该是RPC请求 
# 'requests/math/#' topic.
def on_message(mqttc, userdata, msg):
    print(msg.topic + "  " + str(msg.payload))

    #获取响应属性，如果没有给出则中止
    props = msg.properties
    if not hasattr(props, 'ResponseTopic') or not hasattr(props, 'CorrelationData'):
        print("No reply requested")
        return

    corr_id = props.CorrelationData
    reply_to = props.ResponseTopic


    #现在我们有了结果res，所以将其发送回'reply_to'
    #个主题，使用与请求相同的相关性ID。
    props = mqtt.Properties(PacketTypes.PUBLISH)
    props.CorrelationData = corr_id

    mqttc.publish(reply_to, msg.payload, qos=1, properties=props)

def on_log(mqttc, obj, level, string):
    print(string)


#通常，对于RPC服务，您需要确保自己是唯一的
#客户回答特定主题的请求。使用已知的客户端ID
#可能有帮助。

# 从a-zA-Z0-9生成指定数量的随机字符：
rd_str = ''.join(random.sample(string.ascii_letters + string.digits, 18))
print (rd_str)

mqttc = mqtt.Client(client_id=rd_str, protocol=mqtt.MQTTv5)
mqttc.on_message = on_message
mqttc.on_connect = on_connect

#取消注释以启用调试消息
# mqttc.on_log = on_log

#mqttc.connect("mqtt.eclipse.org", 1883, 60)
mqttc.connect(host="localhost", clean_start=False)
mqttc.loop_forever()