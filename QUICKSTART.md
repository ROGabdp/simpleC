# CFD 求解器 Web 介面 - 快速開始指南

## 前置需求

- Python 3.10 或更高版本
- Node.js 16 或更高版本
- npm 或 yarn

## 後端設定與執行

### 1. 安裝 Python 依賴

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
# source venv/bin/activate

pip install -r requirements.txt
```

### 2. 啟動後端服務

```bash
# 確保在 backend 目錄並已啟動虛擬環境
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

後端服務會在 `http://localhost:8000` 啟動

- API 文檔 (Swagger): http://localhost:8000/docs
- API 文檔 (ReDoc): http://localhost:8000/redoc

## 前端設定與執行

### 1. 安裝 Node.js 依賴

```bash
cd frontend
npm install
```

### 2. 啟動前端開發伺服器

```bash
npm start
```

前端應用程式會在 `http://localhost:3000` 自動開啟瀏覽器

## 使用流程

### 步驟 1: 輸入參數

在前端介面輸入模擬參數:

- **Reynolds 數**: 100 (建議範圍: 10 - 1000)
- **X 方向網格數**: 41 (建議: 21 - 81)
- **Y 方向網格數**: 41 (建議: 21 - 81)

點擊「開始模擬」按鈕。

### 步驟 2: 監控進度

系統會即時顯示:

- 當前迭代次數
- U 和 V 速度的殘差值
- 已執行時間

### 步驟 3: 查看結果

模擬完成後會自動顯示三種視覺化圖表:

1. **壓力等高線圖**: 顯示腔體內的壓力分佈
2. **速度向量圖**: 顯示流場的速度場
3. **中心線速度分佈**: 顯示 U 和 V 速度沿中心線的變化

## 測試案例

### 標準測試 (Re=100, 41x41)

**預期結果**:

- 求解時間: < 30 秒
- 收斂狀態: 已收斂
- 最終殘差: < 1e-5

### 小網格快速測試 (Re=100, 21x21)

**預期結果**:

- 求解時間: < 10 秒
- 適合快速驗證系統功能

## 執行測試

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

## 常見問題

### 1. 後端啟動失敗

**問題**: `ModuleNotFoundError: No module named 'fastapi'`

**解決方案**: 確保已啟動虛擬環境並安裝依賴

```bash
cd backend
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. 前端無法連線到後端

**問題**: CORS 錯誤或連線被拒絕

**解決方案**:

1. 確認後端服務已啟動在 `http://localhost:8000`
2. 檢查 `backend/app/core/config.py` 中的 CORS 設定
3. 確保防火牆沒有阻擋 8000 埠

### 3. WebSocket 連線失敗

**問題**: 進度無法即時更新

**解決方案**:

1. 檢查瀏覽器控制台是否有 WebSocket 錯誤
2. 確認後端 WebSocket 端點正常運作
3. 嘗試重新整理頁面

### 4. 求解器計算時間過長

**問題**: 網格過大導致計算緩慢

**解決方案**:

1. 減少網格數量 (建議 ≤ 81x81)
2. 降低最大迭代次數
3. 放寬收斂標準 (例如從 1e-5 改為 1e-4)

## 停止服務

### 停止後端

在後端終端機按 `Ctrl+C`

### 停止前端

在前端終端機按 `Ctrl+C`

## 下一步

- 查閱完整文檔: [README.md](README.md)
- 了解技術設計: [specs/001-web-cfd-interface/plan.md](specs/001-web-cfd-interface/plan.md)
- 查看任務清單: [specs/001-web-cfd-interface/tasks.md](specs/001-web-cfd-interface/tasks.md)
