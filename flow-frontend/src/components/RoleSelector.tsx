import { useState } from 'react';
import { updateUser } from '../services/api';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface RoleSelectorProps {
  user: any;
  onRoleSelected: () => void;
}

const RoleSelector = ({ user, onRoleSelected }: RoleSelectorProps) => {
  const [role, setRole] = useState<'athlete' | 'coach' | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRoleSelection = async () => {
    if (!role) return;
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      // Log the user object to debug
      console.log("User object from Cognito:", user);
      
      // Get the correct user ID
      const userId = user.userId || user.username || user.attributes?.sub;
      console.log("Using user ID for update:", userId);
      
      // Make sure we're sending a properly formatted request
      const userData = {
        role: role
      };
      console.log("Sending role update:", userData);
      
      // Update user with selected role
      const updatedUser = await updateUser(userId, userData);
      console.log("Role update successful:", updatedUser);
      
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
        <Card>
          <CardContent className="pt-6">
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
                  <p className="text-sm text-gray-500">Track workouts and self-coach</p>
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

              <div className="mt-6">
                <Button
                  type="button"
                  onClick={handleRoleSelection}
                  disabled={!role || isSubmitting}
                  className="w-full"
                >
                  {isSubmitting ? 'Setting up your account...' : 'Continue'}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default RoleSelector;