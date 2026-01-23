import { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import Layout from '../../components/Layout';
import { getBlocks, getUser } from '../../services/api';
import type { Block, User } from '../../services/api';
import { formatDate } from '../../utils/dateUtils';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';

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
          <Button asChild>
            <Link to={`/coach/athletes/${athleteId}/blocks/new`}>
              Create New Program
            </Link>
          </Button>
        </div>

        {isLoading ? (
          <div className="space-y-4">
            <Skeleton className="h-20" />
            <Skeleton className="h-20" />
            <Skeleton className="h-20" />
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {blocks && blocks.length > 0 ? (
              blocks.map((block) => (
                <Link key={block.block_id} to={`/blocks/${block.block_id}`}>
                  <Card className="hover:shadow-md transition-shadow">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-lg">{block.title}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-500">{block.description}</p>
                      <p className="mt-2 text-xs text-gray-500">
                        {formatDate(block.start_date)} - {formatDate(block.end_date)}
                      </p>
                      <div className="mt-2">
                        <Badge variant={
                          block.status === 'active' ? 'default' :
                          block.status === 'completed' ? 'secondary' : 'outline'
                        }>
                          {block.status.charAt(0).toUpperCase() + block.status.slice(1)}
                        </Badge>
                        {block.coach_id === user.user_id && (
                          <span className="ml-2 text-xs text-gray-500">
                            (Created by you)
                          </span>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))
            ) : (
              <Card className="col-span-3">
                <CardContent className="p-6 text-center">
                  <p className="text-gray-500">No training programs found. Create the first program for {athlete?.name}.</p>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default CoachAthleteBlocks;