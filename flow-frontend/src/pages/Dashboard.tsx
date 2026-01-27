import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { getBlocks, getCoachRelationships, getUser } from '../services/api';
import type { Block } from '../services/api';
import { formatDate } from '../utils/dateUtils';
import TodaysWorkoutCard from '../components/TodaysWorkoutCard';

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
        <h1 className="text-2xl font-bold text-ocean-navy-dark">Dashboard</h1>
        
        {isLoading ? (
          <div className="space-y-4">
            <Skeleton className="h-40 w-full" />
            <Skeleton className="h-20 w-full" />
          </div>
        ) : (
          <>
            {/* Today's Workout - PRIMARY FOCUS */}
            <TodaysWorkoutCard activeBlock={activeBlock} userId={user.user_id} />

            {/* Current Program - demoted to context line */}
            {activeBlock && (
              <div className="flex items-center justify-between py-3 px-4 bg-ocean-mist rounded-lg">
                <div className="flex items-center gap-3">
                  <Badge className="bg-state-active/10 text-state-active">Active</Badge>
                  <Link
                    to={`/blocks/${activeBlock.block_id}`}
                    className="font-medium text-ocean-navy hover:text-ocean-teal transition-colors"
                  >
                    {activeBlock.title}
                  </Link>
                  <span className="text-sm text-ocean-slate hidden sm:inline">
                    {formatDate(activeBlock.start_date)} - {formatDate(activeBlock.end_date)}
                  </span>
                </div>
                <Link
                  to={`/blocks/${activeBlock.block_id}`}
                  className="text-sm text-ocean-teal hover:text-ocean-navy"
                >
                  View →
                </Link>
              </div>
            )}
            
            <div className="mt-8">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-ocean-navy-dark">Your Programs</h2>
                <Link
                  to="/blocks"
                  className="text-sm font-medium text-ocean-teal hover:text-ocean-navy"
                >
                  View all
                </Link>
              </div>
              
              {blocks.length > 0 ? (
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {blocks.slice(0, 3).map((block) => (
                    <Link key={block.block_id} to={`/blocks/${block.block_id}`}>
                      <Card className="hover:shadow-md transition-shadow">
                        <CardContent className="pt-4">
                          <h3 className="text-lg font-medium text-ocean-navy">{block.title}</h3>
                          <p className="mt-1 text-sm text-ocean-slate">{block.description}</p>
                          <p className="mt-2 text-xs text-ocean-slate-light">
                            {formatDate(block.start_date)} - {formatDate(block.end_date)}
                          </p>
                          <Badge className={`mt-2 ${
                            block.status === 'active'
                              ? 'bg-state-active/10 text-state-active hover:bg-state-active/10'
                              : block.status === 'completed'
                              ? 'bg-state-completed/10 text-state-completed hover:bg-state-completed/10'
                              : 'bg-ocean-mist text-ocean-slate hover:bg-ocean-mist'
                          }`}>
                            {block.status.charAt(0).toUpperCase() + block.status.slice(1)}
                          </Badge>
                        </CardContent>
                      </Card>
                    </Link>
                  ))}
                </div>
              ) : (
                <p className="text-ocean-slate py-2">Ready to start training? Create your first program.</p>
              )}
            </div>

            {/* Analytics - simplified link */}
            <div className="mt-8 flex items-center justify-between py-3 px-4 bg-ocean-mist/50 rounded-lg">
              <span className="text-ocean-slate">Track your strength gains and training insights</span>
              <Link
                to="/analytics"
                className="text-sm font-medium text-ocean-teal hover:text-ocean-navy"
              >
                View Analytics →
              </Link>
            </div>

            {user.role === 'coach' && (
                <div className="mt-8">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold text-ocean-navy-dark">My Athletes</h2>
                  </div>

                  {isLoadingAthletes ? (
                    <div className="space-y-4">
                      <Skeleton className="h-20 w-full" />
                      <Skeleton className="h-20 w-full" />
                    </div>
                  ) : athletes.length > 0 ? (
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                      {athletes.map((athlete) => (
                        <Link key={athlete.athlete_id} to={`/coach/athletes/${athlete.athlete_id}/blocks`}>
                          <Card className="hover:shadow-md transition-shadow">
                            <CardContent className="pt-4">
                              <h3 className="text-lg font-medium text-ocean-navy">{athlete.name}</h3>
                              <p className="mt-2 text-sm">
                                {athlete.activeProgram ? (
                                  <span className="text-state-active">Active: {athlete.activeProgram}</span>
                                ) : (
                                  <span className="text-ocean-slate">No active program</span>
                                )}
                              </p>
                            </CardContent>
                          </Card>
                        </Link>
                      ))}
                    </div>
                  ) : (
                    <p className="text-ocean-slate py-4">Your athletes will appear here once they accept your invitation.</p>
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