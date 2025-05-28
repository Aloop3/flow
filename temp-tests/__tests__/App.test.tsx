import { render, screen, waitFor } from '@testing-library/react';
import App from '../App';
import { getCurrentUser } from 'aws-amplify/auth';
import { getUser } from '../services/api';

jest.mock('aws-amplify/auth', () => ({
  getCurrentUser: jest.fn(),
  fetchAuthSession: jest.fn(),
  signOut: jest.fn()
}));

jest.mock('../services/api', () => ({
  getUser: jest.fn()
}));

// Mock the Authenticator component
jest.mock('@aws-amplify/ui-react', () => ({
  Authenticator: ({ children }: any) => children({ 
    signOut: jest.fn(),
    user: { userId: 'test-user-id', username: 'testuser' } 
  })
}));

// Mock components
jest.mock('../components/RoleSelector', () => () => <div data-testid="role-selector" />);
jest.mock('../pages/Dashboard', () => () => <div data-testid="dashboard" />);

describe('App Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('shows loading state initially', async () => {
    (getCurrentUser as jest.Mock).mockResolvedValue({ userId: 'test-user-id' });
    (getUser as jest.Mock).mockImplementation(() => new Promise(() => {})); // Never resolves
    
    render(<App />);
    
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument(); // Loading indicator
  });

  test('shows RoleSelector when user exists but has no DB record', async () => {
    (getCurrentUser as jest.Mock).mockResolvedValue({ userId: 'test-user-id' });
    (getUser as jest.Mock).mockRejectedValue(new Error('User not found'));
    
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByTestId('role-selector')).toBeInTheDocument();
    });
  });

  test('shows main app when user exists and has DB record', async () => {
    (getCurrentUser as jest.Mock).mockResolvedValue({ userId: 'test-user-id' });
    (getUser as jest.Mock).mockResolvedValue({ 
      user_id: 'test-user-id',
      email: 'test@example.com',
      name: 'Test User',
      role: 'athlete'
    });
    
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByTestId('dashboard')).toBeInTheDocument();
    });
  });
});