#!/usr/bin/python
# -*- coding: utf-8 -*-

#这显示了MQTTv5远程过程调用（RPC）客户端的示例。

import sys
import time
import json
import paho.mqtt.client as mqtt
from paho.mqtt.packettypes import PacketTypes

#这些将使用服务器分配的客户端ID更新
client_id = "mathcli"
reply_to = ""

# 将出站请求与返回的回复相关联
corr_id = b"1"

# 当我们得到响应时，在消息回调中发送
reply = None

#MQTTv5回调采用附加的“ props”参数。
def on_connect(mqttc, userdata, flags, rc, props):
    global client_id, reply_to

    print("Connected: '"+str(flags)+"', '"+str(rc)+"', '"+str(props))
    if hasattr(props, 'AssignedClientIdentifier'):
        client_id = props.AssignedClientIdentifier
    reply_to = "replies/math/" + client_id
    mqttc.subscribe(reply_to)


#收到的邮件应该是对我们请求的回复
def on_message(mqttc, userdata, msg):
    global reply

    print(msg.topic+" "+str(msg.payload)+"  "+str(msg.properties))
    props = msg.properties
    if not hasattr(props, 'CorrelationData'):
        print("No correlation ID")

    #将响应与请求相关性ID匹配。
    if props.CorrelationData == corr_id:
        reply = msg.payload

if len(sys.argv) < 3:
    print("USAGE: client_rpc_math.py [add|mult] n1 n2 ...")
    sys.exit(1)

mqttc = mqtt.Client(client_id="", protocol=mqtt.MQTTv5)
mqttc.on_message = on_message
mqttc.on_connect = on_connect

mqttc.connect(host='localhost', clean_start=True)
mqttc.loop_start()

#等待连接设置`client_id`等。
while not mqttc.is_connected():
    time.sleep(0.1)

#请求的属性指定ResponseTopic和CorrelationData
props = mqtt.Properties(PacketTypes.PUBLISH)
props.CorrelationData = corr_id
props.ResponseTopic = reply_to

#取消注释以查看设置了什么
#print("Client ID: "+client_id)
#print("Reply To: "+reply_to)
#print(props)

# The requested operation, 'add' or 'mult'
func = sys.argv[1]

#将数字参数收集为数字数组
#这些可以是int或float的
args = []
for s in sys.argv[2:]:
    args.append(float(s))

# Send the request
topic = "requests/math/" + func 
payload = json.dumps(args)
mqttc.publish(topic, payload, qos=1, properties=props)

# Wait for the reply
while reply is None:
    time.sleep(0.1)

# Extract the response and print it.
rsp = json.loads(reply)
print("Response: "+str(rsp))

mqttc.loop_stop()