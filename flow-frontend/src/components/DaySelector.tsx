import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { getWeeks, getDays } from '../services/api';
import type { Week, Day } from '../services/api';
import { formatDate } from '../utils/dateUtils';

interface DaySelectorProps {
  isOpen: boolean;
  onClose: () => void;
  onDaySelected: (dayId: string) => void;
  blockId: string;
  title?: string;
  excludeDayId?: string; // Optional day to exclude from selection
}

const DaySelector = ({ 
  isOpen, 
  onClose, 
  onDaySelected, 
  blockId,
  title = 'Select a Day',
  excludeDayId
}: DaySelectorProps) => {
  const [weeks, setWeeks] = useState<Week[]>([]);
  const [days, setDays] = useState<Record<string, Day[]>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [activeWeek, setActiveWeek] = useState<string | null>(null);
  
  useEffect(() => {
    if (!isOpen || !blockId) return;
    
    const fetchBlockData = async () => {
      setIsLoading(true);
      try {
        const weeksData = await getWeeks(blockId);
        const sortedWeeks = Array.isArray(weeksData)
          ? [...weeksData].sort((a, b) => a.week_number - b.week_number)
          : [];
        
        setWeeks(sortedWeeks);
        
        if (sortedWeeks.length > 0) {
          setActiveWeek(sortedWeeks[0].week_id);
          
          // Fetch days for all weeks in parallel (mobile-friendly)
          const daysPromises = sortedWeeks.map(async (week) => {
            try {
              const daysData = await getDays(week.week_id);
              return { week_id: week.week_id, data: daysData };
            } catch (error) {
              console.error(`Error fetching days for week ${week.week_id}:`, error);
              return { week_id: week.week_id, data: [] };
            }
          });
          
          const daysResults = await Promise.all(daysPromises);
          const daysObj: Record<string, Day[]> = {};
          daysResults.forEach(result => {
            daysObj[result.week_id] = result.data;
          });
          setDays(daysObj);
        }
      } catch (error) {
        console.error('Error fetching block data:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchBlockData();
  }, [isOpen, blockId]);
  
  const handleDayClick = (dayId: string) => {
    onDaySelected(dayId);
    onClose();
  };
  
  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>
        {isLoading ? (
          <div className="space-y-4">
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-32 w-full" />
          </div>
        ) : (
          <div className="space-y-4">
            {/* Week tabs */}
            {weeks.length > 0 && (
              <>
                <div className="flex overflow-x-auto pb-2 border-b">
                  {weeks.map(week => (
                    <button
                      key={week.week_id}
                      onClick={() => setActiveWeek(week.week_id)}
                      className={`px-4 py-2 text-sm whitespace-nowrap ${
                        activeWeek === week.week_id
                          ? 'border-b-2 border-blue-500 text-blue-600 font-medium'
                          : 'text-gray-500 hover:text-gray-700'
                      }`}
                    >
                      Week {week.week_number}
                    </button>
                  ))}
                </div>

                {/* Days grid */}
                {activeWeek && days[activeWeek] && (
                  <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
                    {days[activeWeek]
                      .filter(day => day.day_id !== excludeDayId)
                      .sort((a, b) => a.day_number - b.day_number)
                      .map(day => (
                        <button
                          key={day.day_id}
                          onClick={() => handleDayClick(day.day_id)}
                          className="border rounded-md p-3 text-left hover:bg-gray-50"
                        >
                          <p className="font-medium">Day {day.day_number}</p>
                          <p className="text-sm text-muted-foreground">
                            {formatDate(day.date, { weekday: 'short', month: 'short', day: 'numeric' })}
                          </p>
                          {day.focus && (
                            <Badge variant="secondary" className="mt-1">
                              {day.focus}
                            </Badge>
                          )}
                        </button>
                      ))
                    }
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default DaySelector;