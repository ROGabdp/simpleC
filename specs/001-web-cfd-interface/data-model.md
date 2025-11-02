# Data Model

**Feature**: CFD 求解器 Web 介面
**Date**: 2025-11-02

## 概述

本文件定義系統中所有資料實體的結構、驗證規則和關係。

---

## 實體定義

### 1. SimulationParameters (輸入參數)

**用途**: 代表使用者輸入的所有 CFD 求解器參數

**欄位**:

| 欄位名稱 | 型別 | 必填 | 預設值 | 驗證規則 | 說明 |
|---------|------|------|--------|---------|------|
| reynolds_number | float | ✅ | - | > 0, < 100000 | Reynolds 數 |
| nx | int | ✅ | 41 | >= 10, <= 200 | x 方向網格數 |
| ny | int | ✅ | 41 | >= 10, <= 200 | y 方向網格數 |
| alpha_u | float | ❌ | 0.7 | > 0, <= 1.0 | 速度鬆弛因子 |
| alpha_p | float | ❌ | 1.0 | > 0, <= 1.0 | 壓力鬆弛因子 (SIMPLEC 通常=1.0) |
| max_iter | int | ❌ | 10000 | >= 100, <= 100000 | 最大迭代次數 |
| tolerance | float | ❌ | 1e-5 | > 0, < 1.0 | 收斂標準 |
| lid_velocity | float | ❌ | 1.0 | > 0 | 上蓋速度 |

**Pydantic 模型**:
```python
from pydantic import BaseModel, Field, validator

class SimulationParameters(BaseModel):
    reynolds_number: float = Field(..., gt=0, lt=100000, description="Reynolds number")
    nx: int = Field(41, ge=10, le=200, description="Grid points in x")
    ny: int = Field(41, ge=10, le=200, description="Grid points in y")
    alpha_u: float = Field(0.7, gt=0, le=1.0, description="Velocity relaxation factor")
    alpha_p: float = Field(1.0, gt=0, le=1.0, description="Pressure relaxation factor")
    max_iter: int = Field(10000, ge=100, le=100000)
    tolerance: float = Field(1e-5, gt=0, lt=1.0)
    lid_velocity: float = Field(1.0, gt=0)

    @validator('nx', 'ny')
    def warn_large_grid(cls, v):
        if v > 100:
            # 可以加入警告邏輯
            pass
        return v
```

---

### 2. SimulationJob (模擬任務)

**用途**: 追蹤一次完整的 CFD 求解任務

**欄位**:

| 欄位名稱 | 型別 | 必填 | 說明 |
|---------|------|------|------|
| job_id | str (UUID) | ✅ | 唯一任務識別碼 |
| parameters | SimulationParameters | ✅ | 輸入參數 |
| status | JobStatus (enum) | ✅ | 任務狀態 |
| created_at | datetime | ✅ | 建立時間 |
| started_at | datetime | ❌ | 開始執行時間 |
| completed_at | datetime | ❌ | 完成時間 |
| error_message | str | ❌ | 錯誤訊息 (若失敗) |

**狀態列舉**:
```python
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "PENDING"      # 已建立,等待執行
    RUNNING = "RUNNING"      # 正在執行
    COMPLETED = "COMPLETED"  # 成功完成
    FAILED = "FAILED"        # 執行失敗
```

**Pydantic 模型**:
```python
from datetime import datetime
from typing import Optional
from uuid import UUID

class SimulationJob(BaseModel):
    job_id: UUID
    parameters: SimulationParameters
    status: JobStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
```

**狀態轉換**:
```
PENDING → RUNNING → COMPLETED
         ↓
        FAILED
```

---

### 3. SolverProgress (求解進度)

**用途**: WebSocket 即時推送的進度資訊

**欄位**:

| 欄位名稱 | 型別 | 說明 |
|---------|------|------|
| job_id | str | 任務 ID |
| iteration | int | 當前迭代次數 |
| residual_u | float | u 速度殘差 |
| residual_v | float | v 速度殘差 |
| elapsed_time | float | 已執行時間 (秒) |
| estimated_remaining | float (可選) | 預估剩餘時間 (秒) |

**Pydantic 模型**:
```python
class SolverProgress(BaseModel):
    job_id: str
    iteration: int
    residual_u: float
    residual_v: float
    elapsed_time: float
    estimated_remaining: Optional[float] = None
```

---

### 4. FlowFieldResults (流場結果)

**用途**: 求解完成後的流場資料

**欄位**:

| 欄位名稱 | 型別 | 維度 | 說明 |
|---------|------|------|------|
| job_id | str | - | 任務 ID |
| pressure | List[List[float]] | (ny, nx) | 壓力場 |
| velocity_u | List[List[float]] | (ny, nx-1) | u 速度場 |
| velocity_v | List[List[float]] | (ny-1, nx) | v 速度場 |
| x_coords | List[float] | (nx,) | x 座標 |
| y_coords | List[float] | (ny,) | y 座標 |
| convergence_history | List[dict] | - | 收斂歷史 |
| final_residuals | dict | - | 最終殘差 |

**Pydantic 模型**:
```python
class FlowFieldResults(BaseModel):
    job_id: str
    pressure: List[List[float]]
    velocity_u: List[List[float]]
    velocity_v: List[List[float]]
    x_coords: List[float]
    y_coords: List[float]
    convergence_history: List[dict]  # [{iteration: int, residual_u: float, residual_v: float}]
    final_residuals: dict  # {u: float, v: float}

    class Config:
        schema_extra = {
            "example": {
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "pressure": [[0.0, 0.1], [0.2, 0.3]],
                "velocity_u": [[1.0, 0.9]],
                "velocity_v": [[0.0], [0.1]],
                "x_coords": [0.0, 0.5, 1.0],
                "y_coords": [0.0, 0.5, 1.0],
                "convergence_history": [{"iteration": 100, "residual_u": 0.01, "residual_v": 0.01}],
                "final_residuals": {"u": 1e-6, "v": 1e-6}
            }
        }
```

---

## 資料關係

```
SimulationParameters (1) ──< SimulationJob (1) ──< SolverProgress (N)
                                         │
                                         └──< FlowFieldResults (1)
```

**說明**:
- 一個 SimulationJob 包含一組 SimulationParameters
- 一個 SimulationJob 可產生多個 SolverProgress (即時更新)
- 一個 SimulationJob 產生一個 FlowFieldResults (完成時)

---

## 驗證規則摘要

1. **參數範圍檢查**:
   - Reynolds number: 0 < Re < 100000
   - 網格尺寸: 10 ≤ nx, ny ≤ 200
   - 鬆弛因子: 0 < alpha ≤ 1.0

2. **網格尺寸警告**:
   - nx或ny > 100: 警告計算時間可能過長

3. **狀態轉換限制**:
   - PENDING → RUNNING: 僅當求解器啟動時
   - RUNNING → COMPLETED/FAILED: 僅當求解器結束時
   - 不可逆轉 (無法從 COMPLETED 回到 RUNNING)

4. **陣列維度一致性**:
   - pressure: (ny, nx)
   - velocity_u: (ny, nx-1)
   - velocity_v: (ny-1, nx)
   - 交錯網格要求

---

## 儲存策略 (MVP)

**記憶體暫存**:
- 使用 Python 字典儲存當前任務
- 單使用者模式,僅保存一個活躍任務
- 無持久化 (重啟清空)

**未來擴展**:
- 檔案系統: 儲存為 JSON
- 資料庫: SQLite 或 PostgreSQL
- 物件儲存: S3 for large results
