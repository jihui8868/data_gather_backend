from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Humidity, Pressure, Temperature
from app.schemas import (
    HumidityCreate,
    PressureCreate,
    ReadingBase,
    ReadingOut,
    ReadingPage,
    TemperatureCreate,
)

DbSession = Annotated[Session, Depends(get_db)]


def build_router(
    *, prefix: str, tag: str, model: type, create_schema: type[ReadingBase], unit: str
) -> APIRouter:
    """为一种采集数据生成 保存 / 列表查询 / 单条查询 三个接口"""
    router = APIRouter(prefix=prefix, tags=[tag])

    def to_out(obj) -> ReadingOut:
        return ReadingOut.model_validate({**obj.__dict__, "unit": unit})

    @router.post(
        "", response_model=ReadingOut, status_code=status.HTTP_201_CREATED, summary=f"保存{tag}数据"
    )
    def create(payload: create_schema, db: DbSession):  # type: ignore[valid-type]
        data = payload.model_dump()
        data["collected_at"] = data["collected_at"] or datetime.now()
        obj = model(**data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return to_out(obj)

    @router.get("", response_model=ReadingPage, summary=f"查询{tag}数据")
    def list_readings(
        db: DbSession,
        device_id: str | None = Query(None, description="设备ID"),
        start: datetime | None = Query(None, description="采集开始时间(含)"),
        end: datetime | None = Query(None, description="采集结束时间(含)"),
        offset: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=500),
    ):
        conditions = []
        if device_id:
            conditions.append(model.device_id == device_id)
        if start:
            conditions.append(model.collected_at >= start)
        if end:
            conditions.append(model.collected_at <= end)

        total = db.scalar(select(func.count()).select_from(model).where(*conditions))
        rows = db.scalars(
            select(model)
            .where(*conditions)
            .order_by(model.collected_at.desc(), model.id.desc())
            .offset(offset)
            .limit(limit)
        ).all()
        return ReadingPage(total=total or 0, items=[to_out(r) for r in rows])

    @router.get("/{reading_id}", response_model=ReadingOut, summary=f"按ID查询{tag}数据")
    def get_reading(reading_id: int, db: DbSession):
        obj = db.get(model, reading_id)
        if obj is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"{tag}数据不存在")
        return to_out(obj)

    return router


temperature_router = build_router(
    prefix="/api/temperatures", tag="温度", model=Temperature, create_schema=TemperatureCreate, unit="℃"
)
humidity_router = build_router(
    prefix="/api/humidities", tag="湿度", model=Humidity, create_schema=HumidityCreate, unit="%RH"
)
pressure_router = build_router(
    prefix="/api/pressures", tag="压力", model=Pressure, create_schema=PressureCreate, unit="kPa"
)
