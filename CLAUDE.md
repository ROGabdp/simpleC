# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

這是一個使用 SIMPLEC (Semi-Implicit Method for Pressure-Linked Equations - Consistent) 演算法的計算流體力學 (CFD) 求解器,用於求解二維蓋驅動方腔流 (lid-driven cavity flow) 問題。

## 主要指令

### 執行求解器
```bash
python simplec.py
```

這將執行 SIMPLEC 演算法並產生:
- 壓力等高線圖
- 速度向量圖
- 中心線速度分佈圖

### SpecKit 工作流程

本專案整合了 SpecKit 特性開發框架,用於結構化的功能規劃和實施:

```bash
# 1. 建立功能規格 (從自然語言描述)
/speckit.specify <功能描述>

# 2. 釐清規格中的不明確之處 (可選)
/speckit.clarify

# 3. 產生實施計畫 (技術設計)
/speckit.plan

# 4. 產生任務清單 (可執行的任務分解)
/speckit.tasks

# 5. 執行實施
/speckit.implement

# 6. 分析一致性和品質 (可選)
/speckit.analyze

# 7. 產生檢查清單 (可選)
/speckit.checklist
```

**工作流程說明**:
- 功能規格自動存放在 `specs/N-feature-name/` 目錄
- 每個功能在獨立的 Git 分支上開發 (格式: `N-feature-name`)
- 自動進行品質驗證和憲法檢查
- 支援多個 Reynolds number 測試案例的批次開發

## 程式架構

### 數值方法
- **演算法**: SIMPLEC (相較於 SIMPLE 演算法,壓力修正時使用 alpha_p = 1.0)
- **網格**: 交錯網格 (Staggered Grid)
  - 壓力 `p` 位於網格中心 (i, j)
  - u 速度位於垂直面中心 (i-1/2, j)
  - v 速度位於水平面中心 (i, j-1/2)
- **對流項離散**: 一階迎風格式 (Upwind Scheme)
- **壓力修正**: 高斯-賽德爾迭代法

### 關鍵參數
- `alpha_u = 0.7`: 速度的鬆弛因子 (under-relaxation)
- `alpha_p = 1.0`: 壓力的鬆弛因子 (SIMPLEC 特徵)
- `max_iter = 10000`: 最大迭代次數
- `tolerance = 1e-5`: 收斂標準
- Reynolds number = 100 (rho=1.0, U_lid=1.0, LX=1.0, mu=0.01)

### 求解流程
1. **速度預測** (步驟 A): 求解 u 和 v 動量方程式得到 u_star, v_star
2. **壓力修正** (步驟 B): 求解壓力修正方程式得到 p_prime
3. **速度與壓力修正** (步驟 C): 用 p_prime 修正速度場和壓力場
4. **邊界條件** (步驟 D): 施加邊界條件 (頂蓋速度 U_lid, 其餘壁面無滑移)
5. **收斂檢查** (步驟 E): 檢查 u 和 v 的 L2 範數殘差

### 已知簡化
程式碼中有幾處標記為「簡化」的地方,這些是可能的改進點:
- 第 129-133 行: a_P 係數在壓力修正方程式中被簡化,實際應該為每個速度位置重新計算
- 第 163 行和第 169 行: d_u 和 d_v 係數也使用了簡化的 a_P

## 修改建議

### 提升數值精度
- 重新計算每個速度位置的 a_P 係數,而非使用簡化值
- 考慮使用高階對流格式 (如 QUICK scheme)

### 增強功能
- 將參數設定改為外部配置檔 (如 JSON 或 YAML)
- 增加結果輸出功能 (如儲存流場資料為 VTK 格式)
- 支援不同 Reynolds number 的批次計算
