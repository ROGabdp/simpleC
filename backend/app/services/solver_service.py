"""求解器服務 - 管理模擬任務"""
from datetime import datetime
from typing import Dict, Optional
import uuid
import asyncio

from app.models.simulation import SimulationJob, SimulationParameters, JobStatus
from app.models.results import FlowFieldResults
from app.core.solver import solve_cavity_flow
from app.api.websocket import manager


# 記憶體儲存 (MVP 階段)
jobs_store: Dict[str, SimulationJob] = {}
results_store: Dict[str, Dict] = {}


class SolverService:
    """求解器服務"""

    @staticmethod
    def create_job(parameters: SimulationParameters) -> SimulationJob:
        """建立新的模擬任務"""
        job_id = str(uuid.uuid4())
        job = SimulationJob(
            job_id=job_id,
            parameters=parameters,
            status=JobStatus.PENDING,
            created_at=datetime.now()
        )
        jobs_store[job_id] = job
        return job

    @staticmethod
    def get_job(job_id: str) -> Optional[SimulationJob]:
        """取得任務資訊"""
        return jobs_store.get(job_id)

    @staticmethod
    def get_results(job_id: str) -> Optional[FlowFieldResults]:
        """取得模擬結果"""
        if job_id not in results_store:
            return None

        data = results_store[job_id]
        return FlowFieldResults(
            job_id=job_id,
            **data
        )

    @staticmethod
    async def run_simulation(job_id: str):
        """執行模擬 (背景任務)"""
        job = jobs_store.get(job_id)
        if not job:
            return

        # 更新狀態為 RUNNING
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now()

        try:
            # 定義同步進度回調 (在執行緒中呼叫)
            def progress_callback(progress_data: dict):
                """進度回調 - 透過 WebSocket 發送進度"""
                # 使用 asyncio.run_coroutine_threadsafe 從執行緒安全地呼叫協程
                asyncio.run_coroutine_threadsafe(
                    manager.send_progress(job_id, progress_data),
                    loop
                )

            # 在執行緒池中執行求解器
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                solve_cavity_flow,
                job.parameters,
                progress_callback
            )

            # 儲存結果
            results_store[job_id] = result

            # 更新狀態為 COMPLETED
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now()

            # 發送完成訊息
            await manager.send_completion(job_id, True, "模擬已完成")

        except Exception as e:
            # 更新狀態為 FAILED
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now()

            # 發送錯誤訊息
            await manager.send_completion(job_id, False, f"模擬失敗: {str(e)}")


solver_service = SolverService()
