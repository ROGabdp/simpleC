# CFD 求解器前端

## 安裝

```bash
cd frontend
npm install
```

## 執行

```bash
npm start
```

瀏覽器會自動開啟 http://localhost:3000

## 開發

### 執行測試

```bash
npm test
```

### 建置生產版本

```bash
npm run build
```

## 功能

- 參數輸入表單 (Reynolds 數, 網格尺寸)
- 即時求解進度監控
- 結果視覺化:
  - 壓力等高線圖
  - 速度向量圖
  - 中心線速度分佈

## 注意事項

確保後端服務已啟動在 http://localhost:8000
