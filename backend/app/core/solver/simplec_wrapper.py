"""SIMPLEC 求解器包裝器"""
import numpy as np
import time
from typing import Dict, Optional, Callable, List
from app.models.simulation import SimulationParameters


def solve_cavity_flow(
    parameters: SimulationParameters,
    progress_callback: Optional[Callable[[Dict], None]] = None
) -> Dict:
    """
    使用 SIMPLEC 演算法求解蓋驅動方腔流

    參數:
        parameters: 模擬參數
        progress_callback: 進度回調函式,接收 {iteration, residual_u, residual_v, elapsed_time}

    返回:
        包含流場資料的字典
    """
    # 提取參數
    NX = parameters.nx
    NY = parameters.ny
    U_lid = parameters.lid_velocity
    alpha_u = parameters.alpha_u
    alpha_p = parameters.alpha_p
    max_iter = parameters.max_iter
    tolerance = parameters.tolerance

    # 腔體尺寸
    LX = 1.0
    LY = 1.0
    dx = LX / (NX - 1)
    dy = LY / (NY - 1)

    # 流體性質 (從 Reynolds 數計算黏滯係數)
    rho = 1.0
    mu = rho * U_lid * LX / parameters.reynolds_number

    # 初始化變數
    p = np.zeros((NY, NX))
    p_prime = np.zeros_like(p)

    u = np.zeros((NY, NX - 1))
    v = np.zeros((NY - 1, NX))

    u_star = u.copy()
    v_star = v.copy()

    # 收斂歷史
    convergence_history: List[Dict] = []

    # 開始計時
    start_time = time.time()

    # 主迭代迴圈
    for it in range(max_iter):
        u_old_iter = u.copy()
        v_old_iter = v.copy()

        # === 步驟 A: 求解動量方程式 (速度預測) ===

        # A1. 求解 u-動量方程式
        for j in range(1, NY - 1):
            for i in range(1, NX - 2):
                # 對流項
                conv_u_E = 0.5 * rho * dy * (u[j, i] + u[j, i + 1])
                conv_u_W = 0.5 * rho * dy * (u[j, i - 1] + u[j, i])
                conv_v_N = 0.5 * rho * dx * (v[j, i] + v[j, i + 1])
                conv_v_S = 0.5 * rho * dx * (v[j - 1, i] + v[j - 1, i + 1])

                # 擴散項
                diff_u_E = mu * dy / dx
                diff_u_W = mu * dy / dx
                diff_u_N = mu * dx / dy
                diff_u_S = mu * dx / dy

                # 係數
                a_E = diff_u_E + max(0, -conv_u_E)
                a_W = diff_u_W + max(0, conv_u_W)
                a_N = diff_u_N + max(0, -conv_v_N)
                a_S = diff_u_S + max(0, conv_v_S)

                # 壓力梯度項
                source_p_u = (p[j, i] - p[j, i + 1]) * dy

                # 中心點係數
                a_P_u = a_E + a_W + a_N + a_S + \
                    (conv_u_E - conv_u_W) + (conv_v_N - conv_v_S)

                # 預測速度
                numerator = (a_E * u[j, i+1] + a_W * u[j, i-1] +
                           a_N * u[j+1, i] + a_S * u[j-1, i] + source_p_u)
                u_star[j, i] = (1 - alpha_u) * u[j, i] + alpha_u * (numerator / a_P_u)

        # A2. 求解 v-動量方程式
        for j in range(1, NY - 2):
            for i in range(1, NX - 1):
                # 對流項
                conv_u_E = 0.5 * rho * dy * (u[j, i] + u[j + 1, i])
                conv_u_W = 0.5 * rho * dy * (u[j, i - 1] + u[j + 1, i - 1])
                conv_v_N = 0.5 * rho * dx * (v[j, i] + v[j + 1, i])
                conv_v_S = 0.5 * rho * dx * (v[j - 1, i] + v[j, i])

                # 擴散項
                diff_v_E = mu * dy / dx
                diff_v_W = mu * dy / dx
                diff_v_N = mu * dx / dy
                diff_v_S = mu * dx / dy

                # 係數
                a_E = diff_v_E + max(0, -conv_u_E)
                a_W = diff_v_W + max(0, conv_u_W)
                a_N = diff_v_N + max(0, -conv_v_N)
                a_S = diff_v_S + max(0, conv_v_S)

                # 壓力梯度項
                source_p_v = (p[j, i] - p[j + 1, i]) * dx

                # 中心點係數
                a_P_v = a_E + a_W + a_N + a_S + \
                    (conv_u_E - conv_u_W) + (conv_v_N - conv_v_S)

                # 預測速度
                numerator = (a_E * v[j, i+1] + a_W * v[j, i-1] +
                           a_N * v[j+1, i] + a_S * v[j-1, i] + source_p_v)
                v_star[j, i] = (1 - alpha_u) * v[j, i] + alpha_u * (numerator / a_P_v)

        # === 步驟 B: 求解壓力修正方程式 ===
        p_prime[:, :] = 0
        for _ in range(50):  # 高斯-賽德爾迭代
            for j in range(1, NY - 1):
                for i in range(1, NX - 1):
                    # 簡化的 a_P (應為每個位置重新計算)
                    a_P_u_E = a_P_u if 'a_P_u' in locals() else 1.0
                    a_P_u_W = a_P_u if 'a_P_u' in locals() else 1.0
                    a_P_v_N = a_P_v if 'a_P_v' in locals() else 1.0
                    a_P_v_S = a_P_v if 'a_P_v' in locals() else 1.0

                    # SIMPLEC 的 d 因子
                    d_u_E = alpha_u * dy / a_P_u_E
                    d_u_W = alpha_u * dy / a_P_u_W
                    d_v_N = alpha_u * dx / a_P_v_N
                    d_v_S = alpha_u * dx / a_P_v_S

                    # 壓力修正方程式係數
                    a_E_p = rho * d_u_E * dy
                    a_W_p = rho * d_u_W * dy
                    a_N_p = rho * d_v_N * dx
                    a_S_p = rho * d_v_S * dx
                    a_P_p = a_E_p + a_W_p + a_N_p + a_S_p

                    # 質量不平衡
                    mass_imbalance = (rho * (u_star[j, i] - u_star[j, i-1]) * dy +
                                    rho * (v_star[j, i] - v_star[j-1, i]) * dx)

                    # 求解 p_prime
                    if a_P_p > 1e-12:
                        p_prime[j, i] = (a_E_p * p_prime[j, i+1] + a_W_p * p_prime[j, i-1] +
                                       a_N_p * p_prime[j+1, i] + a_S_p * p_prime[j-1, i] -
                                       mass_imbalance) / a_P_p

        # === 步驟 C: 修正壓力與速度 ===
        p += alpha_p * p_prime

        # 修正 u 速度
        for j in range(1, NY-1):
            for i in range(1, NX-2):
                d_u = alpha_u * dy / (a_P_u if 'a_P_u' in locals() else 1.0)
                u[j, i] = u_star[j, i] - d_u * (p_prime[j, i+1] - p_prime[j, i])

        # 修正 v 速度
        for j in range(1, NY-2):
            for i in range(1, NX-1):
                d_v = alpha_u * dx / (a_P_v if 'a_P_v' in locals() else 1.0)
                v[j, i] = v_star[j, i] - d_v * (p_prime[j+1, i] - p_prime[j, i])

        # === 步驟 D: 施加邊界條件 ===
        u[0, :] = 0.0
        u[-1, :] = 0.0
        u[:, 0] = 0.0
        u[:, -1] = 0.0

        v[:, 0] = 0.0
        v[:, -1] = 0.0
        v[0, :] = 0.0
        v[-1, :] = 0.0

        # 頂蓋速度
        u[NY-1, :] = U_lid

        # === 步驟 E: 檢查收斂 ===
        u_res = np.sqrt(np.sum((u - u_old_iter)**2)) / (np.sqrt(np.sum(u_old_iter**2)) + 1e-12)
        v_res = np.sqrt(np.sum((v - v_old_iter)**2)) / (np.sqrt(np.sum(v_old_iter**2)) + 1e-12)

        # 記錄收斂歷史
        if it % 10 == 0:
            elapsed = time.time() - start_time
            convergence_history.append({
                "iteration": it,
                "residual_u": float(u_res),
                "residual_v": float(v_res)
            })

            # 呼叫進度回調
            if progress_callback:
                progress_callback({
                    "iteration": it,
                    "residual_u": float(u_res),
                    "residual_v": float(v_res),
                    "elapsed_time": elapsed
                })

        # 檢查收斂
        if u_res < tolerance and v_res < tolerance:
            break

    # 計算最終結果
    elapsed_total = time.time() - start_time

    # 產生座標
    x_coords = np.linspace(0, LX, NX).tolist()
    y_coords = np.linspace(0, LY, NY).tolist()

    # 返回結果
    return {
        "pressure": p.tolist(),
        "velocity_u": u.tolist(),
        "velocity_v": v.tolist(),
        "x_coords": x_coords,
        "y_coords": y_coords,
        "convergence_history": convergence_history,
        "final_residuals": {
            "u": float(u_res),
            "v": float(v_res)
        },
        "total_iterations": it + 1,
        "elapsed_time": elapsed_total,
        "converged": u_res < tolerance and v_res < tolerance
    }
