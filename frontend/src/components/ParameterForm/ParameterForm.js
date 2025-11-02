/**
 * 參數輸入表單組件
 */
import React, { useState } from 'react';
import { createSimulation } from '../../services/api';
import { useSimulation } from '../../context/SimulationContext';
import './ParameterForm.css';

function ParameterForm() {
  const { setJob, setError } = useSimulation();

  const [parameters, setParameters] = useState({
    reynolds_number: 100,
    nx: 41,
    ny: 41,
    alpha_u: 0.7,
    alpha_p: 1.0,
    max_iter: 10000,
    tolerance: 0.00001,
    lid_velocity: 1.0,
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // 驗證函式
  const validateField = (name, value) => {
    switch (name) {
      case 'reynolds_number':
        if (value <= 0 || value >= 100000) {
          return 'Reynolds 數必須介於 0 和 100000 之間';
        }
        break;
      case 'nx':
      case 'ny':
        if (value < 10 || value > 200) {
          return '網格數必須介於 10 和 200 之間';
        }
        if (value > 100) {
          return '警告: 大網格可能需要較長計算時間';
        }
        break;
      case 'alpha_u':
      case 'alpha_p':
        if (value <= 0 || value > 1.0) {
          return '鬆弛因子必須介於 0 和 1.0 之間';
        }
        break;
      case 'max_iter':
        if (value < 100 || value > 100000) {
          return '最大迭代次數必須介於 100 和 100000 之間';
        }
        break;
      case 'tolerance':
        if (value <= 0 || value >= 1.0) {
          return '收斂標準必須介於 0 和 1.0 之間';
        }
        break;
      case 'lid_velocity':
        if (value <= 0) {
          return '上蓋速度必須為正數';
        }
        break;
      default:
        break;
    }
    return null;
  };

  // 處理輸入變更
  const handleChange = (e) => {
    const { name, value } = e.target;
    const numValue = parseFloat(value);

    setParameters((prev) => ({
      ...prev,
      [name]: numValue,
    }));

    // 即時驗證
    const error = validateField(name, numValue);
    setErrors((prev) => ({
      ...prev,
      [name]: error,
    }));
  };

  // 處理表單提交
  const handleSubmit = async (e) => {
    e.preventDefault();

    // 驗證所有欄位
    const newErrors = {};
    Object.keys(parameters).forEach((key) => {
      const error = validateField(key, parameters[key]);
      if (error && !error.startsWith('警告')) {
        newErrors[key] = error;
      }
    });

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      // 建立模擬任務
      const job = await createSimulation(parameters);
      setJob(job);
    } catch (error) {
      setError(error.response?.data?.detail || '建立模擬任務失敗');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="parameter-form">
      <h2>模擬參數設定</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="reynolds_number">Reynolds 數:</label>
          <input
            type="number"
            id="reynolds_number"
            name="reynolds_number"
            value={parameters.reynolds_number}
            onChange={handleChange}
            step="1"
            required
          />
          {errors.reynolds_number && (
            <span className="error">{errors.reynolds_number}</span>
          )}
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="nx">X 方向網格數:</label>
            <input
              type="number"
              id="nx"
              name="nx"
              value={parameters.nx}
              onChange={handleChange}
              step="1"
              required
            />
            {errors.nx && <span className="error">{errors.nx}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="ny">Y 方向網格數:</label>
            <input
              type="number"
              id="ny"
              name="ny"
              value={parameters.ny}
              onChange={handleChange}
              step="1"
              required
            />
            {errors.ny && <span className="error">{errors.ny}</span>}
          </div>
        </div>

        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? '正在啟動...' : '開始模擬'}
        </button>
      </form>
    </div>
  );
}

export default ParameterForm;
