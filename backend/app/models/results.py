"""求解結果相關資料模型"""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class SolverProgress(BaseModel):
    """求解進度資訊"""

    job_id: str = Field(..., description="任務 ID")
    iteration: int = Field(..., description="當前迭代次數")
    residual_u: float = Field(..., description="u 速度殘差")
    residual_v: float = Field(..., description="v 速度殘差")
    elapsed_time: float = Field(..., description="已執行時間 (秒)")
    estimated_remaining: Optional[float] = Field(
        None,
        description="預估剩餘時間 (秒)"
    )

    class Config:
        schema_extra = {
            "example": {
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "iteration": 100,
                "residual_u": 0.001,
                "residual_v": 0.0015,
                "elapsed_time": 5.2,
                "estimated_remaining": 15.0
            }
        }


class FlowFieldResults(BaseModel):
    """流場結果資料"""

    job_id: str = Field(..., description="任務 ID")
    pressure: List[List[float]] = Field(..., description="壓力場 (ny x nx)")
    velocity_u: List[List[float]] = Field(..., description="u 速度場 (ny x (nx-1))")
    velocity_v: List[List[float]] = Field(..., description="v 速度場 ((ny-1) x nx)")
    x_coords: List[float] = Field(..., description="x 座標")
    y_coords: List[float] = Field(..., description="y 座標")
    convergence_history: List[Dict] = Field(
        ...,
        description="收斂歷史 [{iteration, residual_u, residual_v}]"
    )
    final_residuals: Dict[str, float] = Field(
        ...,
        description="最終殘差 {u, v}"
    )

    class Config:
        schema_extra = {
            "example": {
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "pressure": [[0.0, 0.1], [0.2, 0.3]],
                "velocity_u": [[1.0, 0.9]],
                "velocity_v": [[0.0], [0.1]],
                "x_coords": [0.0, 0.5, 1.0],
                "y_coords": [0.0, 0.5, 1.0],
                "convergence_history": [
                    {"iteration": 100, "residual_u": 0.01, "residual_v": 0.01}
                ],
                "final_residuals": {"u": 1e-6, "v": 1e-6}
            }
        }
