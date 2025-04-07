import { getCurrentUser, fetchAuthSession, signOut } from 'aws-amplify/auth';
import { getAuthHeaders } from '../../services/api'; // We'll need to extract this function

jest.mock('aws-amplify/auth');

describe('Authentication Services', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('getAuthHeaders returns valid headers with token', async () => {
    const headers = await getAuthHeaders();
    
    expect(fetchAuthSession).toHaveBeenCalled();
    expect(headers).toEqual({
      Authorization: 'Bearer mock-id-token'
    });
  });

  test('getAuthHeaders calls signOut when session fetch fails', async () => {
    (fetchAuthSession as jest.Mock).mockRejectedValueOnce(new Error('Session error'));
    
    await expect(getAuthHeaders()).rejects.toThrow('Authentication required');
    expect(signOut).toHaveBeenCalled();
  });
});