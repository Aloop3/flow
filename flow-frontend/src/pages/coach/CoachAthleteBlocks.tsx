import { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import Layout from '../../components/Layout';
import { getBlocks, getUser } from '../../services/api';
import type { Block, User } from '../../services/api';
import { formatDate } from '../../utils/dateUtils';

interface CoachAthleteBlocksProps {
  user: any;
  signOut: () => void;
}

const CoachAthleteBlocks = ({ user, signOut }: CoachAthleteBlocksProps) => {
  const { athleteId } = useParams<{ athleteId: string }>();
  const [blocks, setBlocks] = useState<Block[]>([]);
  const [athlete, setAthlete] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      if (!athleteId) return;
      
      setIsLoading(true);
      try {
        // Fetch athlete info
        const athleteData = await getUser(athleteId);
        setAthlete(athleteData);
        
        // Fetch athlete's blocks
        const blocksData = await getBlocks(athleteId);
        setBlocks(blocksData);
      } catch (error) {
        console.error('Error fetching athlete data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [athleteId]);

  return (
    <Layout user={user} signOut={signOut}>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <Link 
              to="/dashboard" 
              className="text-sm text-blue-600 hover:text-blue-800 mb-2 inline-block"
            >
              ← Back to Dashboard
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">
              {athlete ? `${athlete.name}'s Training Programs` : 'Training Programs'}
            </h1>
          </div>
          <Link
            to={`/coach/athletes/${athleteId}/blocks/new`}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
          >
            Create New Program
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
                  {block.coach_id === user.user_id && (
                    <span className="ml-2 text-xs text-gray-500">
                      (Created by you)
                    </span>
                  )}
                </Link>
              ))
            ) : (
              <div className="col-span-3 bg-white p-6 text-center rounded-lg shadow">
                <p className="text-gray-500">No training programs found. Create the first program for {athlete?.name}.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default CoachAthleteBlocks;