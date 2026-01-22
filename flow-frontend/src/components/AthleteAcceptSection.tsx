import { useState } from 'react';
import { acceptInvitationCode } from '../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

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
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="text-lg">Connect with a Coach</CardTitle>
      </CardHeader>
      <CardContent>
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
            <Input
              type="text"
              id="inviteCode"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="Enter code from coach"
              className="flex-1"
            />
            <Button onClick={handleAcceptCode} disabled={isLoading}>
              {isLoading ? 'Connecting...' : 'Connect'}
            </Button>
          </div>
          <p className="mt-2 text-sm text-muted-foreground">
            Enter the invitation code provided by your coach to establish a connection.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default AthleteAcceptSection;
