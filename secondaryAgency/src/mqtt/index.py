#!/usr/bin/python
# -*- coding: utf-8 -*-
from idna import decode, encode
from tools import crateRandomId
import asyncio
from typing import List, Union
from paho.mqtt.client import (
    Client,
    MQTTv5,
    CallbackAPIVersion,
    Properties,
    MQTTMessage,
    SubscribeOptions,
)
from paho.mqtt.reasoncodes import ReasonCode as rc
from loguru import logger
from setting import settings

PayloadType = Union[str, bytes, bytearray, int, float, None]


class MqttService:
    def __init__(
        self,
        host: str,
        port: int = 1883,
        username: str = None,
        password: str = None,
        client_id: str = "fastapi-mqtt-client",
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client = Client(
            callback_api_version=CallbackAPIVersion.VERSION2,
            client_id=client_id,
            protocol=MQTTv5,
        )

        self.client.username_pw_set(username, password)
        self.client.on_connect = self.connect_callback
        self.client.on_disconnect = self.disconnect_callback
        self.client.on_message = self.message_callback
        # self.client.on_subscribe = self.subscribe_callback

    def subscribe_callback(
        self, client: Client, userdata, mid, reason_code_list, properties
    ):
        logger.info(f"new subscription: {reason_code_list}")

    def message_callback(self, client, userdata, msg: MQTTMessage):
        """
        收集未被订阅的topic，打印到log中
        """
        logger.info(f"收集未被订阅 topic[{msg.topic}]: {msg.payload.decode()}")

    def disconnect_callback(self, client, userdata, flags, reason_code, properties):
        logger.error(f"MQTT connection failed! Reason: {reason_code}")

    def connect_callback(
        self,
        client: Client,
        userdata,
        flags,
        reason_code,
        properties: Properties,
    ):
        if reason_code != "Success":
            logger.error(f"MQTT connection failed! Reason: {reason_code}")
        else:
            logger.info("MQTT connection successful.")

    def initSub(self):
        # 订阅初始的主题
        logger.info(
            f"Initialize the subscription topic: {settings.aimaster.subscribeTopic}",
        )
        topics = list(map(lambda topic: (topic, 0), settings.aimaster.subscribeTopic))
        self.subTopic(topics)

    def sendMsg(
        self,
        topic: str,
        payload: PayloadType = None,
        qos: int = 0,
        retain: bool = False,
        properties: Properties | None = None,
    ):
        self.client.publish(topic, payload, qos, retain, properties)

    def subTopic(
        self,
        topic: (
            str
            | tuple[str, int]
            | tuple[str, SubscribeOptions]
            | list[tuple[str, int]]
            | list[tuple[str, SubscribeOptions]]
        ),
        qos: int = 0,
        options: SubscribeOptions | None = None,
        properties: Properties | None = None,
    ):
        self.client.subscribe(topic)

    def unSubTopic(self, topic: str | List[str]):
        self.client.subscribe(topic)

    async def start(self):
        self.client.connect_async(self.host, self.port)
        self.client.loop_start()
        await asyncio.sleep(0.01)
        mqttHandle.initSub()

    def close(self):
        self.client.loop_stop()
        self.client.disconnect()


# 单例
mqttHandle = MqttService(
    host=settings.mqtt.host,
    port=settings.mqtt.port,
    username=settings.mqtt.username,
    password=settings.mqtt.password,
    client_id="secondaryAgency-" + crateRandomId(),
)
