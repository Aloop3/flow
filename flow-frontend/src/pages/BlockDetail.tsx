import { useState, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { useParams, Link, useLocation } from 'react-router-dom';
import Layout from '../components/Layout';
import FocusTag from '../components/FocusTag';
import { getBlock, getWeeks, getDays, updateDay, updateBlock } from '../services/api';
import type { Block, Week, Day } from '../services/api';
import DayForm from '../components/DayForm';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Skeleton } from '@/components/ui/skeleton';
import { Card, CardContent } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { formatDate } from '../utils/dateUtils';
import { toast } from 'react-toastify';



interface BlockDetailProps {
  user: any;
  signOut: () => void;
}

const BlockDetail = ({ user, signOut }: BlockDetailProps) => {
  const { blockId } = useParams<{ blockId: string }>();
  const location = useLocation();
  const [block, setBlock] = useState<Block | null>(null);
  const [weeks, setWeeks] = useState<Week[]>([]);
  const [daysMap, setDaysMap] = useState<{ [weekId: string]: Day[] }>({});
  const [isLoading, setIsLoading] = useState(true);
  const [activeWeek, setActiveWeek] = useState<string | null>(null);
  const [weekLoadingStates, setWeekLoadingStates] = useState<{ [weekId: string]: boolean }>({});
  const [loadedWeeks, setLoadedWeeks] = useState<Set<string>>(new Set());
  const [weekLoadErrors, setWeekLoadErrors] = useState<{ [weekId: string]: string }>({});
  const [editingDay, setEditingDay] = useState<any>(null);
  const [selectedDays, setSelectedDays] = useState<{ [key: string]: boolean }>({});
  const [bulkFocus, setBulkFocus] = useState<string>('');
  const [editingFocusDayId, setEditingFocusDayId] = useState<string | null>(null);
  const [isSavingFocus, setIsSavingFocus] = useState(false);
  const [isBulkEditing, setIsBulkEditing] = useState(false);
  const [applyToAllWeeks, setApplyToAllWeeks] = useState(true);
  const [showFullDescription, setShowFullDescription] = useState(false);
  const [isEditingDescription, setIsEditingDescription] = useState(false);
  const [isSavingDescription, setIsSavingDescription] = useState(false);
  const [descriptionContent, setDescriptionContent] = useState('');
  const focusOptions = [
    { value: '', label: 'No focus' },
    { value: 'squat', label: 'Squat' },
    { value: 'bench', label: 'Bench' },
    { value: 'deadlift', label: 'Deadlift' },
    { value: 'cardio', label: 'Cardio' },
    { value: 'rest', label: 'Rest' },
  ];

  const focusTagRef = useRef<HTMLDivElement>(null) as React.RefObject<HTMLDivElement>;
  
  const FocusDropdownPortal = ({ 
    isOpen, 
    onClose, 
    onSelect, 
    triggerRef,
    options, 
    isSaving 
  }: {
    isOpen: boolean;
    onClose: () => void;
    onSelect: (value: string) => void;
    triggerRef: React.RefObject<HTMLDivElement>;
    options: Array<{ value: string; label: string }>;
    isSaving: boolean;
  }) => {
    const [position, setPosition] = useState<{ top: number; left: number } | null>(null);

    useEffect(() => {
      if (isOpen && triggerRef.current) {
        const rect = triggerRef.current.getBoundingClientRect();
        setPosition({
          top: rect.bottom + window.scrollY + 4,
          left: rect.left + window.scrollX
        });
      } else {
        setPosition(null);
      }
    }, [isOpen, triggerRef]);

    if (!isOpen || !position) return null;

    return createPortal(
      <>
        {/* Backdrop */}
        <div 
          className="fixed inset-0 z-40" 
          onClick={onClose}
        />
        
        {/* Dropdown */}
        <div 
          className="absolute z-50 bg-white border border-gray-300 rounded-md shadow-xl py-1 min-w-[120px]"
          style={{
            top: position.top,
            left: position.left
          }}
        >
          {options.map(option => (
            <button
              key={option.value}
              onClick={() => onSelect(option.value)}
              disabled={isSaving}
              className="w-full text-left px-3 py-2 hover:bg-gray-100 flex items-center space-x-2 disabled:opacity-50"
            >
              {option.value ? (
                <FocusTag focus={option.value} size="sm" />
              ) : (
                <span className="text-gray-500 italic text-sm">No focus</span>
              )}
            </button>
          ))}
        </div>
      </>,
      document.body
    );
  };

  const loadWeekData = async (weekId: string, retryCount = 0): Promise<boolean> => {
    if (loadedWeeks.has(weekId) || weekLoadingStates[weekId]) {
      return true; // Already loaded or loading
    }
    
    console.log(`🔄 Loading week data: ${weekId} (attempt ${retryCount + 1})`);
    setWeekLoadingStates(prev => ({ ...prev, [weekId]: true }));
    setWeekLoadErrors(prev => ({ ...prev, [weekId]: '' })); // Clear previous errors
    
    try {
      const startTime = performance.now();
      const daysData = await getDays(weekId);
      const loadTime = performance.now() - startTime;
      
      console.log(`✅ Week ${weekId} loaded in ${loadTime.toFixed(0)}ms (${daysData.length} days)`);
      
      const sortedDays = Array.isArray(daysData)
        ? [...daysData].sort((a, b) => a.day_number - b.day_number)
        : [];
      
      setDaysMap(prev => ({ ...prev, [weekId]: sortedDays }));
      setLoadedWeeks(prev => new Set([...prev, weekId]));
      
      return true;
    } catch (error) {
      console.error(`❌ Failed to load week ${weekId} (attempt ${retryCount + 1}):`, error);
      
      // Automatic retry with exponential backoff (max 2 retries)
      if (retryCount < 2) {
        const retryDelay = retryCount === 0 ? 200 : 500; // 200ms, 500ms 
        console.log(`🔄 Retrying week ${weekId} in ${retryDelay}ms...`);
        
        setTimeout(async () => {
          await loadWeekData(weekId, retryCount + 1);
        }, retryDelay);
        
        return false;
      } else {
        // Max retries exceeded
        const errorMessage = `Failed to load week data after 3 attempts`;
        setWeekLoadErrors(prev => ({ ...prev, [weekId]: errorMessage }));
        return false;
      }
    } finally {
      setWeekLoadingStates(prev => ({ ...prev, [weekId]: false }));
    }
  };

  function handleFocusClick(dayId: string) {
    setEditingFocusDayId(dayId);
  }

  async function handleFocusChange(dayId: string, newFocus: string) {
    // Similar logic to DayDetail
    if (newFocus === daysMap[activeWeek!]
        .find(d => d.day_id === dayId)?.focus) {
      setEditingFocusDayId(null);
      return;
    }

    setIsSavingFocus(true);
    try {
      await updateDay(dayId, { focus: newFocus || null });
      setDaysMap(m => ({
        ...m,
        [activeWeek!]: m[activeWeek!]!.map(d =>
          d.day_id === dayId ? { ...d, focus: newFocus || null } : d
        )
      }));
      toast.success('Focus updated successfully!');
    } catch {
      toast.error('Failed to update focus');
    } finally {
      setIsSavingFocus(false);
      setEditingFocusDayId(null);
    }
  }

  // Initial data loading - only load first week
  useEffect(() => {
    const fetchInitialData = async () => {
      if (!blockId) return;
      
      const startTime = performance.now();
      setIsLoading(true);
      try {
        // Load block + weeks in parallel (not sequential)
        console.log('🚀 Starting parallel fetch: block + weeks');
        const parallelStart = performance.now();
        
        const [blockData, weeksData] = await Promise.all([
          getBlock(blockId),
          getWeeks(blockId)
        ]);
        
        console.log(`⚡ Parallel fetch complete: ${(performance.now() - parallelStart).toFixed(0)}ms`);
        
        // Validate block data first
        if (!blockData) {
          console.log('❌ Block not found');
          return;
        }
        setBlock(blockData);
        setDescriptionContent(blockData.description || '');

        // Process weeks data
        const sortedWeeks = Array.isArray(weeksData)
          ? [...weeksData].sort((a, b) => a.week_number - b.week_number)
          : [];
        setWeeks(sortedWeeks);

        if (sortedWeeks.length === 0) {
          console.log('ℹ️ No weeks found for block');
          setActiveWeek(null);
          setDaysMap({});
          return;
        }

        // Set active week immediately, load data in background
        const firstWeek = sortedWeeks[0];
        console.log(`🔄 Setting active week and loading data: ${firstWeek.week_id}`);
        
        // Set active week immediately for responsive UI
        setActiveWeek(firstWeek.week_id);
        
        // Load first week in background (don't await)
        loadWeekData(firstWeek.week_id);

        const totalTime = performance.now() - startTime;
        console.log(`🎯 INITIAL LOAD COMPLETE: ${totalTime.toFixed(0)}ms`);
        console.log(`📈 Loaded: Block + ${sortedWeeks.length} weeks metadata (first week loading in background)`);
        
      } catch (error) {
        console.error('❌ Error fetching initial data:', error);
        toast.error('Failed to load block data');
      } finally {
        setIsLoading(false);
      }
    };

    fetchInitialData();
  }, [blockId, location.pathname]);

  // Week tab click handler with preloading
  const handleWeekTabClick = async (weekId: string) => {
    console.log(`🖱️ Week tab clicked: ${weekId}`);
    
    // Immediately switch active week for responsive UI
    setActiveWeek(weekId);
    
    // Load week data if not already loaded
    if (!loadedWeeks.has(weekId)) {
      await loadWeekData(weekId);
    }
    
    // OPTIMIZATION: Preload adjacent weeks for faster navigation
    const currentWeekIndex = weeks.findIndex(w => w.week_id === weekId);
    if (currentWeekIndex !== -1) {
      // Preload next week in background (non-blocking)
      if (currentWeekIndex < weeks.length - 1) {
        const nextWeekId = weeks[currentWeekIndex + 1].week_id;
        if (!loadedWeeks.has(nextWeekId) && !weekLoadingStates[nextWeekId]) {
          console.log(`🔮 Preloading next week: ${nextWeekId}`);
          loadWeekData(nextWeekId); // Don't await - background preload
        }
      }
      
      // Preload previous week in background (non-blocking)
      if (currentWeekIndex > 0) {
        const prevWeekId = weeks[currentWeekIndex - 1].week_id;
        if (!loadedWeeks.has(prevWeekId) && !weekLoadingStates[prevWeekId]) {
          console.log(`🔮 Preloading previous week: ${prevWeekId}`);
          loadWeekData(prevWeekId); // Don't await - background preload
        }
      }
    }
  };

  // Week Loading Skeleton Component
  const WeekLoadingSkeleton = () => (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <Skeleton className="h-6 w-20 mb-2" />
          <Skeleton className="h-3 w-40" />
        </div>
        <Skeleton className="h-9 w-32" />
      </div>

      <div className="border rounded-lg">
        <Table>
          <TableHeader>
            <TableRow className="bg-muted/50">
              <TableHead>Day</TableHead>
              <TableHead>Date</TableHead>
              <TableHead>Focus</TableHead>
              <TableHead className="text-center">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {[1, 2, 3, 4, 5, 6, 7].map((i) => (
              <TableRow key={i}>
                <TableCell>
                  <Skeleton className="h-4 w-12" />
                </TableCell>
                <TableCell>
                  <Skeleton className="h-4 w-20" />
                </TableCell>
                <TableCell>
                  <Skeleton className="h-5 w-16" />
                </TableCell>
                <TableCell>
                  <div className="flex justify-center">
                    <Skeleton className="h-6 w-16" />
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );

  // Week Error State Component
  const WeekErrorState = ({ weekId, error }: { weekId: string; error: string }) => (
    <div className="p-6">
      <div className="text-center py-8">
        <div className="text-red-500 mb-2">⚠️</div>
        <p className="text-gray-600 mb-4">{error}</p>
        <Button onClick={() => loadWeekData(weekId)}>
          Retry Loading Week
        </Button>
      </div>
    </div>
  );


  useEffect(() => {
    if (block) {
      setDescriptionContent(block.description || '');
    }
  }, [block]);

  const handleBulkUpdate = async () => {
    try {
      const selectedItems = Object.entries(selectedDays)
        .filter(([_, isSelected]) => isSelected)
        .map(([dayId]) => {
          const day = activeWeek ? daysMap[activeWeek]?.find(d => d.day_id === dayId) : undefined;
          return { dayId, dayNumber: day?.day_number || 0 };
        });

      if (selectedItems.length === 0 || (!bulkFocus && bulkFocus !== 'clear')) return;

      const isClearingFocus = bulkFocus === 'clear';
      const newFocusValue = isClearingFocus ? undefined : bulkFocus;
      
      // Collect all updates needed
      const updates: { dayId: string; weekId: string }[] = [];
      
      if (applyToAllWeeks) {
        console.log(`🔄 Bulk update: fetching all ${weeks.length} weeks for day numbers: ${selectedItems.map(i => i.dayNumber).join(', ')}`);
        
        // Show loading state since we're fetching potentially many weeks
        const originalBulkEditing = isBulkEditing;
        setIsBulkEditing(false); // Hide controls during loading
        
        try {
          const dayNumbers = selectedItems.map(item => item.dayNumber);
          
          // Fetch day data for all weeks that aren't already loaded
          const weekFetchPromises = weeks.map(async (week) => {
            if (daysMap[week.week_id]) {
              // Week already loaded, use existing data
              return { weekId: week.week_id, days: daysMap[week.week_id] };
            } else {
              // Week not loaded, fetch it
              console.log(`📡 Fetching days for week ${week.week_number} (${week.week_id})`);
              try {
                const daysData = await getDays(week.week_id);
                const sortedDays = Array.isArray(daysData)
                  ? [...daysData].sort((a, b) => a.day_number - b.day_number)
                  : [];
                return { weekId: week.week_id, days: sortedDays };
              } catch (error) {
                console.error(`❌ Failed to fetch week ${week.week_number}:`, error);
                return { weekId: week.week_id, days: [] };
              }
            }
          });
          
          // Wait for all week data to be fetched
          const allWeeksData = await Promise.all(weekFetchPromises);
          
          // Update daysMap with newly fetched weeks (for caching)
          const newDaysMap = { ...daysMap };
          allWeeksData.forEach(({ weekId, days }) => {
            if (days.length > 0 && !newDaysMap[weekId]) {
              newDaysMap[weekId] = days;
              setLoadedWeeks(prev => new Set([...prev, weekId]));
            }
          });
          setDaysMap(newDaysMap);
          
          // Now collect updates from ALL weeks
          allWeeksData.forEach(({ weekId, days }) => {
            days.forEach(day => {
              if (dayNumbers.includes(day.day_number)) {
                updates.push({ dayId: day.day_id, weekId });
              }
            });
          });
          
          console.log(`✅ Collected ${updates.length} updates across ${allWeeksData.length} weeks`);
          
        } catch (error) {
          console.error('❌ Failed to fetch week data for bulk update:', error);
          toast.error('Failed to load all weeks for bulk update');
          setIsBulkEditing(originalBulkEditing);
          return;
        }
        
        // Restore bulk editing controls
        setIsBulkEditing(originalBulkEditing);
        
      } else {
        // Single week - use existing logic
        selectedItems.forEach(item => {
          updates.push({ dayId: item.dayId, weekId: activeWeek! });
        });
      }

      console.log(`🎯 Processing ${updates.length} bulk updates`);

      // Update UI immediately for all affected weeks (now we have all the data)
      setDaysMap(prev => {
        const newDaysMap = { ...prev };
        updates.forEach(({ dayId, weekId }) => {
          if (newDaysMap[weekId]) {
            newDaysMap[weekId] = newDaysMap[weekId].map(day =>
              day.day_id === dayId 
                ? { ...day, focus: newFocusValue }
                : day
            );
          }
        });
        return newDaysMap;
      });

      // Clear UI state immediately for better UX
      setSelectedDays({});
      setBulkFocus('');
      setIsBulkEditing(false);

      // Background API updates (no loading state needed)
      const updatePromises = updates.map(async ({ dayId }, index) => {
        try {
          // Stagger requests to prevent rate limiting
          if (index > 0 && index % 5 === 0) {
            await new Promise(resolve => setTimeout(resolve, 200));
          }
          await updateDay(dayId, { focus: newFocusValue });
          return { dayId, success: true };
        } catch (error) {
          console.error(`Focus update failed for day ${dayId}:`, error);
          return { dayId, success: false, error };
        }
      });

      // Wait for all updates and handle failures
      const results = await Promise.all(updatePromises);
      const failedUpdates = results.filter(r => !r.success);
      
      if (failedUpdates.length > 0) {
        console.warn(`${failedUpdates.length}/${updates.length} focus updates failed`);
        toast.error(`${failedUpdates.length} updates failed - please refresh affected weeks`);
        
        // For failed updates, invalidate affected weeks to force fresh data
        const failedWeekIds = new Set(
          failedUpdates
            .map(failed => updates.find(u => u.dayId === failed.dayId)?.weekId)
            .filter((weekId): weekId is string => weekId !== undefined)
        );
        
        if (failedWeekIds.size > 0) {
          console.log(`🔄 Invalidating failed weeks: ${Array.from(failedWeekIds).join(', ')}`);
          setLoadedWeeks(prev => {
            const newLoadedWeeks = new Set(prev);
            failedWeekIds.forEach(weekId => newLoadedWeeks.delete(weekId));
            return newLoadedWeeks;
          });
          
          // Force reload current week if it failed
          if (activeWeek && failedWeekIds.has(activeWeek)) {
            await loadWeekData(activeWeek);
          }
        }
      } else {
        toast.success(`Focus updated for ${updates.length} days across ${applyToAllWeeks ? weeks.length : 1} week${applyToAllWeeks && weeks.length > 1 ? 's' : ''}!`);
      }

      console.log(`✅ Bulk update complete: ${updates.length - failedUpdates.length}/${updates.length} successful`);

    } catch (error) {
      console.error('Bulk focus update error:', error);
      toast.error('Bulk update failed - please try again');
    }
  };

  const handleClearFocus = async () => {
    // Simplified - just call handleBulkUpdate with 'clear' value
    setBulkFocus('clear');
    await handleBulkUpdate();
  };

  const descriptionEditableRef = useRef<HTMLDivElement>(null);

  const handleDescriptionClick = () => {
    setIsEditingDescription(true);
    setShowFullDescription(true);
    requestAnimationFrame(() => {
      if (descriptionEditableRef.current) {
        descriptionEditableRef.current.textContent = descriptionContent;
        descriptionEditableRef.current.focus();
      }
    });
  };

  const handleDescriptionBlur = async () => {
    if (!descriptionEditableRef.current) return;

    // grab whatever the user typed
    const newText = descriptionEditableRef.current.textContent?.trim() || '';

    // prime your React state so your comparisons & API call see it
    setDescriptionContent(newText);

    // if nothing changed, just exit edit mode
    if (!block || newText === (block.description || '')) {
      setIsEditingDescription(false);
      return;
    };

    setIsSavingDescription(true);
    try {
      await updateBlock(block.block_id, { description: newText });
      setBlock(prev => prev ? { ...prev, description: newText } : null);
      toast.success('Description saved successfully!');
    } catch (error) {
      console.error('Error saving description:', error);
      toast.error('Failed to save description');
      // revert to server copy
      setDescriptionContent(block.description || '');
    } finally {
      setIsEditingDescription(false);
      setIsSavingDescription(false);
    };
  };

  const handleDescriptionKeyDown = (e: React.KeyboardEvent) => {
    // Save on Ctrl+Enter (multi-line content)
    if (e.key === 'Enter' && e.ctrlKey) {
      e.preventDefault();
      (e.target as HTMLElement).blur();
    }
    // Cancel on Escape
    if (e.key === 'Escape') {
      setDescriptionContent(block?.description || '');
      setIsEditingDescription(false);
    }
  };

  return (
    <Layout user={user} signOut={signOut}>
      <div className="space-y-6">
        {isLoading ? (
          <div className="space-y-6">
            {/* Block Header Skeleton */}
            <div className="flex justify-between items-center">
              <Skeleton className="h-8 w-64" />
              <Skeleton className="h-9 w-24" />
            </div>

            {/* Horizontal Block Info Card Skeleton */}
            <Card>
              <CardContent className="pt-4">
                {/* Description skeleton */}
                <div className="mb-3">
                  <Skeleton className="h-4 w-3/4 mb-1" />
                  <Skeleton className="h-4 w-1/2" />
                </div>

                {/* Horizontal layout skeleton */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-6">
                    <Skeleton className="h-4 w-20" />
                    <Skeleton className="h-4 w-20" />
                  </div>
                  <Skeleton className="h-5 w-12" />
                </div>
              </CardContent>
            </Card>

            {/* Week Tabs Skeleton */}
            <Card className="overflow-visible">
              <div className="border-b border-gray-200">
                <nav className="flex">
                  {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="py-4 px-6">
                      <Skeleton className="h-4 w-16" />
                    </div>
                  ))}
                </nav>
              </div>

              {/* Days Grid Skeleton */}
              <div className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <div>
                    <Skeleton className="h-6 w-20 mb-2" />
                    <Skeleton className="h-3 w-40" />
                  </div>
                  <Skeleton className="h-9 w-32" />
                </div>

                <div className="border rounded-lg">
                  <Table>
                    <TableHeader>
                      <TableRow className="bg-muted/50">
                        <TableHead>Day</TableHead>
                        <TableHead>Date</TableHead>
                        <TableHead>Focus</TableHead>
                        <TableHead className="text-center">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {[1, 2, 3, 4, 5, 6, 7].map((i) => (
                        <TableRow key={i}>
                          <TableCell>
                            <Skeleton className="h-4 w-12" />
                          </TableCell>
                          <TableCell>
                            <Skeleton className="h-4 w-20" />
                          </TableCell>
                          <TableCell>
                            <Skeleton className="h-5 w-16" />
                          </TableCell>
                          <TableCell>
                            <div className="flex justify-center">
                              <Skeleton className="h-6 w-16" />
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </div>
            </Card>
          </div>
        ) : block ? (
          <>
            <div className="flex justify-between items-center">
              <h1 className="text-2xl font-bold text-gray-900">{block.title}</h1>
              <Link
                to={`/blocks/${blockId}/edit`}
                className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                Edit Program
              </Link>
            </div>

            <Card>
              <CardContent className="pt-4">
                {/* DESCRIPTION SECTION - EDITABLE */}
                <div className="mb-3">
                {descriptionContent || isEditingDescription ? (
                  <div className="relative">
                    <div
                      ref={descriptionEditableRef}
                      contentEditable
                      suppressContentEditableWarning={true}
                      onFocus={handleDescriptionClick}
                      onBlur={handleDescriptionBlur}
                      onKeyDown={handleDescriptionKeyDown}

                      className={`
                        min-h-[2rem] p-2 rounded border-2 transition-all duration-200 outline-none
                        text-gray-600 text-sm leading-relaxed
                        ${isEditingDescription 
                          ? 'border-blue-300 bg-blue-50 shadow-sm' 
                          : 'border-transparent hover:border-gray-200 hover:bg-gray-50 cursor-text'
                        }
                        ${isSavingDescription ? 'opacity-50' : ''}
                      `}
                      style={{
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                        maxHeight: isEditingDescription ? 'none' : (showFullDescription ? 'none' : '3rem'),
                        overflow: isEditingDescription ? 'visible' : (showFullDescription ? 'visible' : 'hidden')
                      }}
                    >
                      { !isEditingDescription && descriptionContent }
                    </div>

                    {isSavingDescription && (
                      <div className="absolute right-2 top-2">
                        <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
                      </div>
                    )}

                    {!isEditingDescription && descriptionContent.length > 100 && (
                      <button
                        onClick={() => setShowFullDescription(!showFullDescription)}
                        className="text-xs text-blue-600 hover:text-blue-800 mt-1 block"
                      >
                        {showFullDescription ? 'Show less' : 'Show more'}
                      </button>
                    )}
                  </div>
                ) : (
                  <div 
                    onClick={handleDescriptionClick}
                    className="p-2 rounded border-2 border-transparent hover:border-gray-200 hover:bg-gray-50 cursor-text min-h-[2rem] text-gray-400 italic text-sm"
                  >
                    Click to add block description...
                  </div>
                )}
              </div>
              
              {/* Horizontal date and status layout */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-6">
                  <div>
                    <span className="text-xs font-medium text-gray-500">Start:</span>
                    <span className="ml-1 text-sm text-gray-900">{formatDate(block.start_date)}</span>
                  </div>
                  <div>
                    <span className="text-xs font-medium text-gray-500">End:</span>
                    <span className="ml-1 text-sm text-gray-900">{formatDate(block.end_date)}</span>
                  </div>
                </div>
                <Badge className={
                  block.status === 'active'
                    ? 'bg-green-100 text-green-800 hover:bg-green-100'
                    : block.status === 'completed'
                    ? 'bg-blue-100 text-blue-800 hover:bg-blue-100'
                    : 'bg-gray-100 text-gray-800 hover:bg-gray-100'
                }>
                  {block.status.charAt(0).toUpperCase() + block.status.slice(1)}
                </Badge>
              </div>
              </CardContent>
            </Card>

            {weeks.length > 0 ? (
              <Card className="overflow-hidden">
                <div className="border-b border-gray-200">
                  <nav className="flex overflow-x-auto">
                    {weeks.map((week) => (
                      <button
                        key={week.week_id}
                        onClick={() => handleWeekTabClick(week.week_id)}
                        className={`py-4 px-6 text-center border-b-2 font-medium text-sm relative ${
                          activeWeek === week.week_id
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        }`}
                      >
                        Week {week.week_number}
                        {/* Loading indicator for week tab */}
                        {weekLoadingStates[week.week_id] && (
                          <div className="absolute top-1 right-1">
                            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                          </div>
                        )}
                        {/* Error indicator for week tab */}
                        {weekLoadErrors[week.week_id] && (
                          <div className="absolute top-1 right-1">
                            <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                          </div>
                        )}
                      </button>
                    ))}
                  </nav>
                </div>

                {/* Week content with lazy loading states */}
                {activeWeek && (
                  <>
                    {weekLoadingStates[activeWeek] ? (
                      <WeekLoadingSkeleton />
                    ) : weekLoadErrors[activeWeek] ? (
                      <WeekErrorState 
                        weekId={activeWeek} 
                        error={weekLoadErrors[activeWeek]} 
                      />
                    ) : daysMap[activeWeek] ? (
                      <div className="p-6">
                        <div className="flex justify-between items-center mb-6">
                          <div>
                            <h2 className="text-lg font-semibold">
                              Week {weeks.find(w => w.week_id === activeWeek)?.week_number || ''}
                            </h2>
                            <p className="text-sm text-gray-500">
                              {daysMap[activeWeek]?.length > 0 &&
                                `${formatDate(daysMap[activeWeek][0].date)} - 
                                ${formatDate(daysMap[activeWeek][daysMap[activeWeek].length - 1].date)}`}
                            </p>
                          </div>

                          {!isBulkEditing ? (
                            <Button onClick={() => setIsBulkEditing(true)}>
                              Bulk Edit Focus
                            </Button>
                          ) : (
                            <div className="space-y-3 sm:space-y-0">
                              {/* Mobile: Stacked layout, Desktop: Grid layout */}
                              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 items-end">
                                {/* Focus Selection */}
                                <div className="flex flex-col">
                                  <label className="text-xs font-medium text-gray-600 mb-1 sm:hidden">
                                    Focus Type
                                  </label>
                                  <Select value={bulkFocus} onValueChange={setBulkFocus}>
                                    <SelectTrigger className="w-full">
                                      <SelectValue placeholder="Select Focus" />
                                    </SelectTrigger>
                                    <SelectContent>
                                      <SelectItem value="squat">Squat</SelectItem>
                                      <SelectItem value="bench">Bench</SelectItem>
                                      <SelectItem value="deadlift">Deadlift</SelectItem>
                                      <SelectItem value="cardio">Cardio</SelectItem>
                                      <SelectItem value="rest">Rest</SelectItem>
                                    </SelectContent>
                                  </Select>
                                </div>

                                {/* Apply to All Weeks Checkbox */}
                                <div className="flex items-center justify-start">
                                  <input
                                    type="checkbox"
                                    id="applyToAllWeeks"
                                    checked={applyToAllWeeks}
                                    onChange={(e) => setApplyToAllWeeks(e.target.checked)}
                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded flex-shrink-0"
                                  />
                                  <label
                                    htmlFor="applyToAllWeeks"
                                    className="ml-2 text-sm text-gray-700 select-none"
                                  >
                                    Apply to all weeks
                                  </label>
                                </div>

                                {/* Action Buttons - Mobile: Full width row, Desktop: Inline */}
                                <div className="col-span-1 sm:col-span-2 lg:col-span-2 flex flex-col sm:flex-row gap-2">
                                  <Button
                                    onClick={handleBulkUpdate}
                                    disabled={!bulkFocus || Object.values(selectedDays).filter(Boolean).length === 0}
                                    className="flex-1"
                                  >
                                    Apply Focus
                                  </Button>

                                  <Button
                                    onClick={handleClearFocus}
                                    disabled={Object.values(selectedDays).filter(Boolean).length === 0}
                                    variant="outline"
                                    className="flex-1"
                                  >
                                    Clear Focus
                                  </Button>

                                  <Button
                                    onClick={() => {
                                      setIsBulkEditing(false);
                                      setSelectedDays({});
                                      setBulkFocus('');
                                    }}
                                    variant="outline"
                                    className="flex-1"
                                  >
                                    Cancel
                                  </Button>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>

                        <div className="border rounded-lg">
                          <Table>
                            <TableHeader>
                              <TableRow className="bg-muted/50">
                                {isBulkEditing && (
                                  <TableHead className="w-10">
                                    <input
                                      type="checkbox"
                                      onChange={(e) => {
                                        e.stopPropagation();
                                        if (e.target.checked && activeWeek) {
                                          const allDayIds = daysMap[activeWeek].reduce((acc: { [key: string]: boolean }, day: any) => {
                                            acc[day.day_id] = true;
                                            return acc;
                                          }, {});
                                          setSelectedDays(allDayIds);
                                        } else {
                                          setSelectedDays({});
                                        }
                                      }}
                                      onClick={(e) => {
                                        e.stopPropagation();
                                      }}
                                      checked={
                                        !!(activeWeek &&
                                        daysMap[activeWeek]?.length > 0 &&
                                        daysMap[activeWeek].every((day: any) => selectedDays[day.day_id]))
                                      }
                                      className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 touch-manipulation cursor-pointer"
                                    />
                                  </TableHead>
                                )}
                                <TableHead>Day</TableHead>
                                <TableHead>Date</TableHead>
                                <TableHead>Focus</TableHead>
                                <TableHead className="text-center">Actions</TableHead>
                              </TableRow>
                            </TableHeader>
                            <TableBody>
                              {activeWeek && daysMap[activeWeek] ? [...daysMap[activeWeek]]
                                .sort((a, b) => a.day_number - b.day_number)
                                .map((day) => (
                                  <TableRow
                                    key={day.day_id}
                                    className={isBulkEditing && selectedDays[day.day_id] ? 'bg-blue-50' : ''}
                                    onClick={isBulkEditing ? (e) => {
                                      const target = e.target as HTMLInputElement;
                                      if (target.tagName === 'INPUT' && target.type === 'checkbox') {
                                        return;
                                      }
                                      setSelectedDays(prev => ({
                                        ...prev,
                                        [day.day_id]: !prev[day.day_id]
                                      }));
                                    } : undefined}
                                    style={isBulkEditing ? { cursor: 'pointer' } : undefined}
                                  >
                                    {isBulkEditing && (
                                      <TableCell>
                                        <input
                                          type="checkbox"
                                          checked={selectedDays[day.day_id] || false}
                                          onChange={(e) => {
                                            e.stopPropagation();
                                            setSelectedDays(prev => ({
                                              ...prev,
                                              [day.day_id]: !prev[day.day_id]
                                            }));
                                          }}
                                          onClick={(e) => {
                                            e.stopPropagation();
                                          }}
                                          className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 touch-manipulation cursor-pointer"
                                        />
                                      </TableCell>
                                    )}
                                    <TableCell className="font-medium">
                                      Day {day.day_number}
                                    </TableCell>
                                    <TableCell className="text-muted-foreground">
                                      {formatDate(day.date, {
                                        weekday: 'short',
                                        month: 'short',
                                        day: 'numeric',
                                      })}
                                    </TableCell>
                                    <TableCell>
                                      <div className="relative inline-block">
                                        <div
                                          ref={editingFocusDayId === day.day_id ? focusTagRef : null}
                                          onClick={() => handleFocusClick(day.day_id)}
                                          className={`
                                            inline-block cursor-pointer p-1 rounded transition-all duration-200
                                            hover:bg-gray-100
                                            ${isSavingFocus ? 'opacity-50' : ''}
                                          `}
                                        >
                                          <FocusTag focus={day.focus || ''} size="sm" />
                                          {isSavingFocus && editingFocusDayId === day.day_id && (
                                            <span className="inline-block ml-1 animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full" />
                                          )}
                                        </div>

                                        <FocusDropdownPortal
                                          isOpen={editingFocusDayId === day.day_id}
                                          onClose={() => setEditingFocusDayId(null)}
                                          onSelect={(value) => handleFocusChange(day.day_id, value)}
                                          triggerRef={focusTagRef}
                                          options={focusOptions}
                                          isSaving={isSavingFocus}
                                        />
                                      </div>
                                    </TableCell>
                                    <TableCell className="text-center">
                                      {!isBulkEditing && (
                                        <Button
                                          size="sm"
                                          onClick={(e) => {
                                            e.stopPropagation();
                                            window.location.href = `/days/${day.day_id}?blockId=${blockId}`;
                                          }}
                                        >
                                          Workout
                                        </Button>
                                      )}
                                    </TableCell>
                                  </TableRow>
                                )) : []}
                            </TableBody>
                          </Table>
                        </div>
                      </div>
                    ) : null}
                  </>
                )}
              </Card>
            ) : (
              <Card className="p-6 text-center">
                <p className="text-muted-foreground">If you don't see any weeks, please refresh the page</p>
              </Card>
            )}
          </>
        ) : (
          <Card className="p-6 text-center">
            <p className="text-muted-foreground">Block not found or failed to load.</p>
            <p className="text-sm text-muted-foreground/70 mt-2">Block ID: {blockId}</p>
            <Button
              onClick={() => window.location.reload()}
              className="mt-4"
            >
              Retry
            </Button>
          </Card>
        )}
      </div>
      
      {/* Day Edit Dialog */}
      <Dialog open={!!editingDay} onOpenChange={(open) => !open && setEditingDay(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingDay ? `Edit Day ${editingDay.day_number}` : ''}</DialogTitle>
          </DialogHeader>
          {editingDay && (
            <DayForm
              day={editingDay}
              onSubmit={async (dayData) => {
                try {
                  // Optimistic update for individual day
                  if (activeWeek) {
                    setDaysMap(prev => ({
                      ...prev,
                      [activeWeek]: prev[activeWeek].map(day =>
                        day.day_id === dayData.day_id
                          ? { ...day, focus: dayData.focus, notes: dayData.notes }
                          : day
                      )
                    }));
                  }

                  // Close dialog immediately for better UX
                  setEditingDay(null);

                  // Background API update
                  await updateDay(dayData.day_id, {
                    focus: dayData.focus,
                    notes: dayData.notes,
                  });

                } catch (error) {
                  console.error('Error updating day:', error);

                  // Revert optimistic update on failure
                  if (activeWeek) {
                    const originalDays = await getDays(activeWeek);
                    setDaysMap(prev => ({
                      ...prev,
                      [activeWeek]: originalDays,
                    }));
                  }

                  // Show error - could use toast instead of alert
                  alert('Update failed - please try again');
                }
              }}
              isLoading={false}
              onCancel={() => setEditingDay(null)}
            />
          )}
        </DialogContent>
      </Dialog>
    </Layout>
  );
};

export default BlockDetail;
