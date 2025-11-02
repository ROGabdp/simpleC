import numpy as np
import matplotlib.pyplot as plt

# --- 1. 問題設定與參數 ---
# 網格數量
NX = 41
NY = 41

# 腔體尺寸
LX = 1.0
LY = 1.0
dx = LX / (NX - 1)
dy = LY / (NY - 1)

# 流體性質
rho = 1.0  # 密度
mu = 0.01  # 動力黏滯係數 (Re = rho * U_lid * LX / mu = 1*1*1/0.01 = 100)

# 邊界條件
U_lid = 1.0  # 頂蓋速度

# 數值方法參數
alpha_u = 0.7  # 速度的鬆弛因子 (Under-relaxation factor)
alpha_p = 1.0  # 壓力的鬆弛因子 (SIMPLEC 通常設為 1.0)
max_iter = 10000  # 最大迭代次數
tolerance = 1e-5  # 收斂標準

# --- 2. 網格與變數初始化 ---
# 建立交錯網格
# 壓力 p 位於網格中心 (i, j)
# u 速度位於網格垂直面的中心 (i-1/2, j)
# v 速度位於網格水平面的中心 (i, j-1/2)

p = np.zeros((NY, NX))
p_prime = np.zeros_like(p)  # 壓力修正量

u = np.zeros((NY, NX - 1))
v = np.zeros((NY - 1, NX))

# 預測速度場
u_star = u.copy()
v_star = v.copy()

# --- 3. 主迭代迴圈 ---
print("SIMPLEC 求解器開始迭代...")
for it in range(max_iter):
    # 儲存上一步的值以計算殘差
    u_old_iter = u.copy()
    v_old_iter = v.copy()

    # --- 步驟 A: 求解動量方程式 (速度預測) ---

    # A1. 求解 u-動量方程式 (x方向)
    for j in range(1, NY - 1):
        for i in range(1, NX - 2):
            # 對流項 (使用一階迎風格式 Upwind Scheme)
            conv_u_E = 0.5 * rho * dy * (u[j, i] + u[j, i + 1])
            conv_u_W = 0.5 * rho * dy * (u[j, i - 1] + u[j, i])
            conv_v_N = 0.5 * rho * dx * (v[j, i] + v[j, i + 1])
            conv_v_S = 0.5 * rho * dx * (v[j - 1, i] + v[j - 1, i + 1])

            # 擴散項
            diff_u_E = mu * dy / dx
            diff_u_W = mu * dy / dx
            diff_u_N = mu * dx / dy
            diff_u_S = mu * dx / dy

            # 離散方程式的係數
            a_E = diff_u_E + max(0, -conv_u_E)
            a_W = diff_u_W + max(0, conv_u_W)
            a_N = diff_u_N + max(0, -conv_v_N)
            a_S = diff_u_S + max(0, conv_v_S)

            # 壓力梯度項
            source_p_u = (p[j, i] - p[j, i + 1]) * dy

            # 中心點係數 a_P
            a_P_u = a_E + a_W + a_N + a_S + \
                (conv_u_E - conv_u_W) + (conv_v_N - conv_v_S)

            # 預測速度 u_star (包含鬆弛因子)
            numerator = a_E * u[j, i+1] + a_W * u[j, i-1] + \
                a_N * u[j+1, i] + a_S * u[j-1, i] + source_p_u
            u_star[j, i] = (1 - alpha_u) * u[j, i] + \
                alpha_u * (numerator / a_P_u)

    # A2. 求解 v-動量方程式 (y方向)
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

            # 離散方程式的係數
            a_E = diff_v_E + max(0, -conv_u_E)
            a_W = diff_v_W + max(0, conv_u_W)
            a_N = diff_v_N + max(0, -conv_v_N)
            a_S = diff_v_S + max(0, conv_v_S)

            # 壓力梯度項
            source_p_v = (p[j, i] - p[j + 1, i]) * dx

            # 中心點係數 a_P
            a_P_v = a_E + a_W + a_N + a_S + \
                (conv_u_E - conv_u_W) + (conv_v_N - conv_v_S)

            # 預測速度 v_star (包含鬆弛因子)
            numerator = a_E * v[j, i+1] + a_W * v[j, i-1] + \
                a_N * v[j+1, i] + a_S * v[j-1, i] + source_p_v
            v_star[j, i] = (1 - alpha_u) * v[j, i] + \
                alpha_u * (numerator / a_P_v)

    # --- 步驟 B: 求解壓力修正方程式 ---
    p_prime[:, :] = 0  # 重置壓力修正量
    for _ in range(50):  # 使用高斯-賽德爾法迭代求解 p_prime
        for j in range(1, NY - 1):
            for i in range(1, NX - 1):
                # 取得動量方程式的中心係數 a_P (這裡需要重新計算)
                # 這是 SIMPLEC 和 SIMPLE 的主要區別
                # u-momentum a_P at (j, i) and (j, i-1)
                a_P_u_E = a_P_u  # 簡化，應重新計算在 u[j,i] 的 a_P
                a_P_u_W = a_P_u  # 簡化，應重新計算在 u[j,i-1] 的 a_P
                # v-momentum a_P at (j, i) and (j-1, i)
                a_P_v_N = a_P_v  # 簡化，應重新計算在 v[j,i] 的 a_P
                a_P_v_S = a_P_v  # 簡化，應重新計算在 v[j-1,i] 的 a_P

                # SIMPLEC 的 d 因子
                d_u_E = alpha_u * dy / a_P_u_E
                d_u_W = alpha_u * dy / a_P_u_W
                d_v_N = alpha_u * dx / a_P_v_N
                d_v_S = alpha_u * dx / a_P_v_S

                # 壓力修正方程式的係數
                a_E_p = rho * d_u_E * dy
                a_W_p = rho * d_u_W * dy
                a_N_p = rho * d_v_N * dx
                a_S_p = rho * d_v_S * dx
                a_P_p = a_E_p + a_W_p + a_N_p + a_S_p

                # 質量不平衡項 (方程式的 source term)
                mass_imbalance = rho * (u_star[j, i] - u_star[j, i-1]) * dy + \
                    rho * (v_star[j, i] - v_star[j-1, i]) * dx

                # 求解 p_prime
                p_prime[j, i] = (a_E_p * p_prime[j, i+1] + a_W_p * p_prime[j, i-1] +
                                 a_N_p * p_prime[j+1, i] + a_S_p * p_prime[j-1, i] - mass_imbalance) / a_P_p

    # --- 步驟 C: 修正壓力與速度 ---
    # 修正壓力
    p += alpha_p * p_prime

    # 修正 u 速度
    for j in range(1, NY-1):
        for i in range(1, NX-2):
            d_u = alpha_u * dy / a_P_u  # 簡化，應為 u[j,i] 的 a_P
            u[j, i] = u_star[j, i] - d_u * (p_prime[j, i+1] - p_prime[j, i])

    # 修正 v 速度
    for j in range(1, NY-2):
        for i in range(1, NX-1):
            d_v = alpha_u * dx / a_P_v  # 簡化，應為 v[j,i] 的 a_P
            v[j, i] = v_star[j, i] - d_v * (p_prime[j+1, i] - p_prime[j, i])

    # --- 步驟 D: 施加邊界條件 ---
    # u-velocity
    u[0, :] = 0.0     # 下邊界
    u[-1, :] = 0.0    # 上邊界 (交錯網格中，頂蓋速度在v的邊界處施加)
    u[:, 0] = 0.0     # 左邊界
    u[:, -1] = 0.0    # 右邊界

    # v-velocity
    v[:, 0] = 0.0     # 左邊界
    v[:, -1] = 0.0    # 右邊界
    v[0, :] = 0.0     # 下邊界
    v[-1, :] = 0.0    # 上邊界 (注意: 頂蓋速度是 u，v 在所有邊界均為0)

    # 頂蓋速度
    u[NY-1, :] = U_lid

    # --- 步驟 E: 檢查收斂 ---
    # 計算 u 速度的 L2 範數殘差
    u_res = np.sqrt(np.sum((u - u_old_iter)**2)) / \
        np.sqrt(np.sum(u_old_iter**2) + 1e-12)
    v_res = np.sqrt(np.sum((v - v_old_iter)**2)) / \
        np.sqrt(np.sum(v_old_iter**2) + 1e-12)

    if it % 100 == 0:
        print(
            f"Iteration: {it}, u-residual: {u_res:.6f}, v-residual: {v_res:.6f}")

    if u_res < tolerance and v_res < tolerance:
        print(f"\n收斂成功！迭代次數: {it}")
        break
else:
    print(f"\n已達最大迭代次數 {max_iter}，計算終止。")


# --- 4. 後處理與視覺化 ---
# 將交錯網格的速度插值到網格中心點，以便繪圖
u_center = np.zeros((NY, NX))
v_center = np.zeros((NY, NX))
u_center[:, 1:-1] = 0.5 * (u[:, :-1] + u[:, 1:])
v_center[1:-1, :] = 0.5 * (v[:-1, :] + v[1:, :])

# 繪製壓力等高線圖
x = np.linspace(0, LX, NX)
y = np.linspace(0, LY, NY)
X, Y = np.meshgrid(x, y)

plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
cp = plt.contourf(X, Y, p, levels=20, cmap='viridis')
plt.colorbar(cp)
plt.title('Pressure Contours')
plt.xlabel('X')
plt.ylabel('Y')
plt.gca().set_aspect('equal', adjustable='box')


# 繪製速度向量圖
plt.subplot(1, 2, 2)
# 每隔幾個點繪製一個向量，避免圖像過於擁擠
skip = 3
plt.quiver(X[::skip, ::skip], Y[::skip, ::skip],
           u_center[::skip, ::skip], v_center[::skip, ::skip], color='k')
plt.title('Velocity Vectors')
plt.xlabel('X')
plt.ylabel('Y')
plt.gca().set_aspect('equal', adjustable='box')

plt.tight_layout()
plt.show()

# 繪製中心線速度分佈圖 (與文獻結果對比)
u_vertical_centerline = u_center[:, NX // 2]
v_horizontal_centerline = v_center[NY // 2, :]
y_coords = np.linspace(0, LY, NY)
x_coords = np.linspace(0, LX, NX)

plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(u_vertical_centerline, y_coords, '-b', label='Computed u at x=0.5')
plt.title('U-velocity along Vertical Centerline')
plt.xlabel('u-velocity')
plt.ylabel('Y')
plt.grid(True)
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(x_coords, v_horizontal_centerline, '-r', label='Computed v at y=0.5')
plt.title('V-velocity along Horizontal Centerline')
plt.xlabel('X')
plt.ylabel('v-velocity')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()
