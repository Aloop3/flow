import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import BlockForm from '../components/BlockForm';
import { getBlock, updateBlock } from '../services/api';
import type { Block } from '../services/api';

interface BlockEditProps {
  user: any;
  signOut: () => void;
}

const BlockEdit = ({ user, signOut }: BlockEditProps) => {
  const { blockId } = useParams<{ blockId: string }>();
  const [block, setBlock] = useState<Block | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchBlock = async () => {
      if (!blockId) return;
      
      setIsLoading(true);
      try {
        const blockData = await getBlock(blockId);
        setBlock(blockData);
      } catch (error) {
        console.error('Error fetching block:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchBlock();
  }, [blockId]);

  const handleUpdateBlock = async (blockData: Partial<Block>) => {
    if (!blockId) return;
    
    setIsSaving(true);
    try {
      await updateBlock(blockId, blockData);
      navigate(`/blocks/${blockId}`);
    } catch (error) {
      console.error('Error updating block:', error);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Layout user={user} signOut={signOut}>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">Edit Training Program</h1>
        </div>
        
        {isLoading ? (
          <div className="animate-pulse space-y-4">
            <div className="h-10 bg-gray-200 rounded w-1/4"></div>
            <div className="h-40 bg-gray-200 rounded"></div>
          </div>
        ) : block ? (
          <div className="bg-white shadow rounded-lg p-6">
            <BlockForm 
              initialData={block} 
              onSubmit={handleUpdateBlock} 
              isLoading={isSaving} 
            />
          </div>
        ) : (
          <div className="bg-white shadow rounded-lg p-6 text-center">
            <p className="text-gray-500">Block not found.</p>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default BlockEdit;