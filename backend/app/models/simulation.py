"""模擬任務相關資料模型"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator


class JobStatus(str, Enum):
    """任務狀態列舉"""
    PENDING = "PENDING"      # 已建立,等待執行
    RUNNING = "RUNNING"      # 正在執行
    COMPLETED = "COMPLETED"  # 成功完成
    FAILED = "FAILED"        # 執行失敗


class SimulationParameters(BaseModel):
    """模擬輸入參數"""

    reynolds_number: float = Field(
        ...,
        gt=0,
        lt=100000,
        description="Reynolds 數"
    )
    nx: int = Field(
        41,
        ge=10,
        le=200,
        description="x 方向網格數"
    )
    ny: int = Field(
        41,
        ge=10,
        le=200,
        description="y 方向網格數"
    )
    alpha_u: float = Field(
        0.7,
        gt=0,
        le=1.0,
        description="速度鬆弛因子"
    )
    alpha_p: float = Field(
        1.0,
        gt=0,
        le=1.0,
        description="壓力鬆弛因子 (SIMPLEC 通常=1.0)"
    )
    max_iter: int = Field(
        10000,
        ge=100,
        le=100000,
        description="最大迭代次數"
    )
    tolerance: float = Field(
        1e-5,
        gt=0,
        lt=1.0,
        description="收斂標準"
    )
    lid_velocity: float = Field(
        1.0,
        gt=0,
        description="上蓋速度"
    )

    @validator('nx', 'ny')
    def check_grid_size(cls, v):
        """檢查網格尺寸並發出警告"""
        if v > 100:
            # 大網格可能需要較長計算時間
            pass
        return v

    class Config:
        schema_extra = {
            "example": {
                "reynolds_number": 100.0,
                "nx": 41,
                "ny": 41,
                "alpha_u": 0.7,
                "alpha_p": 1.0,
                "max_iter": 10000,
                "tolerance": 1e-5,
                "lid_velocity": 1.0
            }
        }


class SimulationJob(BaseModel):
    """模擬任務"""

    job_id: str = Field(..., description="任務唯一識別碼")
    parameters: SimulationParameters = Field(..., description="輸入參數")
    status: JobStatus = Field(..., description="任務狀態")
    created_at: datetime = Field(..., description="建立時間")
    started_at: Optional[datetime] = Field(None, description="開始執行時間")
    completed_at: Optional[datetime] = Field(None, description="完成時間")
    error_message: Optional[str] = Field(None, description="錯誤訊息 (若失敗)")

    class Config:
        schema_extra = {
            "example": {
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "parameters": {
                    "reynolds_number": 100.0,
                    "nx": 41,
                    "ny": 41
                },
                "status": "RUNNING",
                "created_at": "2025-11-02T10:00:00",
                "started_at": "2025-11-02T10:00:01",
                "completed_at": None,
                "error_message": None
            }
        }
