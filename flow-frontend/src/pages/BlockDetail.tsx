import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import Layout from '../components/Layout';
import FocusTag from '../components/FocusTag';
import { getBlock, getWeeks, getDays, updateDay, updateBlock } from '../services/api';
import type { Block, Week, Day } from '../services/api';
import Modal from '../components/Modal';
import DayForm from '../components/DayForm';
import FormButton from '../components/FormButton';
import { formatDate } from '../utils/dateUtils';
import { toast } from 'react-toastify';


interface BlockDetailProps {
  user: any;
  signOut: () => void;
}

const BlockDetail = ({ user, signOut }: BlockDetailProps) => {
  const { blockId } = useParams<{ blockId: string }>();
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
  const [isBulkEditing, setIsBulkEditing] = useState(false);
  const [applyToAllWeeks, setApplyToAllWeeks] = useState(true);
  const [showFullDescription, setShowFullDescription] = useState(false);
  const [isEditingDescription, setIsEditingDescription] = useState(false);
  const [isSavingDescription, setIsSavingDescription] = useState(false);
  const [descriptionContent, setDescriptionContent] = useState('');


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
  }, [blockId]);

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
          <div className="h-6 bg-gray-200 rounded w-20 mb-2 animate-pulse"></div>
          <div className="h-3 bg-gray-200 rounded w-40 animate-pulse"></div>
        </div>
        <div className="h-9 bg-gray-200 rounded w-32 animate-pulse"></div>
      </div>

      <div className="overflow-hidden border border-gray-200 rounded-lg">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-3 py-2 text-left font-medium text-gray-600">Day</th>
              <th className="px-3 py-2 text-left font-medium text-gray-600">Date</th>
              <th className="px-3 py-2 text-left font-medium text-gray-600">Focus</th>
              <th className="px-3 py-2 text-center font-medium text-gray-600">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {[1, 2, 3, 4, 5, 6, 7].map((i) => (
              <tr key={i} className="animate-pulse">
                <td className="px-3 py-2">
                  <div className="h-4 bg-gray-200 rounded w-12"></div>
                </td>
                <td className="px-3 py-2">
                  <div className="h-4 bg-gray-200 rounded w-20"></div>
                </td>
                <td className="px-3 py-2">
                  <div className="h-5 bg-gray-200 rounded w-16"></div>
                </td>
                <td className="px-3 py-2">
                  <div className="flex justify-center space-x-1">
                    <div className="h-6 bg-gray-200 rounded w-12"></div>
                    <div className="h-6 bg-gray-200 rounded w-16"></div>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  // Week Error State Component
  const WeekErrorState = ({ weekId, error }: { weekId: string; error: string }) => (
    <div className="p-6">
      <div className="text-center py-8">
        <div className="text-red-500 mb-2">⚠️</div>
        <p className="text-gray-600 mb-4">{error}</p>
        <FormButton
          onClick={() => loadWeekData(weekId)}
          variant="primary"
          size="md"
        >
          Retry Loading Week
        </FormButton>
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
        const dayNumbers = selectedItems.map(item => item.dayNumber);
        Object.entries(daysMap).forEach(([weekId, days]) => {
          days.forEach(day => {
            if (dayNumbers.includes(day.day_number)) {
              updates.push({ dayId: day.day_id, weekId });
            }
          });
        });
      } else {
        selectedItems.forEach(item => {
          updates.push({ dayId: item.dayId, weekId: activeWeek! });
        });
      }

      // Update UI immediately
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
          if (index > 0 && index % 3 === 0) {
            await new Promise(resolve => setTimeout(resolve, 300));
          }
          await updateDay(dayId, { focus: newFocusValue });
          return { dayId, success: true };
        } catch (error) {
          console.error(`Focus update failed for day ${dayId}:`, error);
          return { dayId, success: false, error };
        }
      });

      // Wait for all updates and handle failures silently
      const results = await Promise.all(updatePromises);
      const failedUpdates = results.filter(r => !r.success);
      
      if (failedUpdates.length > 0) {
        console.warn(`${failedUpdates.length} focus updates failed:`, failedUpdates);
        // Optionally: Show a toast notification instead of alert
        // toast.error(`${failedUpdates.length} updates failed - changes reverted`);
        
        // Revert failed updates in UI
        setDaysMap(prev => {
          const revertedDaysMap = { ...prev };
          failedUpdates.forEach(({ dayId }) => {
            const update = updates.find(u => u.dayId === dayId);
            if (update && revertedDaysMap[update.weekId]) {
              // Revert to original focus value (would need to store original state)
              // For now, refetch only failed day's week data
            }
          });
          return revertedDaysMap;
        });
      }

    } catch (error) {
      console.error('Bulk focus update error:', error);
      // Could revert all changes and refetch if needed
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
              <div className="h-8 bg-gray-200 rounded w-64 animate-pulse"></div>
              <div className="h-9 bg-gray-200 rounded w-24 animate-pulse"></div>
            </div>

            {/* Horizontal Block Info Card Skeleton */}
            <div className="bg-white shadow rounded-lg p-4">
              {/* Description skeleton */}
              <div className="mb-3">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-1 animate-pulse"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2 animate-pulse"></div>
              </div>
              
              {/* Horizontal layout skeleton */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-6">
                  <div className="h-4 bg-gray-200 rounded w-20 animate-pulse"></div>
                  <div className="h-4 bg-gray-200 rounded w-20 animate-pulse"></div>
                </div>
                <div className="h-5 bg-gray-200 rounded w-12 animate-pulse"></div>
              </div>
            </div>

            {/* Week Tabs Skeleton */}
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <div className="border-b border-gray-200">
                <nav className="flex">
                  {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="py-4 px-6">
                      <div className="h-4 bg-gray-200 rounded w-16 animate-pulse"></div>
                    </div>
                  ))}
                </nav>
              </div>

              {/* Days Grid Skeleton */}
              <div className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <div>
                    <div className="h-6 bg-gray-200 rounded w-20 mb-2 animate-pulse"></div>
                    <div className="h-3 bg-gray-200 rounded w-40 animate-pulse"></div>
                  </div>
                  <div className="h-9 bg-gray-200 rounded w-32 animate-pulse"></div>
                </div>

                <div className="overflow-hidden border border-gray-200 rounded-lg">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">Day</th>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">Date</th>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">Focus</th>
                        <th className="px-3 py-2 text-center font-medium text-gray-600">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 bg-white">
                      {[1, 2, 3, 4, 5, 6, 7].map((i) => (
                        <tr key={i} className="animate-pulse">
                          <td className="px-3 py-2">
                            <div className="h-4 bg-gray-200 rounded w-12"></div>
                          </td>
                          <td className="px-3 py-2">
                            <div className="h-4 bg-gray-200 rounded w-20"></div>
                          </td>
                          <td className="px-3 py-2">
                            <div className="h-5 bg-gray-200 rounded w-16"></div>
                          </td>
                          <td className="px-3 py-2">
                            <div className="flex justify-center space-x-1">
                              <div className="h-6 bg-gray-200 rounded w-12"></div>
                              <div className="h-6 bg-gray-200 rounded w-16"></div>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
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

            <div className="bg-white shadow rounded-lg p-4">
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
                <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                  block.status === 'active' 
                    ? 'bg-green-100 text-green-800' 
                    : block.status === 'completed'
                    ? 'bg-blue-100 text-blue-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {block.status.charAt(0).toUpperCase() + block.status.slice(1)}
                </span>
              </div>
            </div>

            {weeks.length > 0 ? (
              <div className="bg-white shadow rounded-lg overflow-hidden">
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
                            <FormButton
                              onClick={() => setIsBulkEditing(true)}
                              variant="primary"
                              size="md"
                            >
                              Bulk Edit Focus
                            </FormButton>
                          ) : (
                            <div className="flex flex-wrap items-center gap-3">
                              <select
                                value={bulkFocus}
                                onChange={(e) => setBulkFocus(e.target.value)}
                                className="text-sm border-gray-300 rounded-md"
                              >
                                <option value="">Select Focus</option>
                                <option value="squat">Squat</option>
                                <option value="bench">Bench</option>
                                <option value="deadlift">Deadlift</option>
                                <option value="cardio">Cardio</option>
                                <option value="rest">Rest</option>
                              </select>

                              <div className="flex items-center">
                                <input
                                  type="checkbox"
                                  id="applyToAllWeeks"
                                  checked={applyToAllWeeks}
                                  onChange={(e) => setApplyToAllWeeks(e.target.checked)}
                                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                />
                                <label
                                  htmlFor="applyToAllWeeks"
                                  className="ml-2 text-sm text-gray-700"
                                >
                                  Apply to all weeks
                                </label>
                              </div>

                              <FormButton
                                onClick={handleBulkUpdate}
                                disabled={!bulkFocus || Object.values(selectedDays).filter(Boolean).length === 0}
                                variant="primary"
                                size="md"
                              >
                                Apply Focus
                              </FormButton>

                              <FormButton
                                onClick={handleClearFocus}
                                disabled={Object.values(selectedDays).filter(Boolean).length === 0}
                                variant="secondary"
                                size="md"
                              >
                                Clear Focus
                              </FormButton>

                              <FormButton
                                onClick={() => {
                                  setIsBulkEditing(false);
                                  setSelectedDays({});
                                  setBulkFocus('');
                                }}
                                variant="secondary"
                                size="md"
                              >
                                Cancel
                              </FormButton>
                            </div>
                          )}
                        </div>

                        <div className="overflow-hidden border border-gray-200 rounded-lg">
                          <table className="w-full text-sm">
                            <thead className="bg-gray-50">
                              <tr>
                                {isBulkEditing && (
                                  <th className="px-3 py-2 text-left">
                                    <input
                                      type="checkbox"
                                      onChange={(e) => {
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
                                      checked={
                                        !!(activeWeek &&
                                        daysMap[activeWeek]?.length > 0 && 
                                        daysMap[activeWeek].every((day: any) => selectedDays[day.day_id]))
                                      }
                                      className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                    />
                                  </th>
                                )}
                                <th className="px-3 py-2 text-left font-medium text-gray-600">Day</th>
                                <th className="px-3 py-2 text-left font-medium text-gray-600">Date</th>
                                <th className="px-3 py-2 text-left font-medium text-gray-600">Focus</th>
                                <th className="px-3 py-2 text-center font-medium text-gray-600">Actions</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200 bg-white">
                              {activeWeek && daysMap[activeWeek] ? [...daysMap[activeWeek]]
                                .sort((a, b) => a.day_number - b.day_number)
                                .map((day) => (
                                  <tr
                                    key={day.day_id}
                                    className={`hover:bg-gray-50 ${
                                      isBulkEditing && selectedDays[day.day_id] ? 'bg-blue-50' : ''
                                    }`}
                                    onClick={isBulkEditing ? () => {
                                      setSelectedDays(prev => ({
                                        ...prev,
                                        [day.day_id]: !prev[day.day_id]
                                      }));
                                    } : undefined}
                                    style={isBulkEditing ? { cursor: 'pointer' } : undefined}
                                  >
                                    {isBulkEditing && (
                                      <td className="px-3 py-2">
                                        <input
                                          type="checkbox"
                                          checked={selectedDays[day.day_id] || false}
                                          onChange={() => {
                                            setSelectedDays(prev => ({
                                              ...prev,
                                              [day.day_id]: !prev[day.day_id]
                                            }));
                                          }}
                                          className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                        />
                                      </td>
                                    )}
                                    <td className="px-3 py-2 font-medium text-gray-900">
                                      Day {day.day_number}
                                    </td>
                                    <td className="px-3 py-2 text-gray-600">
                                      {formatDate(day.date, {
                                        weekday: 'short',
                                        month: 'short',
                                        day: 'numeric',
                                      })}
                                    </td>
                                    <td className="px-3 py-2">
                                      {day.focus ? (
                                        <FocusTag focus={day.focus} size="sm" />
                                      ) : (
                                        <button
                                          onClick={(e) => {
                                            e.stopPropagation();
                                            setEditingDay(day);
                                          }}
                                          className="text-blue-600 text-xs border border-blue-200 px-2 py-0.5 rounded hover:bg-blue-50"
                                          disabled={isBulkEditing}
                                        >
                                          Set Focus
                                        </button>
                                      )}
                                    </td>
                                    <td className="px-3 py-2 text-center">
                                      {!isBulkEditing && (
                                        <div className="flex justify-center space-x-1">
                                          <button
                                            onClick={(e) => {
                                              e.stopPropagation();
                                              setEditingDay(day);
                                            }}
                                            className="text-blue-600 text-xs px-2 py-1 border border-blue-200 rounded hover:bg-blue-50"
                                          >
                                            Focus
                                          </button>
                                          <button
                                            onClick={(e) => {
                                              e.stopPropagation();
                                              window.location.href = `/days/${day.day_id}?blockId=${blockId}`;
                                            }}
                                            className="bg-blue-600 text-white text-xs px-2 py-1 rounded hover:bg-blue-700"
                                          >
                                            Workout
                                          </button>
                                        </div>
                                      )}
                                    </td>
                                  </tr>
                                )) : []}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    ) : null}
                  </>
                )}
              </div>
            ) : (
              <div className="bg-white shadow rounded-lg p-6 text-center">
                <p className="text-gray-500">If you don't see any weeks, please refresh the page</p>
              </div>
            )}
          </>
        ) : (
          <div className="bg-white shadow rounded-lg p-6 text-center">
            <p className="text-gray-500">Block not found or failed to load.</p>
            <p className="text-sm text-gray-400 mt-2">Block ID: {blockId}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Retry
            </button>
          </div>
        )}
      </div>
      
      {/* Day Edit Modal */}
      <Modal
        isOpen={!!editingDay}
        onClose={() => setEditingDay(null)}
        title={editingDay ? `Edit Day ${editingDay.day_number}` : ''}
      >
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

                // Close modal immediately for better UX
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
      </Modal>
    </Layout>
  );
};

export default BlockDetail;
