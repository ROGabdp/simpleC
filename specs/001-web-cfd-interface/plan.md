# Implementation Plan: CFD 求解器 Web 介面

**Branch**: `001-web-cfd-interface` | **Date**: 2025-11-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-web-cfd-interface/spec.md`

## Summary

建立一個 Web 應用程式,提供使用者友善的介面來執行 SIMPLEC CFD 求解器。使用者可以透過瀏覽器輸入流場參數 (Reynolds number, 網格尺寸, 鬆弛因子等),即時監控求解進度,並在完成後查看互動式視覺化結果。

**技術方案**:
- **後端**: FastAPI 提供 REST API 和 WebSocket 服務,整合現有的 simplec.py 求解器
- **前端**: React 單頁應用程式,使用 Plotly.js 進行科學視覺化
- **通訊**: WebSocket 用於即時進度推送
- **整合**: 將 simplec.py 重構為可匯入模組,保持演算法邏輯不變

## Technical Context

**Language/Version**: Python 3.10+, JavaScript (ES6+)
**Primary Dependencies**:
- 後端: FastAPI, uvicorn, pydantic, numpy, matplotlib
- 前端: React 18+, Plotly.js, axios
**Storage**: 記憶體暫存 (MVP 階段),未來可選擇性加入檔案儲存
**Testing**: pytest (後端), Jest + React Testing Library (前端)
**Target Platform**: Web 應用程式 (桌面瀏覽器: Chrome, Firefox, Edge)
**Project Type**: Web application (前後端分離)
**Performance Goals**:
- 標準案例 (Re=100, 41x41) 求解時間 < 30 秒
- API 回應時間 < 200ms
- WebSocket 訊息延遲 < 2 秒
**Constraints**:
- 必須重用現有 simplec.py,不重新實作 CFD 演算法
- 單使用者模式 (MVP),一次只執行一個求解任務
- 資料量 < 10 MB (適合 WebSocket 傳輸)
**Scale/Scope**:
- 單一使用者
- 3 個主要頁面 (參數輸入、進度監控、結果視覺化)
- 約 1500-2000 行後端程式碼, 1000-1500 行前端程式碼

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. MVP 優先原則
✅ **PASS** - 計畫專注於 P1 使用者故事 (基本流場模擬執行),P2 和 P3 功能標記為後續迭代

### II. 可測試性原則
✅ **PASS** - 計畫包含完整測試策略:
- 後端: pytest 單元測試 (求解器邏輯) + API 整合測試
- 前端: Jest 單元測試 + React Testing Library 組件測試
- 目標覆蓋率 ≥ 80%

### III. 簡約設計原則
✅ **PASS** - 避免過度設計:
- 無抽象化的資料存取層 (直接記憶體操作)
- 無任務佇列系統 (單一任務執行)
- 無複雜狀態管理 (使用 React Context,避免 Redux)
- 重用現有 simplec.py,不重新實作演算法

### IV. 正體中文規範
✅ **PASS** - 所有使用者介面文字、錯誤訊息、文檔使用正體中文

### V. 技術棧標準
✅ **PASS** - 完全符合憲法規定:
- 後端: FastAPI + Pydantic + async/await
- 前端: React (函式組件 + Hooks) + Plotly.js
- 通訊: WebSocket
- 求解器: 重用 simplec.py

**總結**: ✅ 所有憲法原則均通過,無需例外批准

## Project Structure

### Documentation (this feature)

```text
specs/001-web-cfd-interface/
├── plan.md              # 本文件
├── research.md          # Phase 0 輸出
├── data-model.md        # Phase 1 輸出
├── quickstart.md        # Phase 1 輸出
├── contracts/           # Phase 1 輸出
│   ├── simulation.openapi.yaml
│   └── websocket.md
├── checklists/          # 已存在
│   └── requirements.md
└── tasks.md             # Phase 2 輸出 (/speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 應用程式入口
│   ├── models/
│   │   ├── __init__.py
│   │   ├── simulation.py       # Pydantic 資料模型
│   │   └── results.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── solver_service.py   # 求解器服務 (整合 simplec.py)
│   │   └── visualization_service.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── simulation.py       # REST API 端點
│   │   └── websocket.py        # WebSocket 端點
│   └── core/
│       ├── __init__.py
│       ├── config.py           # 配置管理
│       └── solver/
│           ├── __init__.py
│           └── simplec_wrapper.py  # simplec.py 包裝器
├── tests/
│   ├── unit/
│   │   ├── test_solver.py
│   │   └── test_models.py
│   └── integration/
│       ├── test_api.py
│       └── test_websocket.py
├── requirements.txt
└── README.md

frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── index.js                # React 應用程式入口
│   ├── App.js
│   ├── components/
│   │   ├── ParameterForm/
│   │   │   ├── ParameterForm.js
│   │   │   └── ParameterForm.test.js
│   │   ├── ProgressMonitor/
│   │   │   ├── ProgressMonitor.js
│   │   │   └── ProgressMonitor.test.js
│   │   └── ResultsVisualization/
│   │       ├── PressureContour.js
│   │       ├── VelocityVector.js
│   │       ├── CenterlineProfile.js
│   │       └── ResultsVisualization.test.js
│   ├── services/
│   │   ├── api.js              # API 客戶端 (axios)
│   │   └── websocket.js        # WebSocket 客戶端
│   ├── context/
│   │   └── SimulationContext.js
│   └── utils/
│       ├── validation.js
│       └── formatters.js
├── tests/
│   └── integration/
│       └── App.test.js
├── package.json
└── README.md

simplec.py                      # 現有求解器 (保持不變或輕微重構)
```

**Structure Decision**: 選擇 Web application 結構 (Option 2),因為這是前後端分離的 Web 應用程式。後端和前端各自獨立,便於開發和部署。

## Complexity Tracking

> 本專案無憲法違規,此區塊為空

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

---

## Phase 0: Research & Decisions

**目標**: 解決技術細節和整合問題

### Research Topics

1. **simplec.py 重構方案**
   - 如何將現有程式碼轉換為可匯入的模組
   - 如何在不改變演算法的情況下支援進度回調
   - 如何處理 matplotlib 繪圖 (轉換為資料格式而非顯示視窗)

2. **FastAPI + WebSocket 最佳實務**
   - 如何在 FastAPI 中管理長時間運行的背景任務
   - WebSocket 廣播進度更新的模式
   - 錯誤處理和連線斷開重連機制

3. **Plotly.js 科學視覺化**
   - 如何繪製壓力等高線圖 (contour plot)
   - 如何繪製速度向量圖 (quiver plot / cone plot)
   - 如何處理大型陣列資料的效能

4. **資料序列化**
   - Numpy 陣列 → JSON 轉換的最佳方案
   - 壓縮策略 (如果資料量接近 10 MB 上限)

**輸出**: `research.md` 文件包含所有研究結果和決策

---

## Phase 1: Design Artifacts

### Data Model

**實體定義** (參考 spec.md 的 Key Entities):

1. **SimulationParameters** (輸入參數)
   - reynolds_number: float
   - nx, ny: int (網格尺寸)
   - alpha_u, alpha_p: float (鬆弛因子)
   - max_iter: int
   - tolerance: float
   - lid_velocity: float (預設 1.0)
   - density, viscosity: float (自動從 Re 計算)

2. **SimulationJob** (模擬任務)
   - job_id: str (UUID)
   - parameters: SimulationParameters
   - status: enum (PENDING, RUNNING, COMPLETED, FAILED)
   - created_at: datetime
   - started_at: datetime (可選)
   - completed_at: datetime (可選)
   - error_message: str (可選)

3. **SolverProgress** (求解進度)
   - job_id: str
   - iteration: int
   - residual_u: float
   - residual_v: float
   - elapsed_time: float
   - estimated_remaining: float (可選)

4. **FlowFieldResults** (流場結果)
   - job_id: str
   - pressure: List[List[float]] (2D 陣列)
   - velocity_u: List[List[float]]
   - velocity_v: List[List[float]]
   - x_coords, y_coords: List[float]
   - convergence_history: List[dict] (迭代次數和殘差)
   - final_residuals: dict

**輸出**: `data-model.md` 詳細資料模型文件

### API Contracts

**REST Endpoints**:

```
POST   /api/simulations          # 建立新模擬任務
GET    /api/simulations/{id}     # 查詢任務狀態
DELETE /api/simulations/{id}     # 取消任務
GET    /api/simulations/{id}/results  # 取得結果資料
```

**WebSocket**:

```
WS /ws/simulation/{job_id}       # 訂閱即時進度更新
```

**輸出**: `contracts/` 目錄包含 OpenAPI 規格和 WebSocket 協定文件

### Quickstart Guide

**測試場景** (對應 User Stories):

1. **基本模擬流程** (P1)
   - 啟動後端: `uvicorn backend.app.main:app`
   - 啟動前端: `npm start`
   - 輸入參數: Re=100, 41x41
   - 驗證: 查看進度更新,結果圖表顯示

2. **進階參數測試** (P2)
   - 修改 alpha_u=0.5
   - 驗證: 收斂速度變化

3. **錯誤處理測試**
   - 輸入無效參數 (負數 Re, 過大網格)
   - 驗證: 錯誤訊息正確顯示

**輸出**: `quickstart.md` 快速開始指南

---

## Next Steps

Phase 2 將由 `/speckit.tasks` 命令執行,產生詳細任務清單。

**準備就緒的前置條件**:
- ✅ 規格已完成並通過品質檢查
- ✅ 憲法已建立
- ✅ 技術設計已完成
- ⏳ 待辦: 產生 research.md, data-model.md, contracts/, quickstart.md

**後續命令**:
1. 完成 Phase 0 和 Phase 1 (本命令)
2. 執行 `/speckit.tasks` 產生任務清單
3. 執行 `/speckit.implement` 開始實施
