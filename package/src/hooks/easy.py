from typing import Union
from fastapi import Depends, Cookie, HTTPException, Header

"""
创建一个钩子
"""


# !这个钩子函数用在路径请求之前。
async def common_parameters(q: Union[str, None] = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}


"""
嵌套路由
"""


# !第一层，先被处理
def query_extractor(q: Union[str, None] = None):
    return q


# !第二层，后被处理
def query_or_cookie_extractor(
    q: str = Depends(query_extractor),
    last_query: Union[str, None] = Cookie(default=None),
):
    if not q:
        return last_query
    return q


"""
有些时候，不需要返回值，而是需要直接拦截请求，那我们可以使用如下方案。
"""


async def verify_token(x_token: str = Header()):
    if x_token != "fake-super-secret-token":
        # *这里触发异常即可，拦截请求
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: str = Header()):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    # *这个返回值无法被路径接收到，但是可以被嵌套钩子复用。。
    return x_key
