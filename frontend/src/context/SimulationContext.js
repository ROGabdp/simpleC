/**
 * 模擬狀態管理 - 使用 React Context
 */
import React, { createContext, useState, useContext } from 'react';

const SimulationContext = createContext();

export function SimulationProvider({ children }) {
  const [job, setJob] = useState(null);
  const [progress, setProgress] = useState(null);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const resetSimulation = () => {
    setJob(null);
    setProgress(null);
    setResults(null);
    setError(null);
  };

  return (
    <SimulationContext.Provider
      value={{
        job,
        setJob,
        progress,
        setProgress,
        results,
        setResults,
        error,
        setError,
        resetSimulation,
      }}
    >
      {children}
    </SimulationContext.Provider>
  );
}

export function useSimulation() {
  const context = useContext(SimulationContext);
  if (!context) {
    throw new Error('useSimulation 必須在 SimulationProvider 內使用');
  }
  return context;
}

export default SimulationContext;
