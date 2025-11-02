/**
 * CFD 求解器主應用程式
 */
import React from 'react';
import { SimulationProvider, useSimulation } from './context/SimulationContext';
import ParameterForm from './components/ParameterForm/ParameterForm';
import ProgressMonitor from './components/ProgressMonitor/ProgressMonitor';
import ResultsVisualization from './components/ResultsVisualization/ResultsVisualization';
import './App.css';

function AppContent() {
  const { job, results, error, resetSimulation } = useSimulation();

  return (
    <div className="App">
      <header className="App-header">
        <h1>CFD 求解器 Web 介面</h1>
        <p>SIMPLEC 演算法 - 蓋驅動方腔流</p>
      </header>

      <main className="App-main">
        {error && (
          <div className="error-banner">
            <p>{error}</p>
          </div>
        )}

        {!job && <ParameterForm />}

        {job && !results && <ProgressMonitor />}

        {results && (
          <>
            <ResultsVisualization />
            <div className="reset-button-container">
              <button onClick={resetSimulation} className="reset-button">
                開始新模擬
              </button>
            </div>
          </>
        )}
      </main>

      <footer className="App-footer">
        <p>© 2025 CFD 求解器 | SIMPLEC 演算法</p>
      </footer>
    </div>
  );
}

function App() {
  return (
    <SimulationProvider>
      <AppContent />
    </SimulationProvider>
  );
}

export default App;
