import { render, screen, waitFor } from '@testing-library/react';
import SettingsGeneral from './SettingsGeneral';
import settingsService from '../../api/settingsService';

jest.mock('../../api/settingsService');

const mockSettings = {
  id: 1,
  current_academic_year: '2024/2025',
  pdp_i_demand_deadline: '2025-05-01',
  pl_assignment_deadline: '2025-06-15',
  university_name: 'Universität Passau',
  contact_email: 'test@uni-passau.de',
  contact_phone: '+49 851 509-0',
  total_credit_hour_budget: 210.00,
  gs_budget_percentage: 80.48,
  ms_budget_percentage: 19.52,
};

describe('SettingsGeneral Component', () => {
  beforeEach(() => {
    settingsService.getActive.mockResolvedValue({ data: mockSettings });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders without crashing', async () => {
    render(<SettingsGeneral />);
    await waitFor(() => {
      expect(screen.getByText(/General Settings/i)).toBeInTheDocument();
    });
  });

  test('shows all required form fields', async () => {
    render(<SettingsGeneral />);
    await waitFor(() => {
      expect(screen.getByLabelText(/Current Academic Year/i)).toBeInTheDocument();
    });
    expect(screen.getByLabelText(/PDP I\/II Default Deadline/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/SFP\/ZSP Default Deadline/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/University Name/i)).toBeInTheDocument();
  });

  test('Save button is functional', async () => {
    render(<SettingsGeneral />);
    await waitFor(() => {
      const saveButton = screen.getByText(/Save Changes/i);
      expect(saveButton).toBeInTheDocument();
      expect(saveButton).not.toBeDisabled();
    });
  });
});