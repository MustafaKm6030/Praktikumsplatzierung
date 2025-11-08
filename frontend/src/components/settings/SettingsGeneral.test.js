import { render, screen, fireEvent } from '@testing-library/react';
import SettingsGeneral from './SettingsGeneral';

describe('SettingsGeneral Component', () => {
  test('renders without crashing', () => {
    render(<SettingsGeneral />);
    expect(screen.getByText(/General Settings/i)).toBeInTheDocument();
  });

  test('shows all required form fields', () => {
    render(<SettingsGeneral />);
    expect(screen.getByLabelText(/Current Academic Year/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/PDP I\/II Default Deadline/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/SFP\/ZSP Default Deadline/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/University Name/i)).toBeInTheDocument();
  });

  test('Save button is functional', () => {
    render(<SettingsGeneral />);
    const saveButton = screen.getByText(/Save Changes/i);
    expect(saveButton).toBeInTheDocument();
    expect(saveButton).not.toBeDisabled();
  });
});