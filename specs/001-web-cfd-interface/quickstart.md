# Quick Start Guide

**Feature**: CFD 求解器 Web 介面
**Target**: 開發者和測試人員
**Estimated Time**: 10-15 分鐘

---

## 前置需求

### 後端
- Python 3.10+
- pip

### 前端
- Node.js 16+
- npm

---

## 安裝步驟

### 1. 後端設定

```bash
# 進入後端目錄
cd backend

# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安裝依賴
pip install fastapi uvicorn pydantic numpy matplotlib

# 啟動後端伺服器
uvicorn app.main:app --reload

# 預期輸出:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete.
```

### 2. 前端設定

```bash
# 新開終端機,進入前端目錄
cd frontend

# 安裝依賴
npm install

# 啟動開發伺服器
npm start

# 預期輸出:
# webpack compiled successfully
# Local: http://localhost:3000
```

---

## 測試場景

### 場景 1: 基本流場模擬 (P1)

**目標**: 執行標準測試案例並查看結果

**步驟**:
1. 開啟瀏覽器訪問 http://localhost:3000
2. 在參數表單中輸入:
   - Reynolds Number: `100`
   - 網格尺寸 NX: `41`
   - 網格尺寸 NY: `41`
3. 點擊「開始求解」按鈕
4. 觀察進度監控面板:
   - ✅ 迭代次數應即時更新
   - ✅ 殘差值應逐漸下降
   - ✅ 更新延遲 < 2 秒
5. 等待求解完成 (約 15-30 秒)
6. 查看結果視覺化:
   - ✅ 壓力等高線圖顯示
   - ✅ 速度向量圖顯示
   - ✅ 中心線速度分佈圖顯示
7. 驗證圖表互動功能:
   - ✅ 可縮放
   - ✅ 可平移
   - ✅ 懸停顯示數值

**預期結果**:
- 求解時間: < 30 秒
- 最終殘差: < 1e-5
- 壓力場中心附近應有負壓
- 頂蓋附近 u 速度接近 1.0

---

### 場景 2: 進階參數測試 (P2)

**目標**: 測試自訂參數功能

**步驟**:
1. 點擊「顯示進階參數」
2. 修改參數:
   - Alpha U (速度鬆弛因子): `0.5` (原本 0.7)
   - 最大迭代次數: `5000`
3. 點擊「開始求解」
4. 觀察收斂速度差異

**預期結果**:
- 較小的鬆弛因子 → 收斂更慢但更穩定
- 可能需要更多迭代次數

---

### 場景 3: 參數驗證測試

**目標**: 驗證錯誤處理

**測試案例 A - 負數 Reynolds Number**:
1. Reynolds Number: `-100`
2. 點擊「開始求解」

**預期**: 顯示錯誤訊息「Reynolds number 必須為正數」

**測試案例 B - 過大網格**:
1. 網格尺寸 NX: `250` (超過上限 200)
2. 點擊「開始求解」

**預期**: 顯示錯誤訊息「網格尺寸必須在 10-200 之間」

**測試案例 C - 非數值輸入**:
1. Reynolds Number: `abc`
2. 離開輸入框

**預期**: 即時顯示驗證錯誤

---

## API 測試 (使用 curl)

### 建立模擬任務

```bash
curl -X POST http://localhost:8000/api/simulations \
  -H "Content-Type: application/json" \
  -d '{
    "reynolds_number": 100,
    "nx": 41,
    "ny": 41
  }'

# 預期回應:
# {"job_id":"123e4567-e89b-12d3-a456-426614174000","status":"PENDING"}
```

### 查詢任務狀態

```bash
curl http://localhost:8000/api/simulations/123e4567-e89b-12d3-a456-426614174000

# 預期回應:
# {
#   "job_id": "...",
#   "status": "RUNNING",
#   "created_at": "2025-11-02T10:30:00",
#   ...
# }
```

### 取得結果

```bash
# 等待任務完成後
curl http://localhost:8000/api/simulations/123e4567-e89b-12d3-a456-426614174000/results

# 預期回應: 完整流場資料 (JSON)
```

---

## WebSocket 測試

### 使用瀏覽器 DevTools

1. 開啟瀏覽器開發者工具 (F12)
2. 切換到 Network 標籤
3. 篩選 WS (WebSocket)
4. 啟動模擬
5. 點擊 WebSocket 連線
6. 查看 Messages 標籤

**預期訊息序列**:
```json
// 1. 進度更新
{"type":"progress","data":{"iteration":10,"residual_u":0.1,...}}
{"type":"progress","data":{"iteration":20,"residual_u":0.05,...}}
...
// 2. 完成訊息
{"type":"completed","data":{"status":"COMPLETED",...}}
```

---

## 常見問題

### Q: 後端啟動失敗 "Port 8000 already in use"
**A**: 終止佔用端口的程序或修改 `uvicorn` 端口:
```bash
uvicorn app.main:app --port 8080
```

### Q: 前端無法連線到後端
**A**: 檢查 CORS 設定,確保 FastAPI 允許 localhost:3000:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Q: 求解時間過長 (> 1 分鐘)
**A**:
- 確認網格尺寸不要過大 (建議 ≤ 50x50 for testing)
- 檢查 CPU 使用率
- 減少最大迭代次數進行快速測試

### Q: WebSocket 斷線
**A**:
- 檢查網路穩定性
- 查看瀏覽器 Console 錯誤訊息
- 確認後端 WebSocket 端點正確

---

## 下一步

完成 Quick Start 後:
1. 執行 `/speckit.tasks` 產生完整任務清單
2. 執行 `/speckit.implement` 開始實施開發
3. 參考 `data-model.md` 和 `contracts/` 了解詳細設計

---

## 支援

遇到問題請查閱:
- API 文檔: http://localhost:8000/docs (FastAPI 自動生成)
- 專案憲法: `.specify/memory/constitution.md`
- 功能規格: `spec.md`
