import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import RoleSelector from '../../components/RoleSelector';
import { createUser } from '../../services/api';

jest.mock('../../services/api', () => ({
  createUser: jest.fn()
}));

describe('RoleSelector Component', () => {
  const mockUser = {
    attributes: {
      email: 'test@example.com',
      name: 'Test User'
    }
  };
  
  const mockOnRoleSelected = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders role selection options', () => {
    render(<RoleSelector user={mockUser} onRoleSelected={mockOnRoleSelected} />);
    
    expect(screen.getByText('Welcome to Flow')).toBeInTheDocument();
    expect(screen.getByText('Athlete')).toBeInTheDocument();
    expect(screen.getByText('Coach')).toBeInTheDocument();
    expect(screen.getByText('Both')).toBeInTheDocument();
    
    // Continue button should be disabled initially
    const continueButton = screen.getByText('Continue');
    expect(continueButton).toBeDisabled();
  });

  test('enables continue button when role is selected', () => {
    render(<RoleSelector user={mockUser} onRoleSelected={mockOnRoleSelected} />);
    
    // Select a role
    fireEvent.click(screen.getByText('Athlete'));
    
    // Continue button should be enabled
    const continueButton = screen.getByText('Continue');
    expect(continueButton).not.toBeDisabled();
  });

  test('calls createUser with correct data when role is submitted', async () => {
    (createUser as jest.Mock).mockResolvedValueOnce({ user_id: 'new-user-id' });
    
    render(<RoleSelector user={mockUser} onRoleSelected={mockOnRoleSelected} />);
    
    // Select a role
    fireEvent.click(screen.getByText('Coach'));
    
    // Submit the form
    fireEvent.click(screen.getByText('Continue'));
    
    await waitFor(() => {
      expect(createUser).toHaveBeenCalledWith({
        email: 'test@example.com',
        name: 'Test User',
        role: 'coach'
      });
      expect(mockOnRoleSelected).toHaveBeenCalled();
    });
  });

  test('shows error message when createUser fails', async () => {
    (createUser as jest.Mock).mockRejectedValueOnce(new Error('API error'));
    
    render(<RoleSelector user={mockUser} onRoleSelected={mockOnRoleSelected} />);
    
    // Select a role and submit
    fireEvent.click(screen.getByText('Both'));
    fireEvent.click(screen.getByText('Continue'));
    
    // Error message should be displayed
    await waitFor(() => {
      expect(screen.getByText('Failed to set role. Please try again.')).toBeInTheDocument();
      expect(mockOnRoleSelected).not.toHaveBeenCalled();
    });
  });
});