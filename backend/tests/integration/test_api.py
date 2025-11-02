"""API 整合測試"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """測試根端點"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_check():
    """測試健康檢查端點"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_simulation():
    """測試建立模擬任務"""
    parameters = {
        "reynolds_number": 100.0,
        "nx": 21,
        "ny": 21,
        "alpha_u": 0.7,
        "alpha_p": 1.0,
        "max_iter": 500,
        "tolerance": 1e-4,
        "lid_velocity": 1.0
    }

    response = client.post("/api/simulations", json=parameters)
    assert response.status_code == 201

    data = response.json()
    assert "job_id" in data
    assert data["status"] == "PENDING"
    assert "parameters" in data


def test_get_simulation_status():
    """測試查詢模擬狀態"""
    # 先建立任務
    parameters = {
        "reynolds_number": 100.0,
        "nx": 11,
        "ny": 11,
        "max_iter": 100
    }

    create_response = client.post("/api/simulations", json=parameters)
    job_id = create_response.json()["job_id"]

    # 查詢狀態
    response = client.get(f"/api/simulations/{job_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["job_id"] == job_id
    assert data["status"] in ["PENDING", "RUNNING", "COMPLETED", "FAILED"]


def test_get_simulation_not_found():
    """測試查詢不存在的任務"""
    response = client.get("/api/simulations/non-existent-id")
    assert response.status_code == 404


def test_create_simulation_invalid_parameters():
    """測試無效參數"""
    parameters = {
        "reynolds_number": -100.0,  # 無效: 負數
        "nx": 21,
        "ny": 21
    }

    response = client.post("/api/simulations", json=parameters)
    assert response.status_code == 422  # Validation error
