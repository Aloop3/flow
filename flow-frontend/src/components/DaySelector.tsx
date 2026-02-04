import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Skeleton } from '@/components/ui/skeleton';
import { getWeeks, getDays } from '../services/api';
import type { Week, Day } from '../services/api';
import { formatDate } from '../utils/dateUtils';
import FocusTag from './FocusTag';
import { parseFocusTags } from '../constants/focusOptions';

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
      <DialogContent className="max-w-lg max-h-[85vh] flex flex-col">
        <DialogHeader className="flex-shrink-0">
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>
        {isLoading ? (
          <div className="space-y-4">
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-32 w-full" />
          </div>
        ) : (
          <div className="flex flex-col min-h-0 flex-1">
            {/* Week tabs - sticky at top */}
            {weeks.length > 0 && (
              <>
                <div className="flex overflow-x-auto pb-2 border-b flex-shrink-0 -mx-1 px-1">
                  {weeks.map(week => (
                    <button
                      key={week.week_id}
                      onClick={() => setActiveWeek(week.week_id)}
                      className={`px-4 py-2 text-sm whitespace-nowrap flex-shrink-0 ${
                        activeWeek === week.week_id
                          ? 'border-b-2 border-ocean-teal text-ocean-navy font-medium'
                          : 'text-gray-500 hover:text-gray-700'
                      }`}
                    >
                      Week {week.week_number}
                    </button>
                  ))}
                </div>

                {/* Days grid - scrollable */}
                {activeWeek && days[activeWeek] && (
                  <div className="overflow-y-auto flex-1 pt-4 -mx-1 px-1">
                    <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                      {days[activeWeek]
                        .filter(day => day.day_id !== excludeDayId)
                        .sort((a, b) => a.day_number - b.day_number)
                        .map(day => (
                          <button
                            key={day.day_id}
                            onClick={() => handleDayClick(day.day_id)}
                            className="border rounded-md p-3 text-left hover:bg-gray-50 active:bg-gray-100 flex items-center justify-between gap-2"
                          >
                            <div>
                              <p className="font-medium">Day {day.day_number}</p>
                              <p className="text-sm text-muted-foreground">
                                {formatDate(day.date, { weekday: 'short', month: 'short', day: 'numeric' })}
                              </p>
                            </div>
                            {day.focus && (
                              <div className="flex gap-1 flex-shrink-0">
                                {parseFocusTags(day.focus).map(tag => (
                                  <FocusTag key={tag} focus={tag} size="sm" />
                                ))}
                              </div>
                            )}
                          </button>
                        ))
                      }
                    </div>
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