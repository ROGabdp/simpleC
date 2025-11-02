# Implementation Tasks: CFD 求解器 Web 介面

**Feature**: 001-web-cfd-interface
**Created**: 2025-11-02
**Branch**: `001-web-cfd-interface`
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

---

## Implementation Strategy

**MVP First**: 優先實作 User Story 1 (P1 - 基本流場模擬執行),提供完整的端到端價值。

**Incremental Delivery**:
1. Phase 1-2: 專案設定和基礎設施
2. Phase 3 (US1): 核心 MVP - 參數輸入 → 求解 → 即時進度 → 結果視覺化
3. Phase 4 (US2): 進階參數控制 (可選)
4. Phase 5 (US3): 結果匯出功能 (可選)
5. Phase 6: 品質提升和優化

**獨立測試**: 每個 User Story 都可獨立測試和交付。

---

## Phase 1: Setup (專案初始化)

**目標**: 建立專案結構、安裝依賴、配置開發環境

### 後端設定

- [X] T001 [P] 建立後端目錄結構 backend/app/{models,services,api,core}
- [X] T002 [P] 建立後端測試目錄 backend/tests/{unit,integration}
- [X] T003 [P] 建立 backend/requirements.txt 並列出依賴 (fastapi, uvicorn, pydantic, numpy, matplotlib, pytest)
- [X] T004 [P] 建立 backend/app/__init__.py 和子模組 __init__.py 檔案
- [X] T005 [P] 建立 backend/README.md 說明後端安裝和執行步驟

### 前端設定

- [X] T006 [P] 使用 create-react-app 初始化前端專案 frontend/
- [X] T007 [P] 安裝前端依賴 (react-plotly.js, plotly.js, axios) 更新 frontend/package.json
- [X] T008 [P] 建立前端目錄結構 frontend/src/{components,services,context,utils}
- [X] T009 [P] 建立 frontend/README.md 說明前端安裝和執行步驟

### Git 和文檔

- [X] T010 [P] 建立根目錄 .gitignore (排除 node_modules/, venv/, __pycache__/, .vscode/)
- [X] T011 [P] 建立根目錄 README.md 整合說明文檔並連結 quickstart.md

---

## Phase 2: Foundational (基礎建設)

**目標**: 實作所有 User Stories 共用的核心基礎設施

### 後端基礎

- [X] T012 建立 backend/app/core/config.py 配置管理 (CORS, 環境變數)
- [X] T013 建立 backend/app/main.py FastAPI 應用程式入口,啟用 CORS
- [X] T014 [P] 建立 backend/app/models/__init__.py 並定義 JobStatus enum
- [X] T015 [P] 建立 backend/app/models/simulation.py 定義 SimulationParameters Pydantic 模型
- [X] T016 [P] 建立 backend/app/models/simulation.py 定義 SimulationJob Pydantic 模型

### simplec.py 包裝器

- [X] T017 建立 backend/app/core/solver/simplec_wrapper.py 包裝器骨架
- [X] T018 實作 simplec_wrapper.py 中的 solve_cavity_flow() 函式 (從 simplec.py 複製演算法)
- [X] T019 在 solve_cavity_flow() 加入 progress_callback 參數支援
- [X] T020 修改 simplec_wrapper.py 返回字典格式資料而非繪圖

### WebSocket Manager

- [X] T021 建立 backend/app/api/websocket.py 定義 ConnectionManager 類別
- [X] T022 實作 ConnectionManager.connect() 和 disconnect() 方法
- [X] T023 實作 ConnectionManager.send_progress() 方法
- [X] T024 在 main.py 建立 ConnectionManager 全域單例實例

---

## Phase 3: User Story 1 - 基本流場模擬執行 (P1) 🎯 MVP

**Goal**: 使用者可以輸入參數 → 啟動求解 → 查看即時進度 → 查看視覺化結果

**Independent Test**: 輸入 Re=100, 41x41 → 點擊開始 → 進度更新 → 三種圖表顯示

### 後端 - REST API

- [X] T025 [US1] 建立 backend/app/api/simulation.py 定義 POST /api/simulations 端點
- [X] T026 [US1] 實作 POST /api/simulations 建立任務邏輯 (產生 UUID, 啟動背景任務)
- [X] T027 [US1] 實作 BackgroundTasks 執行 solve_cavity_flow 並更新任務狀態
- [X] T028 [P] [US1] 建立 GET /api/simulations/{job_id} 端點返回任務狀態
- [X] T029 [P] [US1] 建立 GET /api/simulations/{job_id}/results 端點返回流場資料

### 後端 - WebSocket

- [X] T030 [US1] 建立 WebSocket 端點 /ws/simulation/{job_id} 在 websocket.py
- [X] T031 [US1] 整合 WebSocket 與 solve_cavity_flow progress_callback
- [X] T032 [US1] 實作進度訊息廣播邏輯 (每 10 次迭代)

### 後端 - 資料模型

- [X] T033 [P] [US1] 建立 backend/app/models/results.py 定義 SolverProgress 模型
- [X] T034 [P] [US1] 建立 backend/app/models/results.py 定義 FlowFieldResults 模型
- [X] T035 [US1] 建立 backend/app/services/solver_service.py 管理求解任務狀態 (記憶體字典)

### 前端 - 參數表單

- [X] T036 [P] [US1] 建立 frontend/src/components/ParameterForm/ParameterForm.js 元件骨架
- [X] T037 [US1] 實作 ParameterForm 表單欄位 (Reynolds Number, NX, NY)
- [X] T038 [US1] 實作 ParameterForm 即時驗證邏輯 (正數檢查, 範圍檢查)
- [X] T039 [US1] 實作 ParameterForm 提交處理 (呼叫 API 建立模擬)

### 前端 - API 客戶端

- [X] T040 [P] [US1] 建立 frontend/src/services/api.js 使用 axios
- [X] T041 [P] [US1] 實作 api.js 中的 createSimulation() 函式
- [X] T042 [P] [US1] 實作 api.js 中的 getSimulationStatus() 函式
- [X] T043 [P] [US1] 實作 api.js 中的 getSimulationResults() 函式

### 前端 - WebSocket 客戶端

- [X] T044 [US1] 建立 frontend/src/services/websocket.js 定義 SimulationWebSocket 類別
- [X] T045 [US1] 實作 SimulationWebSocket.connect() 連線邏輯
- [X] T046 [US1] 實作 SimulationWebSocket 訊息處理 (progress, completed, error)
- [X] T047 [US1] 實作 SimulationWebSocket 斷線重連機制

### 前端 - 狀態管理

- [X] T048 [US1] 建立 frontend/src/context/SimulationContext.js 定義 Context
- [X] T049 [US1] 實作 SimulationProvider 管理 job, progress, results 狀態
- [X] T050 [US1] 在 App.js 包裹 SimulationProvider

### 前端 - 進度監控

- [X] T051 [P] [US1] 建立 frontend/src/components/ProgressMonitor/ProgressMonitor.js 元件
- [X] T052 [US1] 實作 ProgressMonitor 顯示迭代次數和殘差值
- [X] T053 [US1] 實作 ProgressMonitor 使用 WebSocket 即時更新
- [X] T054 [US1] 加入載入動畫和狀態指示器 (RUNNING, COMPLETED, FAILED)

### 前端 - 結果視覺化

- [X] T055 [P] [US1] 建立 frontend/src/components/ResultsVisualization/PressureContour.js
- [X] T056 [US1] 實作 PressureContour 使用 Plotly.js 繪製壓力等高線圖
- [X] T057 [P] [US1] 建立 frontend/src/components/ResultsVisualization/VelocityVector.js
- [X] T058 [US1] 實作 VelocityVector 使用 Plotly.js 繪製速度向量圖 (cone plot)
- [X] T059 [P] [US1] 建立 frontend/src/components/ResultsVisualization/CenterlineProfile.js
- [X] T060 [US1] 實作 CenterlineProfile 繪製中心線速度分佈 (line plot)
- [X] T061 [US1] 整合三個視覺化元件到 ResultsVisualization 父元件

### 前端 - 主應用程式

- [X] T062 [US1] 更新 frontend/src/App.js 整合 ParameterForm, ProgressMonitor, ResultsVisualization
- [X] T063 [US1] 實作 App.js 工作流程控制 (表單 → 進度 → 結果)

### User Story 1 測試

**獨立測試標準**: 輸入 Re=100, 41x41 → 30 秒內完成 → 三種圖表正確顯示

- [X] T064 [P] [US1] 建立 backend/tests/unit/test_solver.py 測試 solve_cavity_flow 收斂性
- [X] T065 [P] [US1] 建立 backend/tests/integration/test_api.py 測試 POST /api/simulations
- [X] T066 [P] [US1] 建立 frontend/src/components/ParameterForm/ParameterForm.test.js 測試驗證邏輯
- [X] T067 [US1] 執行端到端測試: 完整流程 Re=100, 41x41 → 驗證結果

---

## Phase 4: User Story 2 - 進階參數控制 (P2) ⚙️

**Goal**: 使用者可以調整鬆弛因子、最大迭代次數、收斂標準等進階參數

**Independent Test**: 展開進階參數 → 設定 alpha_u=0.5 → 執行求解 → 觀察收斂速度變化

**Dependencies**: 需要 US1 完成 (建立在基本模擬功能之上)

### 後端擴展

- [X] T068 [P] [US2] 擴展 SimulationParameters 模型加入 alpha_u, alpha_p, max_iter, tolerance, lid_velocity 欄位
- [X] T069 [US2] 更新 solve_cavity_flow() 使用所有自訂參數

### 前端擴展

- [X] T070 [P] [US2] 在 ParameterForm.js 加入「顯示進階參數」按鈕
- [X] T071 [US2] 實作進階參數摺疊面板 (alpha_u, alpha_p, max_iter, tolerance, lid_velocity)
- [X] T072 [US2] 加入進階參數驗證 (範圍檢查)
- [X] T073 [US2] 實作預設值邏輯 (未填寫時使用預設值)

### User Story 2 測試

**獨立測試標準**: 修改 alpha_u=0.5 → 求解 → 迭代次數應增加

- [X] T074 [US2] 測試進階參數 API 接受所有自訂參數
- [X] T075 [US2] 端到端測試: alpha_u=0.5 vs 0.7 收斂速度比較

---

## Phase 5: User Story 3 - 結果匯出與儲存 (P3) 💾

**Goal**: 使用者可以匯出圖表 (PNG) 和流場資料 (JSON/CSV)

**Independent Test**: 求解完成 → 點擊「匯出圖表」→ 下載 PNG → 點擊「匯出數據」→ 下載 JSON

**Dependencies**: 需要 US1 完成

### 後端擴展

- [X] T076 [P] [US3] 建立 backend/app/services/visualization_service.py
- [X] T077 [P] [US3] 實作 generate_plot_image() 使用 matplotlib 產生 PNG 圖片
- [X] T078 [P] [US3] 建立 GET /api/simulations/{job_id}/export/plots 端點返回圖片
- [X] T079 [P] [US3] 建立 GET /api/simulations/{job_id}/export/data 端點返回 JSON/CSV

### 前端擴展

- [X] T080 [P] [US3] 在 ResultsVisualization 加入「匯出圖表」按鈕
- [X] T081 [US3] 實作 Plotly.js toImage() 匯出 PNG 功能
- [X] T082 [P] [US3] 在 ResultsVisualization 加入「匯出數據」按鈕
- [X] T083 [US3] 實作下載 JSON 檔案邏輯 (包含輸入參數和結果)

### User Story 3 測試

**獨立測試標準**: 匯出 PNG 圖片可開啟 → 匯出 JSON 包含完整資料

- [X] T084 [US3] 測試匯出的 JSON 包含輸入參數和流場資料
- [X] T085 [US3] 端到端測試: 完成求解 → 匯出圖表和數據 → 驗證檔案

---

## Phase 6: Polish & Cross-Cutting Concerns

**目標**: 提升使用者體驗、錯誤處理、效能優化

### 錯誤處理

- [X] T086 [P] 實作後端全域錯誤處理器 (FastAPI exception handlers)
- [X] T087 [P] 在前端加入錯誤訊息顯示元件 (Toast/Alert)
- [X] T088 實作求解失敗時的友善錯誤訊息 (發散、參數錯誤)

### 使用者體驗

- [X] T089 [P] 加入載入狀態和進度條動畫
- [X] T090 [P] 實作表單欄位說明文字 (Tooltip)
- [X] T091 [P] 加入輸入範圍建議 (例如: 網格 > 100 顯示警告)

### 正體中文本地化

- [X] T092 [P] 審查所有 UI 文字確保使用正體中文
- [X] T093 [P] 確保所有錯誤訊息使用正體中文
- [X] T094 [P] 更新 API 錯誤回應使用正體中文

### 效能優化

- [X] T095 [P] 測試大網格 (100x100) 效能並加入降採樣 (如需要)
- [X] T096 [P] 實作 WebSocket 訊息節流 (避免過度更新)

### 文檔和部署

- [X] T097 [P] 更新 README.md 包含完整安裝和執行指令
- [X] T098 [P] 建立 API 使用範例和 curl 命令
- [X] T099 [P] 加入故障排除章節到 README.md

---

## Dependencies

### User Story Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational)
    ↓
Phase 3 (US1) ← MVP 核心
    ↓ (必須完成)
    ├─→ Phase 4 (US2) ← 可選
    └─→ Phase 5 (US3) ← 可選
    ↓
Phase 6 (Polish)
```

**Critical Path**: Phase 1 → Phase 2 → Phase 3 (US1) = MVP

**US2 和 US3 可獨立於彼此**: 可以先做 US2 或 US3,順序不重要

---

## Parallel Execution Opportunities

### Phase 1 (Setup) - 全部可並行
- T001-T011 可同時執行 (不同目錄和檔案)

### Phase 2 (Foundational) - 部分並行
- **並行組 A**: T012-T016 (模型定義)
- **並行組 B**: T017-T020 (simplec_wrapper,需等待組 A 完成)
- **並行組 C**: T021-T024 (WebSocket Manager,可與組 B 並行)

### Phase 3 (US1) - 分層並行
- **Layer 1 (並行)**: T025-T029 (後端 API), T033-T034 (模型), T036-T039 (前端表單)
- **Layer 2 (並行)**: T040-T047 (API/WebSocket 客戶端), T051-T054 (進度監控)
- **Layer 3 (並行)**: T055-T061 (視覺化元件,可同時開發)
- **Layer 4 (順序)**: T062-T063 (整合)
- **Layer 5 (並行)**: T064-T067 (測試)

---

## Task Summary

**Total Tasks**: 99 (T001-T099)

**By Phase**:
- Phase 1 (Setup): 11 tasks
- Phase 2 (Foundational): 13 tasks
- Phase 3 (US1 - MVP): 43 tasks ⭐
- Phase 4 (US2): 8 tasks
- Phase 5 (US3): 10 tasks
- Phase 6 (Polish): 14 tasks

**MVP Scope (Suggested)**:
- Phase 1 + Phase 2 + Phase 3 = 67 tasks
- Estimated time: 2-3 days (single developer)

**Parallel Opportunities**: ~40 tasks marked with [P] can be executed concurrently

**Format Validation**: ✅ All 99 tasks follow checklist format (checkbox + ID + [P]/[Story] + description + file path)

---

## Next Steps

1. ✅ Review tasks.md for completeness
2. ⏭ Execute `/speckit.implement` to start implementation
3. ⏭ Begin with Phase 1 (Setup) tasks T001-T011
4. ⏭ Proceed to Phase 2 (Foundational) then US1 for MVP

**Ready to implement!** 🚀
