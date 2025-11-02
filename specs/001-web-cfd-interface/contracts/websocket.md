# WebSocket 協定規格

**Endpoint**: `ws://localhost:8000/ws/simulation/{job_id}`

**用途**: 即時推送 CFD 求解進度更新

---

## 連線建立

### 客戶端請求

```
GET ws://localhost:8000/ws/simulation/123e4567-e89b-12d3-a456-426614174000
Upgrade: websocket
Connection: Upgrade
```

### 伺服器回應

**成功**:
```
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
```

**失敗 (任務不存在)**:
```
HTTP/1.1 404 Not Found
```

---

## 訊息格式

### 進度更新訊息 (Server → Client)

**頻率**: 每 10 次迭代或每秒 (取較快者)

**格式**:
```json
{
  "type": "progress",
  "data": {
    "job_id": "123e4567-e89b-12d3-a456-426614174000",
    "iteration": 100,
    "residual_u": 0.001234,
    "residual_v": 0.000987,
    "elapsed_time": 5.32,
    "estimated_remaining": 45.2
  }
}
```

### 完成訊息 (Server → Client)

**觸發時機**: 求解器收斂或達到最大迭代次數

**格式**:
```json
{
  "type": "completed",
  "data": {
    "job_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "COMPLETED",
    "final_iteration": 1523,
    "final_residuals": {
      "u": 9.8e-6,
      "v": 8.7e-6
    },
    "total_time": 28.4
  }
}
```

### 錯誤訊息 (Server → Client)

**觸發時機**: 求解器執行失敗

**格式**:
```json
{
  "type": "error",
  "data": {
    "job_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "FAILED",
    "error_message": "求解發散: 殘差超過 1e10",
    "last_iteration": 234
  }
}
```

---

## 連線生命週期

```
客戶端                                  伺服器
  │                                      │
  │──── WebSocket 連線請求 ────────────→│
  │                                      │
  │←─── 接受連線 (101 Switching) ──────│
  │                                      │
  │                                      │ (求解器執行中...)
  │←─── progress 訊息 ────────────────│ (每 10 次迭代)
  │←─── progress 訊息 ────────────────│
  │←─── progress 訊息 ────────────────│
  │                                      │
  │←─── completed 訊息 ────────────────│ (求解完成)
  │                                      │
  │──── 關閉連線 ────────────────────→│
  │←─── 確認關閉 ──────────────────────│
```

---

## 錯誤處理

### 斷線重連機制

**客戶端實作**:
```javascript
class SimulationWebSocket {
  constructor(jobId) {
    this.jobId = jobId;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.connect();
  }

  connect() {
    this.ws = new WebSocket(`ws://localhost:8000/ws/simulation/${this.jobId}`);

    this.ws.onclose = () => {
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        setTimeout(() => {
          this.reconnectAttempts++;
          this.connect();
        }, 1000 * this.reconnectAttempts); // 指數退避
      }
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };
  }

  handleMessage(message) {
    switch (message.type) {
      case 'progress':
        // 更新進度 UI
        break;
      case 'completed':
        // 取得結果並顯示
        this.ws.close();
        break;
      case 'error':
        // 顯示錯誤訊息
        this.ws.close();
        break;
    }
  }
}
```

---

## 測試場景

### 正常流程
1. 客戶端建立 WebSocket 連線
2. 接收多個 progress 訊息
3. 接收 completed 訊息
4. 關閉連線

### 求解失敗流程
1. 客戶端建立 WebSocket 連線
2. 接收數個 progress 訊息
3. 接收 error 訊息 (求解發散)
4. 關閉連線

### 斷線重連流程
1. 客戶端建立連線
2. 網路中斷
3. 客戶端偵測到 onclose
4. 等待 1 秒後重連
5. 重新接收 progress 訊息

---

## 效能考量

- **訊息頻率**: 最多每秒 1 次 (避免過度更新)
- **訊息大小**: < 1 KB (純進度資訊)
- **連線數**: MVP 支援 1 個同時連線 (單使用者)
- **超時**: 若 30 秒無訊息,客戶端應檢查任務狀態

---

## 安全性 (未來考量)

- 身份驗證: 使用 JWT token 在連線時驗證
- 授權: 確保只能訂閱自己的任務
- 加密: wss:// (WebSocket Secure)
