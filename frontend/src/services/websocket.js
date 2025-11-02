/**
 * WebSocket 客戶端 - 用於即時進度更新
 */

const WS_BASE_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';

export class SimulationWebSocket {
  constructor(jobId, onProgress, onCompleted, onError) {
    this.jobId = jobId;
    this.onProgress = onProgress;
    this.onCompleted = onCompleted;
    this.onError = onError;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 2000; // 2 秒
  }

  /**
   * 建立 WebSocket 連線
   */
  connect() {
    const url = `${WS_BASE_URL}/simulation/${this.jobId}`;
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log('WebSocket 已連線');
      this.reconnectAttempts = 0;

      // 發送 ping 保持連線
      this.pingInterval = setInterval(() => {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
          this.ws.send('ping');
        }
      }, 30000); // 每 30 秒 ping 一次
    };

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        console.error('解析訊息失敗:', error);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket 錯誤:', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket 已斷線');
      clearInterval(this.pingInterval);
      this.attemptReconnect();
    };
  }

  /**
   * 處理接收到的訊息
   */
  handleMessage(message) {
    switch (message.type) {
      case 'progress':
        if (this.onProgress) {
          this.onProgress(message.data);
        }
        break;

      case 'completed':
        if (this.onCompleted) {
          this.onCompleted(message.message);
        }
        this.close();
        break;

      case 'error':
        if (this.onError) {
          this.onError(message.message);
        }
        this.close();
        break;

      case 'pong':
        // ping-pong 回應,保持連線
        break;

      default:
        console.warn('未知訊息類型:', message.type);
    }
  }

  /**
   * 嘗試重新連線
   */
  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('重新連線次數已達上限');
      if (this.onError) {
        this.onError('無法連線到伺服器');
      }
      return;
    }

    this.reconnectAttempts++;
    console.log(`嘗試重新連線 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

    setTimeout(() => {
      this.connect();
    }, this.reconnectDelay);
  }

  /**
   * 關閉連線
   */
  close() {
    if (this.ws) {
      clearInterval(this.pingInterval);
      this.ws.close();
      this.ws = null;
    }
  }
}

export default SimulationWebSocket;
