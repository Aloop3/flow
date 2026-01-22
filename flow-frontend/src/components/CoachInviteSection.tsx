import { useState, useEffect } from 'react';
import { generateInvitationCode } from '../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

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
      console.log('Generating invitation code for user ID:', user.user_id);
      const response = await generateInvitationCode(user.user_id);

      console.log('Generated code response:', response);

      if (response && response.invitation_code) {
        setCode(response.invitation_code);

        // Convert expiry timestamp to readable date
        if (response.expires_at) {
          const expiryDate = new Date(response.expires_at * 1000);
          setExpiry(expiryDate.toLocaleString());
          console.log('Setting expiry to:', expiryDate.toLocaleString());
        }

        console.log('Code state updated to:', response.invitation_code);

        if (onGenerateCode) {
          onGenerateCode();
        }
      } else {
        console.error('Response missing invitation_code:', response);
        setError('Invalid response received. Please try again.');
      }
    } catch (err: any) {
      setError('Failed to generate invitation code. Please try again.');
      console.error('Error generating code:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Effect to log when code state changes
  useEffect(() => {
    console.log('Current code state:', code);
  }, [code]);

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="text-lg">Invite Athletes</CardTitle>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="mb-4 bg-red-50 text-red-700 p-3 rounded-md border border-red-200">
            {error}
          </div>
        )}

        {code ? (
          <div>
            <p className="mb-2">Share this invitation code with your athlete:</p>
            <div className="bg-muted p-3 rounded-md font-mono text-center text-lg mb-2">
              {code}
            </div>
            {expiry && (
              <p className="text-sm text-muted-foreground">
                This code will expire on {expiry}
              </p>
            )}

            <Button
              variant="outline"
              onClick={handleGenerateCode}
              disabled={isLoading}
              className="mt-4"
            >
              {isLoading ? 'Generating...' : 'Generate New Code'}
            </Button>
          </div>
        ) : (
          <div>
            <p className="mb-4">Generate an invitation code to connect with an athlete.</p>
            <Button onClick={handleGenerateCode} disabled={isLoading}>
              {isLoading ? 'Generating...' : 'Generate Invitation Code'}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default CoachInviteSection;
