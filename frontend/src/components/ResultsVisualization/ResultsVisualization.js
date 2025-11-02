/**
 * 結果視覺化主組件
 */
import React from 'react';
import { useSimulation } from '../../context/SimulationContext';
import PressureContour from './PressureContour';
import VelocityVector from './VelocityVector';
import CenterlineProfile from './CenterlineProfile';
import './ResultsVisualization.css';

function ResultsVisualization() {
  const { results } = useSimulation();

  if (!results) {
    return null;
  }

  return (
    <div className="results-visualization">
      <h2>模擬結果</h2>

      <div className="results-info">
        <p>總迭代次數: {results.total_iterations || 'N/A'}</p>
        <p>計算時間: {results.elapsed_time?.toFixed(2) || 'N/A'} 秒</p>
        <p>
          最終殘差: U = {results.final_residuals?.u?.toExponential(4) || 'N/A'},
          V = {results.final_residuals?.v?.toExponential(4) || 'N/A'}
        </p>
        <p>收斂狀態: {results.converged ? '已收斂 ✓' : '未收斂'}</p>
      </div>

      <div className="visualization-grid">
        <div className="viz-item">
          <PressureContour results={results} />
        </div>

        <div className="viz-item">
          <VelocityVector results={results} />
        </div>

        <div className="viz-item full-width">
          <CenterlineProfile results={results} />
        </div>
      </div>
    </div>
  );
}

export default ResultsVisualization;
