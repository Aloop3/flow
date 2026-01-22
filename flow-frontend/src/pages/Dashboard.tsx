import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
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
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        
        {isLoading ? (
          <div className="space-y-4">
            <Skeleton className="h-40 w-full" />
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
          </div>
        ) : (
          <>
            {activeBlock ? (
              <Card>
                <CardContent className="pt-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">Current Program</h2>
                  <p className="text-lg font-medium text-gray-900">{activeBlock.title}</p>
                  <p className="text-muted-foreground mb-4">{activeBlock.description}</p>

                  <div className="sm:flex sm:items-center sm:justify-between">
                    <div className="mb-4 sm:mb-0">
                      <p className="text-sm text-muted-foreground">
                        {formatDate(activeBlock.start_date)} - {formatDate(activeBlock.end_date)}
                      </p>
                    </div>
                    <Button asChild className="w-full sm:w-auto">
                      <Link to={`/blocks/${activeBlock.block_id}`}>View Program</Link>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="pt-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">No Active Program</h2>
                  <p className="text-muted-foreground mb-4">You don't have an active training program.</p>
                  <Button asChild>
                    <Link to="/blocks/new">Create New Program</Link>
                  </Button>
                </CardContent>
              </Card>
            )}
            
            {/* Today's Workout Card - Insert this new section here */}
            <div className="mt-8">
              <TodaysWorkoutCard activeBlock={activeBlock} userId={user.user_id} />
            </div>
            
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
                    <Link key={block.block_id} to={`/blocks/${block.block_id}`}>
                      <Card className="hover:shadow-md transition-shadow">
                        <CardContent className="pt-4">
                          <h3 className="text-lg font-medium text-gray-900">{block.title}</h3>
                          <p className="mt-1 text-sm text-muted-foreground">{block.description}</p>
                          <p className="mt-2 text-xs text-muted-foreground">
                            {formatDate(block.start_date)} - {formatDate(block.end_date)}
                          </p>
                          <Badge className={`mt-2 ${
                            block.status === 'active'
                              ? 'bg-green-100 text-green-800 hover:bg-green-100'
                              : block.status === 'completed'
                              ? 'bg-blue-100 text-blue-800 hover:bg-blue-100'
                              : 'bg-gray-100 text-gray-800 hover:bg-gray-100'
                          }`}>
                            {block.status.charAt(0).toUpperCase() + block.status.slice(1)}
                          </Badge>
                        </CardContent>
                      </Card>
                    </Link>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No programs found. Create your first program.</p>
              )}
            </div>

            {/* Analytics Section */}
            <div className="mt-8">
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h2 className="text-xl font-semibold text-gray-900">Progress Analytics</h2>
                      <p className="text-sm text-muted-foreground">Track your strength gains and training insights</p>
                    </div>
                    <Button asChild>
                      <Link to="/analytics">View Analytics</Link>
                    </Button>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-muted rounded">
                      <p className="text-2xl font-bold text-blue-600">{blocks.length}</p>
                      <p className="text-sm text-muted-foreground">Total Programs</p>
                    </div>
                    <div className="text-center p-4 bg-muted rounded">
                      <p className="text-2xl font-bold text-green-600">
                        {blocks.filter(b => b.status === 'completed').length}
                      </p>
                      <p className="text-sm text-muted-foreground">Completed</p>
                    </div>
                    <div className="text-center p-4 bg-muted rounded">
                      <p className="text-2xl font-bold text-orange-600">
                        {blocks.filter(b => b.status === 'active').length}
                      </p>
                      <p className="text-sm text-muted-foreground">Active</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {user.role === 'coach' && (
                <div className="mt-8">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold text-gray-900">My Athletes</h2>
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
                              <h3 className="text-lg font-medium text-gray-900">{athlete.name}</h3>
                              <p className="mt-2 text-sm">
                                {athlete.activeProgram ? (
                                  <span className="text-green-600">Active: {athlete.activeProgram}</span>
                                ) : (
                                  <span className="text-muted-foreground">No active program</span>
                                )}
                              </p>
                            </CardContent>
                          </Card>
                        </Link>
                      ))}
                    </div>
                  ) : (
                    <Card className="text-center">
                      <CardContent className="pt-6">
                        <p className="text-muted-foreground">No athletes yet. Athletes must accept your invitation first.</p>
                      </CardContent>
                    </Card>
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