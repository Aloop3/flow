import { useState } from 'react';
import { acceptInvitationCode } from '../services/api';
import FormButton from './FormButton';

interface AthleteAcceptSectionProps {
  user: any;
  onAcceptCode: () => void;
}

const AthleteAcceptSection = ({ user, onAcceptCode }: AthleteAcceptSectionProps) => {
  const [code, setCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleAcceptCode = async () => {
    if (!code.trim()) {
      setError('Please enter an invitation code');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      await acceptInvitationCode(user.user_id, code.trim());
      setSuccess('Successfully connected with coach!');
      setCode('');
      
      if (onAcceptCode) {
        onAcceptCode();
      }
    } catch (err: any) {
      // Handle specific error cases
      if (err.response && err.response.status === 400) {
        setError('You already have an active coach. End that relationship first.');
      } else if (err.response && err.response.status === 404) {
        setError('Invalid or expired invitation code.');
      } else {
        setError('Failed to accept invitation. Please try again.');
      }
      console.error('Error accepting invitation:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white shadow rounded-lg p-6 mb-6">
      <h2 className="text-lg font-medium mb-4">Connect with a Coach</h2>
      
      {error && (
        <div className="mb-4 bg-red-50 text-red-700 p-3 rounded-md border border-red-200">
          {error}
        </div>
      )}
      
      {success && (
        <div className="mb-4 bg-green-50 text-green-700 p-3 rounded-md border border-green-200">
          {success}
        </div>
      )}
      
      <div>
        <label htmlFor="inviteCode" className="block text-sm font-medium text-gray-700 mb-1">
          Enter Invitation Code
        </label>
        <div className="flex space-x-2">
          <input
            type="text"
            id="inviteCode"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            className="flex-1 border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="Enter code from coach"
          />
          <FormButton
            type="button"
            variant="primary"
            onClick={handleAcceptCode}
            isLoading={isLoading}
          >
            Connect
          </FormButton>
        </div>
        <p className="mt-2 text-sm text-gray-500">
          Enter the invitation code provided by your coach to establish a connection.
        </p>
      </div>
    </div>
  );
};

export default AthleteAcceptSection;