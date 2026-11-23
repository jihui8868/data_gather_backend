from datetime import datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ReadingMixin:
    """采集数据公共字段"""

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[str] = mapped_column(String(64), index=True)
    value: Mapped[float] = mapped_column(Float)
    collected_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class Temperature(ReadingMixin, Base):
    """温度, 单位 ℃"""

    __tablename__ = "temperature"


class Humidity(ReadingMixin, Base):
    """湿度, 单位 %RH"""

    __tablename__ = "humidity"


class Pressure(ReadingMixin, Base):
    """压力, 单位 kPa"""

    __tablename__ = "pressure"
