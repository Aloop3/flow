import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import BlockForm from '../components/BlockForm';
import { createBlock } from '../services/api';

interface BlockCreateProps {
  user: any;
  signOut: () => void;
}

const BlockCreate = ({ user, signOut }: BlockCreateProps) => {
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  const handleCreateBlock = async (blockData: any) => {
    setIsLoading(true);
    setError(null);

    try {
      // Add athlete_id from current user
      const fullBlockData = {
        ...blockData,
        athlete_id: user.user_id,
        // Ensure description is not undefined
        description: blockData.description || ''
      };
      
      await createBlock(fullBlockData);
      navigate('/blocks');
    } catch (error) {
      console.error('Error creating block:', error);
      setError('Failed to create training program. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Layout user={user} signOut={signOut}>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">Create Training Program</h1>
        </div>
        
        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}
        
        <div className="bg-white shadow rounded-lg p-6">
          <BlockForm onSubmit={handleCreateBlock} isLoading={isLoading} />
        </div>
      </div>
    </Layout>

  );
};

export default BlockCreate;