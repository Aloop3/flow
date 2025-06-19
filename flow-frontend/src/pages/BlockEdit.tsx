import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import BlockForm from '../components/BlockForm';
import { getBlock, updateBlock, deleteBlock } from '../services/api';
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
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteConfirmation, setShowDeleteConfirmation] = useState(false);
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

  const handleDeleteClick = () => {
    setShowDeleteConfirmation(true);
  };

  const handleDeleteConfirm = async () => {
    if (!blockId || !block) return;
    
    setIsDeleting(true);
    try {
      await deleteBlock(blockId);
      navigate('/blocks');
    } catch (error) {
      console.error('Error deleting block:', error);
      alert('Failed to delete training program. Please try again.');
    } finally {
      setIsDeleting(false);
      setShowDeleteConfirmation(false);
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteConfirmation(false);
  };

  return (
    <Layout user={user} signOut={signOut}>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">Edit Training Program</h1>
          
          {block && (
            <div className="relative">
              {showDeleteConfirmation ? (
                <div className="flex items-center space-x-2 bg-white rounded-md shadow-lg border p-3">
                  <span className="text-sm text-gray-700 whitespace-nowrap">Delete "{block.title}"?</span>
                  <button
                    onClick={handleDeleteConfirm}
                    disabled={isDeleting}
                    className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50"
                  >
                    {isDeleting ? 'Deleting...' : 'Yes'}
                  </button>
                  <button
                    onClick={handleDeleteCancel}
                    disabled={isDeleting}
                    className="px-3 py-1 text-sm bg-gray-300 text-gray-700 rounded hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50"
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <button
                  type="button"
                  onClick={handleDeleteClick}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  <svg className="-ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1-1H9a1 1 0 00-1 1v1M4 7h16" />
                  </svg>
                  Delete
                </button>
              )}
            </div>
          )}
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