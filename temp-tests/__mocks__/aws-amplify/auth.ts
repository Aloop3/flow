export const signOut = jest.fn().mockResolvedValue(true);
export const getCurrentUser = jest.fn().mockResolvedValue({
  userId: 'test-user-id',
  username: 'testuser',
  attributes: {
    email: 'test@example.com',
    name: 'Test User'
  }
});
export const fetchAuthSession = jest.fn().mockResolvedValue({
  tokens: {
    idToken: {
      toString: () => 'mock-id-token'
    }
  }
});

// src/__mocks__/aws-amplify/api.ts
export const get = jest.fn();
export const post = jest.fn();
export const put = jest.fn();
export const del = jest.fn();