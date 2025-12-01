#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
socket 转为其他协议
"""

import asyncio
import json
from typing import Dict
from loguru import logger


class AsyncClient(object):
    name = "客户端"

    def __init__(self, host, port, receQueue):
        self.host = host
        self.port = port
        self.sendQueue = asyncio.Queue()
        self.receQueue = receQueue
        self.reader = None
        self.writer = None

    @classmethod
    def setName(cls, n: str):
        cls.name = n

    async def sendMsg(self, msg: Dict):
        """
        添加信息 到 发送队列
        """
        logger.info(f"从意识空间 发送到 输出节点{msg}")
        await self.sendQueue.put(json.dumps(msg).encode())

    async def sendLoop(self):
        """
        从意识空间 发送到 输出节点
        """
        try:
            while True:
                msg = await self.sendQueue.get()
                if not msg:
                    continue
                self.writer.write(msg)
                await self.writer.drain()
                self.sendQueue.task_done()
        except Exception as identifier:
            logger.error("输出节点 发送问题", identifier)
        finally:
            if self.writer:
                self.writer.close()
                await self.writer.wait_closed()

    async def receLoop(self):
        """
        从输出节点 发送到 意识空间
        """
        try:
            while True:
                data = await self.reader.read(1024)
                if not data:
                    break
                node = json.loads(data.decode())
                await self.receQueue.put(node)
        except Exception as identifier:
            logger.error("输出节点 接收问题", identifier)

    async def testLoopSend(self):
        while True:
            await self.sendMsg({"测试接口": [1, True]})
            await asyncio.sleep(1)

    async def createInit(self):
        """
        建立连接并启动读写任务
        """
        try:
            # 使用 asyncio.open_connection 建立连接
            self.reader, self.writer = await asyncio.open_connection(
                self.host, self.port
            )
            logger.info(f"输出节点 发送端 建立 {self.host}:{self.port}")
            # 启动独立的读写任务
            async with asyncio.TaskGroup() as tg:
                tg.create_task(self.sendLoop())
                tg.create_task(self.receLoop())
                # tg.create_task(self.testLoopSend())

        except Exception as identifier:
            logger.error(f"输出节点 发送端 {identifier}")

    async def offConnect(self):
        """
        关闭客户端连接
        """
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            logger.info(f"输出节点 客户端关闭 {self.host}:{self.port}")
