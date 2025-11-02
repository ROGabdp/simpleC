# Research & Technical Decisions

**Feature**: CFD 求解器 Web 介面
**Date**: 2025-11-02
**Purpose**: 解決技術整合問題和選擇最佳實作方案

---

## 1. simplec.py 重構方案

### 研究問題
- 如何將現有腳本轉換為可匯入的模組?
- 如何在不改變演算法的情況下支援進度回調?
- 如何處理 matplotlib 繪圖 (轉換為資料而非顯示視窗)?

### 決策: 使用包裝器模式 (Wrapper Pattern)

**方案**:
1. **保持 simplec.py 原樣**,不修改核心演算法程式碼
2. **建立 simplec_wrapper.py**,提供函式化介面:
   ```python
   def solve_cavity_flow(parameters, progress_callback=None):
       # 從 parameters 提取變數
       # 執行 SIMPLEC 演算法 (複製自 simplec.py)
       # 在每 N 次迭代後呼叫 progress_callback
       # 返回流場資料字典而非繪圖
       return {
           'pressure': p.tolist(),
           'velocity_u': u.tolist(),
           'velocity_v': v.tolist(),
           'x_coords': x.tolist(),
           'y_coords': y.tolist(),
           'convergence_history': [...]
       }
   ```

3. **進度回調機制**:
   ```python
   if it % 10 == 0 and progress_callback:
       progress_callback({
           'iteration': it,
           'residual_u': residual_u,
           'residual_v': residual_v
       })
   ```

**理由**:
- ✅ 符合憲法原則 III (簡約設計): 最小化修改
- ✅ 保持演算法正確性: 不改動數值方法邏輯
- ✅ 易於測試: 包裝器可以獨立測試

**替代方案被拒絕**:
- ❌ 重寫為物件導向類別: 過度設計,違反簡約原則
- ❌ 直接修改 simplec.py: 破壞現有可執行腳本

---

## 2. FastAPI + WebSocket 最佳實務

### 研究問題
- 如何在 FastAPI 中管理長時間運行的背景任務?
- WebSocket 進度更新模式?
- 錯誤處理和斷線重連?

### 決策: BackgroundTasks + WebSocket Manager

**方案**:

1. **背景任務執行**:
   ```python
   from fastapi import BackgroundTasks

   @app.post("/api/simulations")
   async def create_simulation(
       params: SimulationParameters,
       background_tasks: BackgroundTasks
   ):
       job_id = str(uuid.uuid4())
       background_tasks.add_task(run_simulation, job_id, params)
       return {"job_id": job_id, "status": "PENDING"}
   ```

2. **WebSocket Manager 單例模式**:
   ```python
   class ConnectionManager:
       def __init__(self):
           self.active_connections: Dict[str, WebSocket] = {}

       async def connect(self, job_id: str, websocket: WebSocket):
           await websocket.accept()
           self.active_connections[job_id] = websocket

       async def send_progress(self, job_id: str, data: dict):
           if job_id in self.active_connections:
               await self.active_connections[job_id].send_json(data)

   manager = ConnectionManager()  # 全域單例
   ```

3. **錯誤處理**:
   - 捕獲求解器例外,更新任務狀態為 FAILED
   - WebSocket 斷線時清理連線,但求解繼續執行
   - 前端可透過 REST API 輪詢狀態

**理由**:
- ✅ FastAPI 內建支援 BackgroundTasks,無需額外依賴
- ✅ WebSocket Manager 簡單實用,適合單使用者 MVP
- ✅ 符合憲法原則 III: 避免引入 Celery 等重量級任務佇列

**替代方案被拒絕**:
- ❌ Celery + Redis: 過度設計,MVP 不需要分散式任務佇列
- ❌ asyncio.create_task: 任務管理複雜,缺少進度追蹤機制

---

## 3. Plotly.js 科學視覺化

### 研究問題
- 如何繪製壓力等高線圖?
- 如何繪製速度向量圖?
- 大型陣列資料效能?

### 決策: 使用 Plotly React 組件 + 資料降採樣

**方案**:

1. **壓力等高線圖** (使用 Plotly.js Contour type):
   ```javascript
   import Plot from 'react-plotly.js';

   <Plot
     data={[{
       type: 'contour',
       z: pressureData,  // 2D 陣列
       x: xCoords,
       y: yCoords,
       colorscale: 'Viridis'
     }]}
     layout={{title: '壓力等高線圖'}}
   />
   ```

2. **速度向量圖** (使用 Cone or Quiver):
   ```javascript
   <Plot
     data={[{
       type: 'cone',
       x: xGrid,
       y: yGrid,
       z: Array(N).fill(0),  // 2D 平面
       u: velocityU,
       v: velocityV,
       w: Array(N).fill(0)
     }]}
   />
   ```

3. **資料降採樣** (如果網格 > 100x100):
   ```python
   def downsample(data, target_size=50):
       factor = max(data.shape[0] // target_size, 1)
       return data[::factor, ::factor]
   ```

**理由**:
- ✅ Plotly.js 專為科學視覺化設計,內建等高線和向量場
- ✅ react-plotly.js 提供 React 整合
- ✅ 互動功能 (縮放、平移、懸停) 開箱即用

**效能考量**:
- 41x41 網格: 1681 個點,資料量 ~50 KB (JSON),無需優化
- 若未來支援 200x200: 40000 點,約 1.2 MB,考慮降採樣

**替代方案被拒絕**:
- ❌ D3.js: 需要手動實作等高線演算法,開發成本高
- ❌ Chart.js: 不支援科學視覺化 (無等高線、向量場)

---

## 4. 資料序列化

### 研究問題
- Numpy 陣列 → JSON 轉換最佳方案?
- 是否需要壓縮?

### 決策: tolist() + 精度控制

**方案**:

1. **Numpy → JSON**:
   ```python
   import numpy as np
   import json

   def serialize_array(arr, precision=6):
       # 四捨五入減少資料量
       rounded = np.round(arr, precision)
       return rounded.tolist()

   results = {
       'pressure': serialize_array(p, precision=6),
       'velocity_u': serialize_array(u, precision=6),
       'velocity_v': serialize_array(v, precision=6)
   }
   json_str = json.dumps(results)
   ```

2. **精度控制**:
   - 預設保留 6 位小數 (科學計算足夠)
   - 41x41 網格: 約 1681 * 3 陣列 * 8 bytes/float ≈ 40 KB (原始)
   - JSON 編碼後: 約 150-200 KB (可接受)

3. **不使用壓縮** (MVP 階段):
   - 資料量 < 1 MB,瀏覽器處理無壓力
   - 避免引入 gzip 解壓縮複雜度

**理由**:
- ✅ 簡單直接,無額外依賴
- ✅ FastAPI 自動處理 JSON 序列化
- ✅ 符合憲法原則 III: 避免預先優化

**未來優化選項** (若網格變大):
- 選項 A: gzip 壓縮 (可減少 70-80% 體積)
- 選項 B: Base64 編碼二進位資料
- 選項 C: 使用 MessagePack 替代 JSON

**替代方案被拒絕**:
- ❌ Protocol Buffers: 過度設計,需要 schema 定義
- ❌ HDF5 over HTTP: 瀏覽器支援不佳

---

## 5. 前端狀態管理

### 研究問題
- 使用 Redux 還是 React Context?
- 如何管理 WebSocket 連線狀態?

### 決策: React Context + Custom Hooks

**方案**:

1. **SimulationContext** 管理全域狀態:
   ```javascript
   const SimulationContext = createContext();

   export function SimulationProvider({ children }) {
       const [job, setJob] = useState(null);
       const [progress, setProgress] = useState(null);
       const [results, setResults] = useState(null);

       return (
           <SimulationContext.Provider value={{
               job, setJob,
               progress, setProgress,
               results, setResults
           }}>
               {children}
           </SimulationContext.Provider>
       );
   }
   ```

2. **useWebSocket Custom Hook**:
   ```javascript
   function useWebSocket(jobId) {
       const { setProgress } = useContext(SimulationContext);

       useEffect(() => {
           if (!jobId) return;

           const ws = new WebSocket(`ws://localhost:8000/ws/simulation/${jobId}`);
           ws.onmessage = (event) => {
               setProgress(JSON.parse(event.data));
           };

           return () => ws.close();
       }, [jobId]);
   }
   ```

**理由**:
- ✅ 符合憲法原則 V: "優先使用 React Context"
- ✅ 簡約設計: 狀態結構簡單 (job, progress, results)
- ✅ MVP 不需要 Redux 的時間旅行除錯、中介軟體等進階功能

**替代方案被拒絕**:
- ❌ Redux: 過度設計,引入額外複雜度 (actions, reducers, store)
- ❌ MobX: 額外學習成本,MVP 不需要響應式狀態管理

---

## 6. 測試策略

### 研究問題
- 如何測試 CFD 演算法正確性?
- 如何測試 WebSocket 通訊?

### 決策: 多層測試策略

**方案**:

1. **後端單元測試** (pytest):
   ```python
   def test_solve_cavity_flow_converges():
       params = SimulationParameters(
           reynolds_number=100,
           nx=21, ny=21,
           max_iter=1000
       )
       results = solve_cavity_flow(params)
       assert results['final_residuals']['u'] < 1e-5
   ```

2. **API 整合測試** (pytest + httpx):
   ```python
   def test_create_simulation_endpoint():
       response = client.post("/api/simulations", json={
           "reynolds_number": 100,
           "nx": 21, "ny": 21
       })
       assert response.status_code == 200
       assert "job_id" in response.json()
   ```

3. **WebSocket 測試** (pytest-asyncio):
   ```python
   async def test_websocket_progress_updates():
       async with client.websocket_connect(f"/ws/simulation/{job_id}") as ws:
           data = await ws.receive_json()
           assert "iteration" in data
   ```

4. **前端組件測試** (Jest + React Testing Library):
   ```javascript
   test('ParameterForm validates input', () => {
       render(<ParameterForm />);
       const input = screen.getByLabelText('Reynolds Number');
       fireEvent.change(input, { target: { value: '-10' } });
       expect(screen.getByText('必須為正數')).toBeInTheDocument();
   });
   ```

**理由**:
- ✅ 符合憲法原則 II: 多層測試確保正確性
- ✅ 覆蓋率目標 ≥ 80%

---

## Summary

| 技術領域 | 決策 | 理由 |
|---------|------|------|
| simplec.py 整合 | 包裝器模式 + 進度回調 | 簡約,保持演算法不變 |
| 背景任務 | FastAPI BackgroundTasks | 內建支援,無需額外依賴 |
| 即時通訊 | WebSocket Manager 單例 | 簡單實用,適合 MVP |
| 視覺化 | Plotly.js (Contour + Cone) | 科學視覺化專用,互動功能完整 |
| 資料序列化 | tolist() + 精度控制 | 簡單直接,效能足夠 |
| 狀態管理 | React Context + Custom Hooks | 符合憲法,避免過度設計 |
| 測試 | pytest + Jest 多層策略 | 確保 CFD 正確性和系統穩定性 |

**所有決策均符合專案憲法原則,無例外需求。**

**下一步**: 產生 data-model.md, contracts/, quickstart.md
