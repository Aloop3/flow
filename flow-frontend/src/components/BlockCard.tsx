import { Link } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { formatDate } from '../utils/dateUtils';

interface BlockCardProps {
  block: {
    block_id: string;
    title: string;
    description: string;
    start_date: string;
    end_date: string;
    status: 'draft' | 'active' | 'completed';
  }
}

export default function BlockCard({ block }: BlockCardProps) {
  // Calculate progress percentage based on dates
  const startDate = new Date(block.start_date);
  const endDate = new Date(block.end_date);
  const today = new Date();
  const totalDays = (endDate.getTime() - startDate.getTime()) / (1000 * 3600 * 24);
  const daysElapsed = (today.getTime() - startDate.getTime()) / (1000 * 3600 * 24);
  const progress = Math.max(0, Math.min(100, (daysElapsed / totalDays) * 100));

  // Status badge color
  const statusColors = {
    draft: 'bg-gray-100 text-gray-800 hover:bg-gray-100',
    active: 'bg-green-100 text-green-800 hover:bg-green-100',
    completed: 'bg-blue-100 text-blue-800 hover:bg-blue-100'
  };

  return (
    <Link to={`/blocks/${block.block_id}`} className="block">
      <Card className="hover:shadow-lg transition-shadow">
        <CardContent className="pt-5">
          <div className="flex justify-between items-start mb-2">
            <h3 className="font-bold text-lg">{block.title}</h3>
            <Badge className={statusColors[block.status]}>
              {block.status.charAt(0).toUpperCase() + block.status.slice(1)}
            </Badge>
          </div>

          <p className="text-muted-foreground text-sm mb-4">{block.description}</p>

          <div className="mb-2">
            <Progress value={progress} className="h-2" />
          </div>

          <div className="flex justify-between text-xs text-muted-foreground">
            <span>{formatDate(block.start_date)}</span>
            <span>{formatDate(block.end_date)}</span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}