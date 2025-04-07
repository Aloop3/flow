import { get, post, put, del } from 'aws-amplify/api';
import { 
  getUser, createUser, updateUser, 
  getBlocks, getBlock, createBlock, updateBlock, deleteBlock 
} from '../../services/api';

jest.mock('aws-amplify/auth', () => ({
  fetchAuthSession: jest.fn().mockResolvedValue({
    tokens: {
      idToken: {
        toString: () => 'mock-id-token'
      }
    }
  }),
  signOut: jest.fn()
}));

jest.mock('aws-amplify/api', () => ({
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    del: jest.fn()
  }));
  

describe('API Services', () => {
  const mockHeaders = { Authorization: 'Bearer mock-id-token' };
  
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // User API tests
  describe('User API', () => {
    test('getUser fetches user data correctly', async () => {
      const mockUser = { 
        user_id: 'test-user-id', 
        email: 'test@example.com',
        name: 'Test User',
        role: 'athlete'
      };
      
      (get as jest.Mock).mockResolvedValueOnce(mockUser);
      
      const result = await getUser('test-user-id');
      
      expect(get).toHaveBeenCalledWith({
        apiName: 'flow-api',
        path: '/users/test-user-id',
        options: { headers: mockHeaders }
      });
      expect(result).toEqual(mockUser);
    });

    test('createUser sends correct payload', async () => {
      const userData = {
        email: 'new@example.com',
        name: 'New User',
        role: 'coach' as 'athlete' | 'coach'
      };
      
      const mockResponse = { ...userData, user_id: 'new-user-id' };
      (post as jest.Mock).mockResolvedValueOnce(mockResponse);
      
      const result = await createUser(userData);
      
      expect(post).toHaveBeenCalledWith({
        apiName: 'flow-api',
        path: '/users',
        options: {
          headers: mockHeaders,
          body: userData
        }
      });
      expect(result).toEqual(mockResponse);
    });

    test('updateUser sends correct payload', async () => {
      const updateData = { name: 'Updated Name' };
      const mockResponse = { 
        user_id: 'test-user-id',
        email: 'test@example.com',
        name: 'Updated Name',
        role: 'athlete'
      };
      
      (put as jest.Mock).mockResolvedValueOnce(mockResponse);
      
      const result = await updateUser('test-user-id', updateData);
      
      expect(put).toHaveBeenCalledWith({
        apiName: 'flow-api',
        path: '/users/test-user-id',
        options: {
          headers: mockHeaders,
          body: updateData
        }
      });
      expect(result).toEqual(mockResponse);
    });
  });

  // Block API tests
  describe('Block API', () => {
    test('getBlocks fetches blocks correctly', async () => {
      const mockBlocks = [
        { block_id: 'block-1', title: 'Block 1', status: 'active' },
        { block_id: 'block-2', title: 'Block 2', status: 'draft' }
      ];
      
      (get as jest.Mock).mockResolvedValueOnce(mockBlocks);
      
      const result = await getBlocks('athlete-id');
      
      expect(get).toHaveBeenCalledWith({
        apiName: 'flow-api',
        path: '/athletes/athlete-id/blocks',
        options: { headers: mockHeaders }
      });
      expect(result).toEqual(mockBlocks);
    });

    test('getBlock fetches a single block correctly', async () => {
      const mockBlock = { 
        block_id: 'block-1', 
        title: 'Block 1', 
        status: 'active' 
      };
      
      (get as jest.Mock).mockResolvedValueOnce(mockBlock);
      
      const result = await getBlock('block-1');
      
      expect(get).toHaveBeenCalledWith({
        apiName: 'flow-api',
        path: '/blocks/block-1',
        options: { headers: mockHeaders }
      });
      expect(result).toEqual(mockBlock);
    });

    test('deleteBlock calls the correct endpoint', async () => {
      await deleteBlock('block-1');
      
      expect(del).toHaveBeenCalledWith({
        apiName: 'flow-api',
        path: '/blocks/block-1',
        options: { headers: mockHeaders }
      });
    });
  });

  // Error handling tests
  describe('Error handling', () => {
    test('API calls handle errors correctly', async () => {
      const errorMessage = 'Network error';
      (get as jest.Mock).mockRejectedValueOnce(new Error(errorMessage));
      
      console.error = jest.fn(); // Mock console.error
      
      await expect(getUser('user-id')).rejects.toThrow();
      expect(console.error).toHaveBeenCalledWith(
        'Error fetching user:', 
        expect.any(Error)
      );
    });
  });
});