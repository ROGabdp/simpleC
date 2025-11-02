<!--
Sync Impact Report:
- Version change: [INITIAL] → 1.0.0
- This is the initial constitution creation for the simpleC CFD project
- Added principles:
  1. MVP 優先原則
  2. 可測試性原則
  3. 簡約設計原則
  4. 正體中文規範
  5. 技術棧標準
- Templates status:
  ✅ plan-template.md - reviewed, aligned with constitution principles
  ✅ spec-template.md - reviewed, aligned with constitution principles
  ✅ tasks-template.md - reviewed, aligned with constitution principles
- Follow-up: None
- Created: 2025-11-02
-->

# simpleC CFD 專案憲法

## 核心原則

### I. MVP 優先原則 (最小可行產品)

**必須遵守**:
- 每個功能必須先實作最小可行版本,驗證價值後再擴展
- 優先實作 P1 (最高優先級) 使用者故事,確保獨立可交付
- 避免預先建構未經驗證需求的功能
- 每個開發迭代都必須產生可演示的工作成果

**理由**: CFD 模擬是科學計算領域,需求驗證成本高。MVP 方法確保我們先驗證核心假設(如 Web 介面是否真正改善工作流程),再投入資源開發進階功能。

### II. 可測試性原則 (NON-NEGOTIABLE)

**必須遵守**:
- 所有求解器邏輯必須有單元測試,驗證數值精確性
- 所有 API 端點必須有整合測試,驗證輸入輸出契約
- 視覺化組件必須有快照測試或視覺回歸測試
- 測試必須涵蓋邊界條件和錯誤情況
- 測試必須能獨立執行,不依賴外部服務或手動設定

**理由**: CFD 求解器的正確性至關重要。數值錯誤可能導致完全錯誤的流場預測。自動化測試是確保程式碼變更不破壞既有功能的唯一可靠方法。

### III. 簡約設計原則 (避免過度設計)

**必須遵守**:
- 不要為未來可能的需求預先建構抽象層
- 優先使用標準函式庫和成熟套件,避免重新發明輪子
- 程式碼結構遵循 YAGNI (You Aren't Gonna Need It) 原則
- 每個抽象必須有明確的當前用途,不能僅為「未來擴展性」
- 重構只在有具體需求驅動時進行

**理由**: 過度設計增加維護成本,且預測的「未來需求」往往不會發生。簡約設計讓程式碼更容易理解、測試和修改。

### IV. 正體中文規範

**必須遵守**:
- 所有使用者介面文字必須使用正體中文
- 所有文檔 (README, 註解, 規格) 必須使用正體中文
- 變數名稱、函式名稱使用英文 (遵循 Python/JavaScript 慣例)
- 提交訊息 (commit messages) 使用正體中文
- 錯誤訊息和日誌必須使用正體中文,方便除錯

**理由**: 專案主要使用者為中文使用者,正體中文介面和文檔降低學習門檻,提高可用性。程式碼使用英文命名維持與國際開發慣例一致。

### V. 技術棧標準

**必須遵守**:
- **後端**: 使用 FastAPI 框架
  - 所有 API 必須有自動生成的 OpenAPI 文檔
  - 使用 Pydantic 進行資料驗證
  - 使用 async/await 處理 I/O 密集操作
- **前端**: 使用 React + Plotly.js
  - React 組件必須是函式組件 (Hooks),不使用 Class 組件
  - 使用 Plotly.js 進行所有科學視覺化
  - 狀態管理優先使用 React Context,複雜場景才引入 Redux
- **求解器**: 重用現有 simplec.py 程式碼
  - 將 simplec.py 重構為可匯入的模組,保持演算法邏輯不變
  - 不重新實作 CFD 演算法
- **通訊**: 使用 WebSocket 進行即時進度更新

**理由**: 統一技術棧降低學習成本和維護複雜度。選擇的技術都是成熟且有良好社群支援的工具,適合科學計算 Web 應用。

## 品質標準

### 程式碼品質

- **型別標註**: Python 程式碼必須使用 type hints,前端使用 TypeScript 或 PropTypes
- **Linting**: 必須通過 pylint/flake8 (Python) 和 ESLint (JavaScript) 檢查
- **格式化**: 使用 Black (Python) 和 Prettier (JavaScript) 自動格式化
- **覆蓋率**: 單元測試覆蓋率目標 ≥ 80%

### 文檔要求

- 每個模組必須有頂層 docstring 說明用途
- 複雜函式必須有參數和返回值說明
- API 端點必須有 FastAPI 自動生成的文檔
- README 必須包含安裝、執行和測試指令

### 效能標準

- 標準測試案例 (Re=100, 41x41) 求解時間 < 30 秒
- API 回應時間 < 200ms (不含求解時間)
- 前端初始載入時間 < 3 秒
- WebSocket 進度更新延遲 < 2 秒

## 開發流程

### 功能開發流程

1. **規格階段**: 使用 `/speckit.specify` 建立功能規格,通過品質檢查
2. **計畫階段**: 使用 `/speckit.plan` 產生技術設計
3. **任務階段**: 使用 `/speckit.tasks` 產生任務清單
4. **實施階段**:
   - 優先實作 P1 使用者故事
   - 每個任務完成後執行測試
   - 確保每個提交都通過 CI 檢查
5. **審查階段**: 程式碼審查關注可測試性、簡約性、正體中文規範

### 分支策略

- `main`: 穩定版本,僅接受經過完整測試的合併
- `###-feature-name`: 功能分支,格式為編號-功能短名稱
- 功能完成後透過 Pull Request 合併回 main

### 測試要求

- 單元測試: 每個函式/類別的獨立測試
- 整合測試: API 端點和 WebSocket 通訊測試
- 端到端測試: 完整使用者流程測試 (可選,非 MVP 必需)

## Governance

### 憲法優先級

本憲法的原則優先於所有其他開發慣例。當有衝突時,必須:
1. 記錄衝突原因
2. 提出憲法修正建議或例外批准
3. 更新相關文檔

### 修正程序

憲法修正必須:
- 記錄修正原因和影響範圍
- 更新版本號 (遵循語意化版本)
- 更新所有相依模板和文檔
- 提交 Pull Request 供審查

### 合規性審查

- 所有 Pull Request 必須驗證是否符合憲法原則
- 程式碼審查者有責任指出違反憲法的設計
- 複雜度和抽象必須有明確的當前需求支持

### 例外處理

若有正當理由需要違反憲法原則:
- 必須在 Pull Request 中明確說明
- 必須記錄例外的範圍和期限
- 必須有計畫在未來版本中移除例外

**Version**: 1.0.0 | **Ratified**: 2025-11-02 | **Last Amended**: 2025-11-02
