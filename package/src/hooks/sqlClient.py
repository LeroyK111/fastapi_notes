"""
这里我们构造一个sql数据库客户端钩子
"""
from sqlalchemy import create_engine, text, exc

engine = create_engine("mysql://root:liukai@localhost:3306/fastApiTest")


async def get_db(SQL: str) -> dict:
    with engine.connect() as conn:
        try:
            data = conn.execute(text(SQL))
        except exc.IntegrityError:
            data = {"status": 0, "message": "The result object does not return a value!", "data": None}
            conn.commit()
        except Exception as e:
            data = {"status": -1, "message": e}
        else:
            # 成功了就将数据进行转换[{},{}]这样的形式
            data = {"status": 1, "data": data}
            conn.commit()
    return data
