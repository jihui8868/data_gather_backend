from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReadingBase(BaseModel):
    device_id: str = Field(min_length=1, max_length=64, examples=["sensor-001"])
    collected_at: datetime | None = Field(default=None, description="采集时间, 默认为当前时间")


class TemperatureCreate(ReadingBase):
    value: float = Field(ge=-273.15, le=1000, description="温度 ℃", examples=[25.6])


class HumidityCreate(ReadingBase):
    value: float = Field(ge=0, le=100, description="相对湿度 %RH", examples=[55.2])


class PressureCreate(ReadingBase):
    value: float = Field(ge=0, description="压力 kPa", examples=[101.3])


class ReadingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: str
    value: float
    unit: str
    collected_at: datetime
    created_at: datetime


class ReadingPage(BaseModel):
    total: int
    items: list[ReadingOut]
