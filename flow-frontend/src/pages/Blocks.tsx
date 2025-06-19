import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import Layout from '../components/Layout';
import { getBlocks } from '../services/api';
import type { Block } from '../services/api';
import { formatDate } from '../utils/dateUtils';

interface BlocksProps {
  user: any;
  signOut: () => void;
}

const Blocks = ({ user, signOut }: BlocksProps) => {
  const [blocks, setBlocks] = useState<Block[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const location = useLocation();

  const fetchBlocks = async () => {
    setIsLoading(true);
    try {
      const blocksData = await getBlocks(user.user_id);
      console.log('Blocks data:', blocksData);
      setBlocks(blocksData);
    } catch (error) {
      console.error('Error fetching blocks:', error);
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
  }, [location.pathname]);

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
              <Link
                key={block.block_id}
                to={`/blocks/${block.block_id}`}
                className="bg-white shadow rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <h3 className="text-lg font-medium text-gray-900">{block.title}</h3>
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