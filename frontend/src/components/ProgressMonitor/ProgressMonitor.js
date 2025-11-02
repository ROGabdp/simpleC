/**
 * 進度監控組件
 */
import React, { useEffect, useState } from 'react';
import { useSimulation } from '../../context/SimulationContext';
import SimulationWebSocket from '../../services/websocket';
import { getSimulationResults } from '../../services/api';
import './ProgressMonitor.css';

function ProgressMonitor() {
  const { job, progress, setProgress, setResults, setError } = useSimulation();
  const [ws, setWs] = useState(null);
  const [status, setStatus] = useState('PENDING');

  useEffect(() => {
    if (!job) return;

    setStatus(job.status);

    // 建立 WebSocket 連線
    const websocket = new SimulationWebSocket(
      job.job_id,
      // onProgress
      (progressData) => {
        setProgress(progressData);
        setStatus('RUNNING');
      },
      // onCompleted
      async (message) => {
        setStatus('COMPLETED');
        // 載入結果
        try {
          const results = await getSimulationResults(job.job_id);
          setResults(results);
        } catch (error) {
          setError('載入結果失敗: ' + error.message);
        }
      },
      // onError
      (errorMessage) => {
        setStatus('FAILED');
        setError(errorMessage);
      }
    );

    websocket.connect();
    setWs(websocket);

    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, [job]);

  if (!job) {
    return null;
  }

  const getStatusText = () => {
    switch (status) {
      case 'PENDING':
        return '等待中';
      case 'RUNNING':
        return '執行中';
      case 'COMPLETED':
        return '已完成';
      case 'FAILED':
        return '失敗';
      default:
        return status;
    }
  };

  const getStatusClass = () => {
    switch (status) {
      case 'RUNNING':
        return 'status-running';
      case 'COMPLETED':
        return 'status-completed';
      case 'FAILED':
        return 'status-failed';
      default:
        return 'status-pending';
    }
  };

  return (
    <div className="progress-monitor">
      <div className="status-header">
        <h3>模擬狀態</h3>
        <span className={`status-badge ${getStatusClass()}`}>
          {getStatusText()}
        </span>
      </div>

      {status === 'RUNNING' && progress && (
        <div className="progress-details">
          <div className="progress-item">
            <span className="label">迭代次數:</span>
            <span className="value">{progress.iteration}</span>
          </div>
          <div className="progress-item">
            <span className="label">U 速度殘差:</span>
            <span className="value">{progress.residual_u?.toExponential(4)}</span>
          </div>
          <div className="progress-item">
            <span className="label">V 速度殘差:</span>
            <span className="value">{progress.residual_v?.toExponential(4)}</span>
          </div>
          <div className="progress-item">
            <span className="label">已執行時間:</span>
            <span className="value">{progress.elapsed_time?.toFixed(2)} 秒</span>
          </div>

          <div className="loading-spinner">
            <div className="spinner"></div>
          </div>
        </div>
      )}

      {status === 'COMPLETED' && (
        <div className="completion-message">
          <svg className="check-icon" viewBox="0 0 24 24">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
          </svg>
          <p>模擬已成功完成!</p>
        </div>
      )}

      {status === 'FAILED' && (
        <div className="error-message">
          <p>模擬執行失敗</p>
        </div>
      )}
    </div>
  );
}

export default ProgressMonitor;
