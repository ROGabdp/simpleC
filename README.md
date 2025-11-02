# CFD 求解器 Web 介面

這是一個使用 SIMPLEC 演算法的計算流體力學 (CFD) 求解器 Web 應用程式,用於求解二維蓋驅動方腔流 (lid-driven cavity flow) 問題。

## 專案結構

```
simpleC/
├── backend/           # FastAPI 後端
│   ├── app/
│   │   ├── models/    # Pydantic 資料模型
│   │   ├── services/  # 業務邏輯
│   │   ├── api/       # REST 和 WebSocket 端點
│   │   └── core/      # 核心功能 (求解器)
│   └── tests/         # 後端測試
├── frontend/          # React 前端
│   └── src/
│       ├── components/  # React 組件
│       ├── services/    # API 客戶端
│       ├── context/     # 狀態管理
│       └── utils/       # 工具函式
└── simplec.py         # 原始 CFD 求解器
```

## 快速開始

### 後端設定

1. 建立虛擬環境並安裝依賴:

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

2. 啟動後端服務:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. 訪問 API 文檔: http://localhost:8000/docs

### 前端設定

1. 安裝依賴:

```bash
cd frontend
npm install
```

2. 啟動開發伺服器:

```bash
npm start
```

3. 瀏覽器開啟: http://localhost:3000

## 功能特性

### 使用者故事 1: 基本流場模擬執行 (MVP)

- ✅ 輸入參數 (Reynolds 數, 網格尺寸)
- ✅ 啟動 CFD 求解
- ✅ 即時進度監控 (迭代次數, 殘差值)
- ✅ 視覺化結果:
  - 壓力等高線圖
  - 速度向量圖
  - 中心線速度分佈

### 使用者故事 2: 進階參數控制 (未來)

- ⏳ 調整鬆弛因子 (alpha_u, alpha_p)
- ⏳ 設定最大迭代次數和收斂標準

### 使用者故事 3: 結果匯出 (未來)

- ⏳ 匯出圖表 (PNG)
- ⏳ 匯出流場資料 (JSON/CSV)

## 測試

### 後端測試

```bash
cd backend
pytest tests/ -v
```

### 前端測試

```bash
cd frontend
npm test
```

## 技術棧

- **後端**: FastAPI, Pydantic, NumPy, Matplotlib
- **前端**: React, Plotly.js, Axios
- **通訊**: WebSocket (即時進度更新)
- **求解器**: SIMPLEC 演算法

## 效能基準

- 標準案例 (Re=100, 41x41 網格): < 30 秒
- API 回應時間: < 200ms
- WebSocket 更新延遲: < 2 秒

## 文檔

- [專案憲法](.specify/memory/constitution.md)
- [功能規格](specs/001-web-cfd-interface/spec.md)
- [技術設計](specs/001-web-cfd-interface/plan.md)
- [資料模型](specs/001-web-cfd-interface/data-model.md)
- [任務清單](specs/001-web-cfd-interface/tasks.md)

## 授權

本專案遵循 MIT 授權條款
