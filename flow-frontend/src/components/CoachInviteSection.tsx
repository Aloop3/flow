import { useState } from 'react';
import { generateInvitationCode } from '../services/api';
import FormButton from './FormButton';

interface CoachInviteSectionProps {
  user: any;
  onGenerateCode: () => void;
}

const CoachInviteSection = ({ user, onGenerateCode }: CoachInviteSectionProps) => {
  const [code, setCode] = useState<string | null>(null);
  const [expiry, setExpiry] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerateCode = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await generateInvitationCode(user.coach_id);
      setCode(response.invitation_code);
      
      // Convert expiry timestamp to readable date
      const expiryDate = new Date(response.expires_at * 1000);
      setExpiry(expiryDate.toLocaleString());
      
      if (onGenerateCode) {
        onGenerateCode();
      }
    } catch (err: any) {
      setError('Failed to generate invitation code. Please try again.');
      console.error('Error generating code:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white shadow rounded-lg p-6 mb-6">
      <h2 className="text-lg font-medium mb-4">Invite Athletes</h2>
      
      {error && (
        <div className="mb-4 bg-red-50 text-red-700 p-3 rounded-md border border-red-200">
          {error}
        </div>
      )}
      
      {code ? (
        <div>
          <p className="mb-2">Share this invitation code with your athlete:</p>
          <div className="bg-gray-100 p-3 rounded-md font-mono text-center text-lg mb-2">
            {code}
          </div>
          <p className="text-sm text-gray-500">
            This code will expire on {expiry}
          </p>
          
          <FormButton 
            type="button"
            variant="secondary"
            onClick={handleGenerateCode}
            className="mt-4"
            isLoading={isLoading}
          >
            Generate New Code
          </FormButton>
        </div>
      ) : (
        <div>
          <p className="mb-4">Generate an invitation code to connect with an athlete.</p>
          <FormButton
            type="button"
            variant="primary"
            onClick={handleGenerateCode}
            isLoading={isLoading}
          >
            Generate Invitation Code
          </FormButton>
        </div>
      )}
    </div>
  );
};

export default CoachInviteSection;