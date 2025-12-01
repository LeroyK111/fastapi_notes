#!/usr/bin/python
# -*- coding: utf-8 -*-

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, BaseModel, field_validator
from typing import Literal, List, Optional, Tuple
from pathlib import Path

# -------------------------- 路径配置 --------------------------
SETTING_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SETTING_DIR.parent.parent
ENV_FILE_PATH = PROJECT_ROOT / ".env"


class AIMasterConfig(BaseModel):
    # 小驼峰字段名 + 显式绑定原.env变量名（确保配置不失效）
    # flowInformationUrl: str = Field(
    #     default="http://172.29.10.42:8856/test/solution",
    #     description="flow_information_url",
    # )
    # sendTo: str = Field(
    #     default="http://172.29.10.42:8856/test/solution_infer",
    #     description="send_to",
    # )
    # visionBuilderTempDetailUrl: str = Field(
    #     default="http://192.168.77.158:9905",
    #     description="vision_builder",
    # )
    # Optional[List[str]] 类型保留，默认值 None
    subscribeTopic: Optional[List[str]] = Field(
        default=["demo"],
        description="AIMaster 相关的 MQTT 订阅主题列表（.env 用逗号分隔）",
    )
    publishTopic: Optional[List[str]] = Field(
        default=["demo"],
        description="AIMaster 相关的 MQTT 发布主题列表（.env 用逗号分隔）",
    )

    # 解析器：适配小驼峰字段名，将逗号分隔字符串转为列表
    @field_validator("subscribeTopic", "publishTopic", mode="before")
    def parse_comma_separated_list(cls, value):
        """
        解析逻辑：
        - 若.env中配置为空/None → 返回 ["demo"]
        - 若为字符串 → 逗号分隔转为列表（过滤空值）
        - 若为列表 → 直接返回
        """
        if isinstance(value, str):
            result = [item.strip() for item in value.split(",") if item.strip()]
            return result if result else None
        elif isinstance(value, list):
            return value
        else:
            return None


class MQTTConfig(BaseModel):
    host: str = Field(default="172.29.10.42", description="MQTT 服务器地址")
    port: int = Field(default=21883, description="MQTT 服务器端口")
    username: str = Field(default="admin", description="MQTT username")
    password: str = Field(default="deepSight123", description="MQTT password")


class SecondaryAgencyConfig(BaseModel):
    host: str = Field(default="172.29.10.42", description="二级代理服务器地址")
    port: int = Field(default=11883, description="二级代理服务器端口")
    workers: int = Field(default=1, ge=1, description="工作进程数（至少 1）")
    logLevel: Literal["debug", "info", "warning", "error", "critical"] = Field(
        default="info", description="日志级别"
    )
    reload: bool = Field(default=False, description="是否热重载")


# -------------------------- 2. 主配置类 --------------------------
class Settings(BaseSettings):
    aimaster: AIMasterConfig = Field(default_factory=AIMasterConfig)
    mqtt: MQTTConfig = Field(default_factory=MQTTConfig)
    secondary_agency: SecondaryAgencyConfig = Field(
        default_factory=SecondaryAgencyConfig
    )

    # Pydantic V2 新版配置方式
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE_PATH),
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="_",
        extra="ignore",
    )


# -------------------------- 全局实例 --------------------------
settings = Settings()

# -------------------------- 调试用 --------------------------
if __name__ == "__main__":
    print(f"settings.aimaster", settings.aimaster.model_dump_json())
    print(f"settings.secondary_agency", settings.secondary_agency.model_dump_json())
