/**
 * API 客戶端 - 使用 axios 與後端通訊
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * 建立新的模擬任務
 * @param {Object} parameters - 模擬參數
 * @returns {Promise<Object>} 任務資訊
 */
export const createSimulation = async (parameters) => {
  const response = await apiClient.post('/simulations', parameters);
  return response.data;
};

/**
 * 查詢模擬任務狀態
 * @param {string} jobId - 任務 ID
 * @returns {Promise<Object>} 任務狀態
 */
export const getSimulationStatus = async (jobId) => {
  const response = await apiClient.get(`/simulations/${jobId}`);
  return response.data;
};

/**
 * 取得模擬結果
 * @param {string} jobId - 任務 ID
 * @returns {Promise<Object>} 流場結果
 */
export const getSimulationResults = async (jobId) => {
  const response = await apiClient.get(`/simulations/${jobId}/results`);
  return response.data;
};

/**
 * 刪除模擬任務
 * @param {string} jobId - 任務 ID
 * @returns {Promise<void>}
 */
export const deleteSimulation = async (jobId) => {
  await apiClient.delete(`/simulations/${jobId}`);
};

export default apiClient;
