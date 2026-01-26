import { useState, useEffect, useMemo } from 'react';
import { Link, useLocation } from 'react-router-dom';
import Layout from '../components/Layout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { getBlocks, deleteBlock } from '../services/api';
import type { Block } from '../services/api';
import { formatDate } from '../utils/dateUtils';

type SortOption = 'name-asc' | 'name-desc' | 'date-newest' | 'date-oldest';

interface BlocksProps {
  user: any;
  signOut: () => void;
}

const Blocks = ({ user, signOut }: BlocksProps) => {
  const [blocks, setBlocks] = useState<Block[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [deletingBlockId, setDeletingBlockId] = useState<string | null>(null);
  const [confirmingDeleteId, setConfirmingDeleteId] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<SortOption>('date-newest');
  const location = useLocation();

  // Sort blocks based on selected option
  const sortedBlocks = useMemo(() => {
    if (!blocks || blocks.length === 0) return [];

    return [...blocks].sort((a, b) => {
      switch (sortBy) {
        case 'name-asc':
          return a.title.localeCompare(b.title);
        case 'name-desc':
          return b.title.localeCompare(a.title);
        case 'date-newest':
          return new Date(b.start_date).getTime() - new Date(a.start_date).getTime();
        case 'date-oldest':
          return new Date(a.start_date).getTime() - new Date(b.start_date).getTime();
        default:
          return 0;
      }
    });
  }, [blocks, sortBy]);

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
  // Extract refresh timestamp to use as primitive dependency
  const refreshTrigger = (location.state as { refresh?: number } | null)?.refresh;

  useEffect(() => {
    // Skip on initial mount (handled by user useEffect above)
    if (!refreshTrigger) return;

    console.log('🔄 Refresh triggered from navigation state');
    fetchBlocks();
  }, [refreshTrigger]);

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
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <h1 className="text-2xl font-bold text-gray-900">Training Programs</h1>
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <Select value={sortBy} onValueChange={(value: SortOption) => setSortBy(value)}>
              <SelectTrigger className="w-[160px]">
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="date-newest">Newest First</SelectItem>
                <SelectItem value="date-oldest">Oldest First</SelectItem>
                <SelectItem value="name-asc">Name A-Z</SelectItem>
                <SelectItem value="name-desc">Name Z-A</SelectItem>
              </SelectContent>
            </Select>
            <Button asChild>
              <Link to="/blocks/new">Create New</Link>
            </Button>
          </div>
        </div>

        {isLoading ? (
          <div className="space-y-4">
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {sortedBlocks.length > 0 ? (
              sortedBlocks.map((block) => (
                <div key={block.block_id} className="relative group">
                  <Link to={`/blocks/${block.block_id}`}>
                    <Card className="hover:shadow-md transition-shadow">
                      <CardContent className="pt-4">
                        <h3 className="text-lg font-medium text-gray-900 pr-8">{block.title}</h3>
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

                  {/* Delete confirmation or button */}
                  <div className="absolute top-4 right-4">
                    {confirmingDeleteId === block.block_id ? (
                      <div className="flex items-center space-x-1 bg-white rounded-md shadow-lg border p-2">
                        <span className="text-xs text-muted-foreground whitespace-nowrap">Delete?</span>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => handleDeleteConfirm(block)}
                          className="h-6 px-2 text-xs"
                        >
                          Yes
                        </Button>
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={handleDeleteCancel}
                          className="h-6 px-2 text-xs"
                        >
                          No
                        </Button>
                      </div>
                    ) : (
                      <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button
                          size="icon"
                          variant="ghost"
                          onClick={(e) => handleDeleteClick(e, block)}
                          disabled={deletingBlockId === block.block_id}
                          className="h-8 w-8 text-gray-400 hover:text-red-600"
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
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              ))
          ) : (
            <Card className="col-span-3 text-center">
              <CardContent className="pt-6">
                <p className="text-muted-foreground">No training programs found. Create your first program to get started.</p>
              </CardContent>
            </Card>
          )}
        </div>
      )}
      </div>
    </Layout>
  );
};

export default Blocks;