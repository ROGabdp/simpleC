"""WebSocket 端點"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import json

router = APIRouter()


class ConnectionManager:
    """WebSocket 連線管理器"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, job_id: str, websocket: WebSocket):
        """建立連線"""
        await websocket.accept()
        self.active_connections[job_id] = websocket

    def disconnect(self, job_id: str):
        """斷開連線"""
        if job_id in self.active_connections:
            del self.active_connections[job_id]

    async def send_progress(self, job_id: str, data: dict):
        """發送進度更新"""
        if job_id in self.active_connections:
            try:
                await self.active_connections[job_id].send_json({
                    "type": "progress",
                    "data": data
                })
            except Exception:
                # 連線已斷開,移除
                self.disconnect(job_id)

    async def send_completion(self, job_id: str, success: bool, message: str = ""):
        """發送完成訊息"""
        if job_id in self.active_connections:
            try:
                await self.active_connections[job_id].send_json({
                    "type": "completed" if success else "error",
                    "message": message
                })
            except Exception:
                self.disconnect(job_id)


# 全域單例
manager = ConnectionManager()


@router.websocket("/simulation/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """WebSocket 端點用於即時進度更新"""
    await manager.connect(job_id, websocket)
    try:
        while True:
            # 保持連線,等待訊息
            data = await websocket.receive_text()
            # 客戶端可以發送 ping 保持連線
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(job_id)
