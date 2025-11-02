# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

這是一個使用 SIMPLEC (Semi-Implicit Method for Pressure-Linked Equations - Consistent) 演算法的 CFD 求解器,具備 Web 介面用於求解二維蓋驅動方腔流 (lid-driven cavity flow) 問題。專案包含:
- 原始的獨立 Python 求解器 (`simplec.py`)
- FastAPI 後端 (提供 REST API 和 WebSocket)
- React 前端 (參數輸入、即時進度監控、結果視覺化)

## 主要指令

### 開發環境設定

**後端**:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

**前端**:
```bash
cd frontend
npm install
```

### 執行應用程式

**啟動後端**:
```bash
cd backend
venv\Scripts\activate  # Windows
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- API 文檔: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**啟動前端**:
```bash
cd frontend
npm start
```
- 開啟 http://localhost:3000

**執行原始求解器**:
```bash
python simplec.py
```

### 測試

**後端測試**:
```bash
cd backend
pytest tests/ -v                    # 執行所有測試
pytest tests/unit/ -v              # 單元測試
pytest tests/integration/ -v       # 整合測試
```

**前端測試**:
```bash
cd frontend
npm test
```

### 程式碼品質工具

**後端**:
```bash
cd backend
black app/ tests/                   # 格式化
flake8 app/ tests/                  # Linting
mypy app/                           # 型別檢查
```

### SpecKit 工作流程

本專案整合了 SpecKit 特性開發框架:

```bash
/speckit.specify <功能描述>    # 1. 建立功能規格
/speckit.clarify               # 2. 釐清不明確之處 (可選)
/speckit.plan                  # 3. 產生實施計畫
/speckit.tasks                 # 4. 產生任務清單
/speckit.implement             # 5. 執行實施
/speckit.analyze               # 6. 分析一致性和品質 (可選)
/speckit.checklist             # 7. 產生檢查清單 (可選)
```

**工作流程說明**:
- 功能規格存放在 `specs/N-feature-name/` 目錄
- 每個功能在獨立的 Git 分支上開發 (格式: `N-feature-name`)
- 自動進行品質驗證和憲法檢查

## 程式架構

### 後端架構 (FastAPI)

```
backend/
├── app/
│   ├── api/           # REST 和 WebSocket 端點
│   │   ├── simulation.py     # 模擬任務 CRUD
│   │   └── websocket.py      # 即時進度推送
│   ├── models/        # Pydantic 資料模型
│   │   ├── simulation.py     # SimulationParameters, SimulationJob
│   │   └── results.py        # FlowFieldResults
│   ├── services/      # 業務邏輯
│   │   └── solver_service.py # 任務管理和求解器執行
│   └── core/          # 核心功能
│       ├── config.py          # 應用程式配置
│       └── solver/
│           └── simplec_wrapper.py  # SIMPLEC 求解器封裝
└── tests/
    ├── unit/          # 單元測試 (求解器邏輯)
    └── integration/   # 整合測試 (API 端點)
```

**關鍵設計**:
- **任務管理**: `solver_service` 管理模擬任務的生命週期 (PENDING → RUNNING → COMPLETED/FAILED)
- **非同步執行**: 使用 FastAPI BackgroundTasks 在背景執行長時間運算
- **即時通訊**: WebSocket 推送迭代進度 (每 10 次迭代更新一次)
- **配置**: `app/core/config.py` 使用 Pydantic Settings 管理環境變數和限制 (最大/最小網格尺寸)

### 前端架構 (React)

```
frontend/src/
├── components/
│   ├── ParameterForm/            # 參數輸入表單
│   ├── ProgressMonitor/          # 進度監控 (WebSocket)
│   └── ResultsVisualization/     # 結果視覺化
│       ├── PressureContour.js    # 壓力等高線圖 (Plotly)
│       ├── VelocityVector.js     # 速度向量圖 (Plotly)
│       └── CenterlineProfile.js  # 中心線速度分佈圖
├── services/
│   ├── api.js         # Axios REST API 客戶端
│   └── websocket.js   # WebSocket 客戶端
└── context/
    └── SimulationContext.js  # 全域狀態管理
```

**關鍵設計**:
- **狀態管理**: React Context API 管理模擬狀態和結果
- **視覺化**: 使用 Plotly.js 繪製互動式圖表
- **即時更新**: WebSocket 訂閱求解器進度,更新 ProgressMonitor 組件

### SIMPLEC 數值方法

**演算法特徵**:
- **網格**: 交錯網格 (Staggered Grid)
  - 壓力 `p` 在格點中心 (i, j)
  - u 速度在垂直面中心 (i-1/2, j)
  - v 速度在水平面中心 (i, j-1/2)
- **對流項**: 一階迎風格式 (Upwind Scheme)
- **壓力修正**: 高斯-賽德爾迭代法 (50 次內迭代)
- **SIMPLEC vs SIMPLE**: 壓力鬆弛因子 `alpha_p = 1.0` (SIMPLE 通常 < 1)

**求解流程** (5 步驟):
1. **速度預測** (步驟 A): 求解動量方程式 → u_star, v_star
2. **壓力修正** (步驟 B): 求解壓力修正方程式 → p_prime
3. **修正** (步驟 C): 用 p_prime 修正速度和壓力場
4. **邊界條件** (步驟 D): 頂蓋 u=U_lid, 其餘壁面 u=v=0
5. **收斂檢查** (步驟 E): 計算 u 和 v 的 L2 範數殘差

**預設參數**:
- `alpha_u = 0.7` (速度鬆弛因子)
- `alpha_p = 1.0` (壓力鬆弛因子, SIMPLEC 特徵)
- `max_iter = 10000`
- `tolerance = 1e-5`
- Reynolds number = 100

### API 設計

**REST 端點**:
- `POST /api/simulations` - 建立新模擬任務
- `GET /api/simulations/{job_id}` - 查詢任務狀態
- `GET /api/simulations/{job_id}/results` - 取得結果 (需 status=COMPLETED)
- `DELETE /api/simulations/{job_id}` - 刪除任務 (MVP: 不支援取消執行中任務)

**WebSocket**:
- `ws://localhost:8000/ws/{job_id}` - 訂閱進度更新
- 訊息格式: `{iteration, residual_u, residual_v, elapsed_time}`

**資料模型關鍵欄位**:
- `SimulationParameters`: `reynolds_number`, `nx`, `ny`, `alpha_u`, `alpha_p`, `max_iter`, `tolerance`, `lid_velocity`
- `FlowFieldResults`: `pressure` (2D 陣列), `velocity_u`, `velocity_v`, `x_coords`, `y_coords`, `convergence_history`, `final_residuals`

## 已知簡化與改進空間

### 數值方法簡化
- `simplec_wrapper.py` 第 136-139 行: `a_P` 係數在壓力修正方程式中使用簡化值,理想上應為每個速度位置重新計算
- 第 170, 176 行: 速度修正時的 `d_u` 和 `d_v` 也使用簡化的 `a_P`

### MVP 限制
- 不支援取消執行中的任務 (見 `app/api/simulation.py:81`)
- 前端無結果匯出功能 (User Story 3 尚未實作)
- 無進階參數控制 UI (User Story 2 尚未實作)

### 未來增強
- 使用高階對流格式 (如 QUICK scheme) 提升精度
- 支援不同 Reynolds number 的批次計算
- 增加結果匯出 (VTK 格式)
