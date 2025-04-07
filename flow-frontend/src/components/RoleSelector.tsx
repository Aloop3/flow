import { useState } from 'react';
import { createUser } from '../services/api';

interface RoleSelectorProps {
  user: any;
  onRoleSelected: () => void;
}

const RoleSelector = ({ user, onRoleSelected }: RoleSelectorProps) => {
  const [role, setRole] = useState<'athlete' | 'coach' | 'both' | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRoleSelection = async () => {
    if (!role) return;
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      // Create user in DynamoDB with selected role
      console.log('Creating user with role:', role);
      await createUser({
        email: user.attributes?.email || '',
        name: user.attributes?.name || user.username || '',
        role
      });
      console.log('User created successfully, calling onRoleSelected');
      onRoleSelected();
    } catch (error) {
      console.error('Error setting user role:', error);
      setError('Failed to set role. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Welcome to Flow
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Select how you'll be using the app
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {error && (
            <div className="mb-4 bg-red-50 p-4 rounded-md">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}
          
          <div className="space-y-4">
            <button
              onClick={() => setRole('athlete')}
              className={`w-full p-4 rounded-lg border-2 flex items-center justify-center ${
                role === 'athlete' 
                  ? 'border-blue-500 bg-blue-50 text-blue-700' 
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <div className="text-left">
                <p className="font-medium">Athlete</p>
                <p className="text-sm text-gray-500">Track workouts and progress</p>
              </div>
            </button>
            
            <button
              onClick={() => setRole('coach')}
              className={`w-full p-4 rounded-lg border-2 flex items-center justify-center ${
                role === 'coach' 
                  ? 'border-blue-500 bg-blue-50 text-blue-700' 
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <div className="text-left">
                <p className="font-medium">Coach</p>
                <p className="text-sm text-gray-500">Create programs for athletes</p>
              </div>
            </button>
            
            <button
              onClick={() => setRole('both')}
              className={`w-full p-4 rounded-lg border-2 flex items-center justify-center ${
                role === 'both' 
                  ? 'border-blue-500 bg-blue-50 text-blue-700' 
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <div className="text-left">
                <p className="font-medium">Both</p>
                <p className="text-sm text-gray-500">Coach athletes and track your own workouts</p>
              </div>
            </button>
          </div>
          
          <div className="mt-6">
            <button
              type="button"
              onClick={handleRoleSelection}
              disabled={!role || isSubmitting}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Setting up your account...' : 'Continue'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RoleSelector;