from .server import *
from .client import *
import asyncio

"""
输入输出节点
"""

receQueue = asyncio.Queue()
inputNet = {
    "vision": AsyncServer("127.0.0.1", 60001, receQueue),
}


responseQueue = asyncio.Queue()
outputNet = {
    "talk": AsyncClient("127.0.0.1", 50001, responseQueue),
}
