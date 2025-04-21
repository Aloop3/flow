import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import { getBlocks } from '../services/api';
import type { Block } from '../services/api';
import { formatDate } from '../utils/dateUtils';

interface DashboardProps {
  user: any;
  signOut: () => void;
}

const Dashboard = ({ user, signOut }: DashboardProps) => {
  const [blocks, setBlocks] = useState<Block[]>([]);
  const [activeBlock, setActiveBlock] = useState<Block | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const blocksData = await getBlocks(user.user_id);
        setBlocks(blocksData || []); // fallback here
  
        const active = (blocksData || []).find(block => block.status === 'active');
        setActiveBlock(active || null);
      } catch (error) {
        console.error('Error fetching blocks:', error);
        setBlocks([]);
        setActiveBlock(null);
      } finally {
        setIsLoading(false);
      }
    };
  
    fetchData();
  }, [user.user_id]);
  

  return (
    <Layout user={user} signOut={signOut}>
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        
        {isLoading ? (
          <div className="animate-pulse space-y-4">
            <div className="h-40 bg-gray-200 rounded-lg"></div>
            <div className="h-20 bg-gray-200 rounded-lg"></div>
            <div className="h-20 bg-gray-200 rounded-lg"></div>
          </div>
        ) : (
          <>
            {activeBlock ? (
              <div className="bg-white shadow rounded-lg overflow-hidden">
                <div className="p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">Current Program</h2>
                  <p className="text-lg font-medium text-gray-900">{activeBlock.title}</p>
                  <p className="text-gray-500 mb-4">{activeBlock.description}</p>
                  
                  <div className="sm:flex sm:items-center sm:justify-between">
                    <div className="mb-4 sm:mb-0">
                      <p className="text-sm text-gray-500">
                        {formatDate(activeBlock.start_date)} - {formatDate(activeBlock.end_date)}
                      </p>
                    </div>
                    <Link
                      to={`/blocks/${activeBlock.block_id}`}
                      className="w-full sm:w-auto inline-flex items-center justify-center px-5 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                    >
                      View Program
                    </Link>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white shadow rounded-lg">
                <div className="p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">No Active Program</h2>
                  <p className="text-gray-500 mb-4">You don't have an active training program.</p>
                  <Link
                    to="/blocks/new"
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
                  >
                    Create New Program
                  </Link>
                </div>
              </div>
            )}
            
            <div className="mt-8">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">Your Programs</h2>
                <Link
                  to="/blocks"
                  className="text-sm font-medium text-blue-600 hover:text-blue-500"
                >
                  View all
                </Link>
              </div>
              
              {blocks.length > 0 ? (
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {blocks.slice(0, 3).map((block) => (
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
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No programs found. Create your first program.</p>
              )}
            </div>
          </>
        )}
      </div>
    </Layout>
  );
};

export default Dashboard;