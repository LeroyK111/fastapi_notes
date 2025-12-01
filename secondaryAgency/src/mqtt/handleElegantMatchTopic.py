#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
优雅匹配固定topic，后续则可以构建为工厂模式
"""
from typing import Optional
from loguru import logger
import orjson
from mqtt import mqttHandle as mq
import requests as req
from paho.mqtt.client import MQTTMessage
from setting import settings


def shuntMethod(msg_payload: str) -> Optional[req.Response]:
    """
    msg_payload: MQTT 消息 payload，字符串，内容应为 JSON
                 包含 "url", "method", "data" 三个字段
    返回：requests.Response 对象（异常时抛出）
    """
    try:
        # 解析 JSON 消息
        msg_dict = orjson.loads(msg_payload)

        url = msg_dict.get("url", "")
        method = msg_dict.get("method", "")
        data = msg_dict.get("data", {})  # 无data时默认空字典，避免后续报错

        # 校验必填字段
        if url == "" or method == "":
            raise ValueError(f"缺少必填字段（url/method），消息内容：{msg_payload}")

        res = None
        # 匹配大写方法名（兼容大小写输入）
        match method.upper():
            case "POST":
                # POST：提交资源，json 传请求体
                res = req.post(url, json=data)
            case "GET":
                # GET：查询资源，params 传查询参数
                res = req.get(url, params=data)
            case "PUT":
                # PUT：全量更新资源，json 传完整资源数据
                res = req.put(url, json=data)
            case "DELETE":
                # DELETE：删除资源，支持 params（查询参数）或 json（请求体）
                # 优先用 params 传参，如需 json 可调整为 json=data
                res = req.delete(url, params=data)
            case "PATCH":
                # PATCH：部分更新资源，json 传需修改的字段
                res = req.patch(url, json=data)
            case _:
                raise ValueError(
                    f"不支持的 HTTP 方法：{method}，支持的方法：POST/GET/PUT/DELETE/PATCH"
                )

        # 校验响应（可选：抛出 HTTP 4xx/5xx 错误）
        if res is not None:
            res.raise_for_status()  # 若HTTP状态码异常，直接抛出异常
        return res

    except Exception as e:
        logger.exception(f"[shuntMethod] 处理消息失败，payload：{msg_payload}")
        raise  # 抛出异常让上层处理（如MQTT发布错误信息）


@mq.client.topic_callback(settings.aimaster.subscribeTopic[0])
def example_handler(client, userdata, msg: MQTTMessage):
    try:
        data = msg.payload.decode()
        logger.info(f"[example_handler] topic={msg.topic}, payload={data}")
        res = shuntMethod(data)
    except Exception as e:
        logger.error(f"[example_handler] Error: {e}")
        mq.sendMsg(
            "settings.aimaster.subscribeTopic[0]", orjson.dumps({"error": str(e)})
        )
    else:
        # 确保 HTTP 响应能被 JSON 解析
        try:
            resp_json = res.json()
        except Exception:
            resp_json = {"error": res.text}
        finally:
            logger.info(f"[example_handler HTTP响应] {resp_json}")
            mq.sendMsg(
                settings.aimaster.publishTopic[0],
                orjson.dumps({"source": orjson.loads(data), "data": resp_json}),
            )
        pass
