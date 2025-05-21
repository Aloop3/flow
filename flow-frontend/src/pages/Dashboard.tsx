import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import { getBlocks, getCoachRelationships, getUser } from '../services/api';
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
  const [athletes, setAthletes] = useState<any[]>([]);
  const [isLoadingAthletes, setIsLoadingAthletes] = useState(false);

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
  
  useEffect(() => {
    const fetchAthletes = async () => {
      if (user.role !== 'coach') return;
      
      setIsLoadingAthletes(true);
      try {
        const relationships = await getCoachRelationships(user.user_id, 'active');
        
        // Extract athlete IDs from relationships
        const athletesList = await Promise.all(
          relationships.map(async (rel) => {
            try {
              // Fetch full athlete details using their ID
              const athlete = await getUser(rel.athlete_id);
              return {
                athlete_id: rel.athlete_id,
                name: athlete?.name || 'Unknown Athlete',
                relationship_id: rel.relationship_id
              };
            } catch (error) {
              console.error(`Error fetching athlete ${rel.athlete_id}:`, error);
              return {
                athlete_id: rel.athlete_id,
                name: 'Unknown Athlete',
                relationship_id: rel.relationship_id
              };
            }
          })
        );
        
        // For each athlete, fetch their active program
        const athletesWithPrograms = await Promise.all(
          athletesList.map(async (athlete) => {
            try {
              const blocks = await getBlocks(athlete.athlete_id);
              const activeBlock = blocks.find(block => block.status === 'active');
              return {
                ...athlete,
                activeProgram: activeBlock?.title || null
              };
            } catch (error) {
              console.error(`Error fetching blocks for athlete ${athlete.athlete_id}:`, error);
              return {
                ...athlete,
                activeProgram: null
              };
            }
          })
        );
        
        setAthletes(athletesWithPrograms);
      } catch (error) {
        console.error('Error fetching athletes:', error);
        setAthletes([]);
      } finally {
        setIsLoadingAthletes(false);
      }
    };
  
    fetchAthletes();
  }, [user.role, user.user_id]);
  

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
            {user.role === 'coach' && (
                <div className="mt-8">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold text-gray-900">My Athletes</h2>
                  </div>
                  
                  {isLoadingAthletes ? (
                    <div className="animate-pulse space-y-4">
                      <div className="h-20 bg-gray-200 rounded-lg"></div>
                      <div className="h-20 bg-gray-200 rounded-lg"></div>
                    </div>
                  ) : athletes.length > 0 ? (
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                      {athletes.map((athlete) => (
                        <Link
                          key={athlete.athlete_id}
                          to={`/coach/athletes/${athlete.athlete_id}/blocks`}
                          className="bg-white shadow rounded-lg p-4 hover:shadow-md transition-shadow"
                        >
                          <h3 className="text-lg font-medium text-gray-900">{athlete.name}</h3>
                          <p className="mt-2 text-sm">
                            {athlete.activeProgram ? (
                              <span className="text-green-600">Active: {athlete.activeProgram}</span>
                            ) : (
                              <span className="text-gray-400">No active program</span>
                            )}
                          </p>
                        </Link>
                      ))}
                    </div>
                  ) : (
                    <div className="bg-white shadow rounded-lg p-6 text-center">
                      <p className="text-gray-500">No athletes yet. Athletes must accept your invitation first.</p>
                    </div>
                  )}
                </div>
              )}
          </>
        )}
      </div>
    </Layout>
  );
};

export default Dashboard;