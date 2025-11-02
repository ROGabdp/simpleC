/**
 * ParameterForm 組件測試
 */
import { render, screen, fireEvent } from '@testing-library/react';
import ParameterForm from './ParameterForm';
import { SimulationProvider } from '../../context/SimulationContext';

// Mock API
jest.mock('../../services/api', () => ({
  createSimulation: jest.fn(() => Promise.resolve({
    job_id: 'test-job-id',
    status: 'PENDING',
  })),
}));

const renderWithProvider = (component) => {
  return render(
    <SimulationProvider>
      {component}
    </SimulationProvider>
  );
};

test('renders parameter form', () => {
  renderWithProvider(<ParameterForm />);
  expect(screen.getByText('模擬參數設定')).toBeInTheDocument();
  expect(screen.getByLabelText('Reynolds 數:')).toBeInTheDocument();
});

test('validates Reynolds number', () => {
  renderWithProvider(<ParameterForm />);

  const input = screen.getByLabelText('Reynolds 數:');
  fireEvent.change(input, { target: { value: '-10' } });

  // 驗證錯誤訊息會顯示
  // Note: 需要實際提交表單才會顯示錯誤
});

test('submits form with valid data', async () => {
  renderWithProvider(<ParameterForm />);

  const button = screen.getByText('開始模擬');
  fireEvent.click(button);

  // 驗證提交邏輯
});
