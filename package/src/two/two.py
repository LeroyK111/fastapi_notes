from fastapi import APIRouter


router = APIRouter()


# !组件two路由
@router.get("/", tags=["two"])
async def read_users():
    return {"message": "这里是two路由"}
