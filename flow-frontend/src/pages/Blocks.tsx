import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import Layout from '../components/Layout';
import { getBlocks, deleteBlock } from '../services/api';
import type { Block } from '../services/api';
import { formatDate } from '../utils/dateUtils';

interface BlocksProps {
  user: any;
  signOut: () => void;
}

const Blocks = ({ user, signOut }: BlocksProps) => {
  const [blocks, setBlocks] = useState<Block[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [deletingBlockId, setDeletingBlockId] = useState<string | null>(null);
  const [confirmingDeleteId, setConfirmingDeleteId] = useState<string | null>(null);
  const location = useLocation();

  const fetchBlocks = async () => {
    setIsLoading(true);
    try {
      const blocksData = await getBlocks(user.user_id);
      console.log('Blocks data received:', blocksData);
      
      // Defensive check
      if (Array.isArray(blocksData)) {
        setBlocks(blocksData);
      } else {
        console.error('Invalid blocks data format:', blocksData);
        setBlocks([]);
      }
    } catch (error) {
      console.error('Error fetching blocks:', error);
      setBlocks([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    console.log('User object in Blocks', user);
    fetchBlocks();
  }, [user]);

  // Refetch on navigation back to /blocks (handles create -> list navigation)
  useEffect(() => {
    // Only refetch if we're on the exact /blocks route
    if (location.pathname === '/blocks') {
      console.log('🔄 Navigation detected - refreshing blocks list');
      fetchBlocks();
    }
  }, [location.pathname, location.key]);

  const handleDeleteClick = (e: React.MouseEvent, block: Block) => {
    e.preventDefault(); // Prevent navigation to block detail
    e.stopPropagation();
    setConfirmingDeleteId(block.block_id);
  };

  const handleDeleteConfirm = async (block: Block) => {
    setConfirmingDeleteId(null);
    setDeletingBlockId(block.block_id);
    try {
      await deleteBlock(block.block_id);
      // Update local state immediately for instant UI feedback
      setBlocks(prevBlocks => prevBlocks.filter(b => b.block_id !== block.block_id));
    } catch (error) {
      console.error('Error deleting block:', error);
      alert('Failed to delete training program. Please try again.');
      // Refresh to restore state if delete failed
      fetchBlocks();
    } finally {
      setDeletingBlockId(null);
    }
  };

  const handleDeleteCancel = () => {
    setConfirmingDeleteId(null);
  };

  return (
    <Layout user={user} signOut={signOut}>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Training Programs</h1>
          <Link
            to="/blocks/new"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
          >
            Create New
          </Link>
        </div>

        {isLoading ? (
          <div className="animate-pulse space-y-4">
            <div className="h-20 bg-gray-200 rounded-lg"></div>
            <div className="h-20 bg-gray-200 rounded-lg"></div>
            <div className="h-20 bg-gray-200 rounded-lg"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {blocks && blocks.length > 0 ? (
              blocks.map((block) => (
                <div key={block.block_id} className="relative group">
                  <Link
                    to={`/blocks/${block.block_id}`}
                    className="block bg-white shadow rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <h3 className="text-lg font-medium text-gray-900 pr-8">{block.title}</h3>
                    <p className="mt-1 text-sm text-gray-500">{block.description}</p>
                    <p className="mt-2 text-xs text-gray-500">
                      {formatDate(block.start_date)} - {formatDate(block.end_date)}
                    </p>
                    <span className={`mt-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      block.status === 'active' 
                        ? 'bg-green-100 text-green-800' 
                        : block.status === 'completed'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-gray-100 text-gray-800'
                      }`}>
                      {block.status.charAt(0).toUpperCase() + block.status.slice(1)}
                    </span>
                  </Link>
                  
                  {/* Delete confirmation or button */}
                  <div className="absolute top-4 right-4">
                    {confirmingDeleteId === block.block_id ? (
                      <div className="flex items-center space-x-1 bg-white rounded-md shadow-lg border p-2">
                        <span className="text-xs text-gray-600 whitespace-nowrap">Delete?</span>
                        <button
                          onClick={() => handleDeleteConfirm(block)}
                          className="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700 focus:outline-none focus:ring-1 focus:ring-red-500"
                        >
                          Yes
                        </button>
                        <button
                          onClick={handleDeleteCancel}
                          className="px-2 py-1 text-xs bg-gray-300 text-gray-700 rounded hover:bg-gray-400 focus:outline-none focus:ring-1 focus:ring-gray-500"
                        >
                          No
                        </button>
                      </div>
                    ) : (
                      <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={(e) => handleDeleteClick(e, block)}
                          disabled={deletingBlockId === block.block_id}
                          className="p-1 text-gray-400 hover:text-red-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                          title="Delete training program"
                        >
                          {deletingBlockId === block.block_id ? (
                            <svg className="animate-spin h-4 w-4 text-red-600" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                          ) : (
                            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1-1H9a1 1 0 00-1 1v1M4 7h16" />
                            </svg>
                          )}
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))
          ) : (
            <div className="col-span-3 bg-white p-6 text-center rounded-lg shadow">
              <p className="text-gray-500">No training programs found. Create your first program to get started.</p>
            </div>
          )}
        </div>
      )}
      </div>
    </Layout>
  );
};

export default Blocks;