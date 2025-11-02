"""求解器單元測試"""
import pytest
from app.models.simulation import SimulationParameters
from app.core.solver import solve_cavity_flow


def test_solve_cavity_flow_converges():
    """測試求解器是否收斂"""
    parameters = SimulationParameters(
        reynolds_number=100.0,
        nx=21,
        ny=21,
        max_iter=1000,
        tolerance=1e-4
    )

    results = solve_cavity_flow(parameters)

    # 驗證結果包含必要欄位
    assert "pressure" in results
    assert "velocity_u" in results
    assert "velocity_v" in results
    assert "final_residuals" in results
    assert "converged" in results

    # 驗證收斂
    assert results["final_residuals"]["u"] < 1e-4
    assert results["final_residuals"]["v"] < 1e-4
    assert results["converged"] is True


def test_solve_cavity_flow_dimensions():
    """測試求解器輸出維度正確"""
    parameters = SimulationParameters(
        reynolds_number=100.0,
        nx=21,
        ny=21,
        max_iter=500
    )

    results = solve_cavity_flow(parameters)

    # 驗證陣列維度
    assert len(results["pressure"]) == 21  # ny
    assert len(results["pressure"][0]) == 21  # nx

    assert len(results["velocity_u"]) == 21  # ny
    assert len(results["velocity_u"][0]) == 20  # nx - 1

    assert len(results["velocity_v"]) == 20  # ny - 1
    assert len(results["velocity_v"][0]) == 21  # nx

    assert len(results["x_coords"]) == 21
    assert len(results["y_coords"]) == 21


def test_solve_cavity_flow_with_callback():
    """測試求解器進度回調"""
    parameters = SimulationParameters(
        reynolds_number=100.0,
        nx=11,
        ny=11,
        max_iter=100
    )

    progress_calls = []

    def progress_callback(data):
        progress_calls.append(data)

    results = solve_cavity_flow(parameters, progress_callback)

    # 驗證回調被呼叫
    assert len(progress_calls) > 0

    # 驗證回調資料格式
    for call in progress_calls:
        assert "iteration" in call
        assert "residual_u" in call
        assert "residual_v" in call
        assert "elapsed_time" in call
