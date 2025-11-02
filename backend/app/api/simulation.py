"""模擬 REST API 端點"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional

from app.models.simulation import SimulationJob, SimulationParameters
from app.models.results import FlowFieldResults
from app.services.solver_service import solver_service

router = APIRouter()


@router.post("", response_model=SimulationJob, status_code=201)
async def create_simulation(
    parameters: SimulationParameters,
    background_tasks: BackgroundTasks
):
    """
    建立新的模擬任務

    接收模擬參數,建立任務並在背景執行求解器
    """
    # 建立任務
    job = solver_service.create_job(parameters)

    # 啟動背景任務
    background_tasks.add_task(solver_service.run_simulation, job.job_id)

    return job


@router.get("/{job_id}", response_model=SimulationJob)
async def get_simulation_status(job_id: str):
    """
    查詢模擬任務狀態

    返回任務的當前狀態 (PENDING, RUNNING, COMPLETED, FAILED)
    """
    job = solver_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="任務不存在")

    return job


@router.get("/{job_id}/results", response_model=FlowFieldResults)
async def get_simulation_results(job_id: str):
    """
    取得模擬結果

    僅當任務狀態為 COMPLETED 時可用
    """
    job = solver_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="任務不存在")

    if job.status != "COMPLETED":
        raise HTTPException(
            status_code=400,
            detail=f"任務尚未完成,當前狀態: {job.status}"
        )

    results = solver_service.get_results(job_id)
    if not results:
        raise HTTPException(status_code=404, detail="結果不存在")

    return results


@router.delete("/{job_id}", status_code=204)
async def delete_simulation(job_id: str):
    """
    取消/刪除模擬任務

    注意: MVP 版本不支援取消正在執行的任務
    """
    job = solver_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="任務不存在")

    # MVP: 僅支援刪除已完成或失敗的任務
    if job.status == "RUNNING":
        raise HTTPException(
            status_code=400,
            detail="無法刪除正在執行的任務"
        )

    # TODO: 實作刪除邏輯
    return None
