import { Link } from 'react-router-dom';
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
    draft: 'bg-gray-100 text-gray-800',
    active: 'bg-green-100 text-green-800',
    completed: 'bg-blue-100 text-blue-800'
  };

  return (
    <Link to={`/blocks/${block.block_id}`} className="block">
      <div className="bg-white rounded-lg shadow-md p-5 hover:shadow-lg transition-shadow">
        <div className="flex justify-between items-start mb-2">
          <h3 className="font-bold text-lg">{block.title}</h3>
          <span className={`text-xs px-2 py-1 rounded-full ${statusColors[block.status]}`}>
            {block.status.charAt(0).toUpperCase() + block.status.slice(1)}
          </span>
        </div>
        
        <p className="text-gray-600 text-sm mb-4">{block.description}</p>
        
        <div className="mb-2">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
        
        <div className="flex justify-between text-xs text-gray-500">
          <span>{formatDate(block.start_date)}</span>
          <span>{formatDate(block.start_date)}</span>
        </div>
      </div>
    </Link>
  );
}