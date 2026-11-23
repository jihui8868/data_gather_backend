# 数据采集演示后台

Python 3.13 + FastAPI + SQLAlchemy 2 + SQLite，使用 uv 管理。

## 运行

```bash
uv sync
uv run uvicorn app.main:app --reload
```

接口文档：http://127.0.0.1:8000/docs

## 接口

| 数据 | 保存 | 列表查询 | 按 ID 查询 |
|------|------|----------|-----------|
| 温度 (℃)   | `POST /api/temperatures` | `GET /api/temperatures` | `GET /api/temperatures/{id}` |
| 湿度 (%RH) | `POST /api/humidities`   | `GET /api/humidities`   | `GET /api/humidities/{id}`   |
| 压力 (kPa) | `POST /api/pressures`    | `GET /api/pressures`    | `GET /api/pressures/{id}`    |

保存请求体（`collected_at` 可省略，默认当前时间）：

```json
{"device_id": "sensor-001", "value": 25.6, "collected_at": "2026-11-24T10:00:00"}
```

列表查询参数：`device_id`、`start`、`end`（采集时间范围）、`offset`、`limit`（默认 20，最大 500），返回 `{"total": n, "items": [...]}`，按采集时间倒序。

示例：

```bash
curl -X POST localhost:8000/api/temperatures -H 'Content-Type: application/json' \
  -d '{"device_id":"sensor-001","value":25.6}'
curl 'localhost:8000/api/temperatures?device_id=sensor-001&start=2026-11-24T00:00:00'
```

## 测试

```bash
uv run pytest
```

数据库默认 `./data_gather.db`，可通过环境变量 `DATABASE_URL` 修改。
