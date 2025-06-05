import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import FocusTag from '../components/FocusTag';
import { getBlock, getWeeks, getDays, updateDay } from '../services/api';
import type { Block, Week, Day } from '../services/api';
import Modal from '../components/Modal';
import DayForm from '../components/DayForm';
import FormButton from '../components/FormButton';
import { formatDate } from '../utils/dateUtils';


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
  const [editingDay, setEditingDay] = useState<any>(null);
  const [selectedDays, setSelectedDays] = useState<{ [key: string]: boolean }>({});
  const [bulkFocus, setBulkFocus] = useState<string>('');
  const [isBulkEditing, setIsBulkEditing] = useState(false);
  const [applyToAllWeeks, setApplyToAllWeeks] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchBlockData = async () => {
      if (!blockId) return;
      
      const startTime = performance.now();
      setIsLoading(true);
      try {
        // Fetch block data first (needed for validation)
        console.log('Fetching block data for:', blockId);
        const blockStart = performance.now();
        const blockData = await getBlock(blockId);
        console.log(`📊 Block fetch: ${(performance.now() - blockStart).toFixed(0)}ms`);
        setBlock(blockData);

        if (!blockData) {
          console.log('Block not found');
          return;
        }

        // Fetch weeks in parallel
        console.log('Fetching weeks for block:', blockId);
        const weeksStart = performance.now();
        const weeksData = await getWeeks(blockId);
        console.log(`📊 Weeks fetch: ${(performance.now() - weeksStart).toFixed(0)}ms`);
        const sortedWeeks = Array.isArray(weeksData)
          ? [...weeksData].sort((a, b) => a.week_number - b.week_number)
          : [];

        setWeeks(sortedWeeks);

        if (sortedWeeks.length === 0) {
          console.log('No weeks found for block');
          setActiveWeek(null);
          setDaysMap({});
          return;
        }

        // Fetch all days in parallel using Promise.all
        console.log('Fetching days for all weeks in parallel...');
        const daysStart = performance.now();
        const daysFetchPromises = sortedWeeks.map(async (week) => {
          const singleDayStart = performance.now();
          try {
            const daysData = await getDays(week.week_id);
            console.log(`📊 Week ${week.week_number} days: ${(performance.now() - singleDayStart).toFixed(0)}ms`);
            const sortedDays = Array.isArray(daysData)
              ? [...daysData].sort((a, b) => a.day_number - b.day_number)
              : [];
            return { weekId: week.week_id, days: sortedDays };
          } catch (error) {
            console.error(`Error fetching days for week ${week.week_id}:`, error);
            return { weekId: week.week_id, days: [] };
          }
        });

        // Execute all days fetches in parallel
        const daysResults = await Promise.all(daysFetchPromises);
        console.log(`📊 All days parallel: ${(performance.now() - daysStart).toFixed(0)}ms`);
        
        // Build days map from parallel results
        const daysObj: { [weekId: string]: Day[] } = {};
        daysResults.forEach(({ weekId, days }) => {
          daysObj[weekId] = days;
        });

        setDaysMap(daysObj);
        setActiveWeek(sortedWeeks[0].week_id);

        const totalTime = performance.now() - startTime;
        console.log(`🎯 TOTAL LOAD TIME: ${totalTime.toFixed(0)}ms`);
        console.log(`📈 Breakdown: Block+Weeks+Days for ${sortedWeeks.length} weeks`);
        
        console.log('Parallel loading complete:', {
          weeksCount: sortedWeeks.length,
          totalDays: Object.values(daysObj).flat().length
        });

      } catch (error) {
        console.error('Error fetching block data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchBlockData();
  }, [blockId]);

  const handleBulkUpdate = async () => {
    try {
      const selectedItems = Object.entries(selectedDays)
        .filter(([_, isSelected]) => isSelected)
        .map(([dayId]) => {
          const day = activeWeek ? daysMap[activeWeek]?.find(d => d.day_id === dayId) : undefined;
          return { dayId, dayNumber: day?.day_number || 0 };
        });

      if (selectedItems.length === 0 || (!bulkFocus && bulkFocus !== 'clear')) return;

      setIsLoading(true);
      const isClearingFocus = bulkFocus === 'clear';
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

      const results = [];
      for (let i = 0; i < updates.length; i++) {
        const { dayId } = updates[i];
        try {
          if (i > 0 && i % 3 === 0) {
            await new Promise(resolve => setTimeout(resolve, 300));
          }
          await updateDay(dayId, { focus: isClearingFocus ? undefined : bulkFocus });
          results.push({ dayId, success: true });
        } catch (error) {
          results.push({ dayId, success: false, error });
        }
      }

      const successCount = results.filter(r => r.success).length;
      console.log(`Updated focus for ${successCount} days successfully`);

      if (applyToAllWeeks) {
        Object.keys(daysMap).forEach(async weekId => {
          const freshDays = await getDays(weekId);
          setDaysMap(prev => ({
            ...prev,
            [weekId]: [...freshDays].sort((a, b) => a.day_number - b.day_number)
          }));
        });
      } else {
        const freshDays = await getDays(activeWeek!);
        setDaysMap(prev => ({
          ...prev,
          [activeWeek!]: [...freshDays].sort((a, b) => a.day_number - b.day_number)
        }));
      }

      setSelectedDays({});
      setBulkFocus('');
      setIsBulkEditing(false);
      setIsLoading(false);
      alert(isClearingFocus ? 'Focus cleared successfully!' : 'Focus updated successfully!');
    } catch (error) {
      setIsLoading(false);
      alert('Some updates failed. Please try again with fewer days at once.');
    }
  };

  const handleClearFocus = async () => {
    try {
      const selectedItems = Object.entries(selectedDays)
        .filter(([_, isSelected]) => isSelected)
        .map(([dayId]) => {
          const day = activeWeek ? daysMap[activeWeek]?.find(d => d.day_id === dayId) : undefined;
          return { dayId, dayNumber: day?.day_number || 0 };
        });
  
      if (selectedItems.length === 0) return;
  
      setIsLoading(true);
  
      const updates: { dayId: string; weekId: string }[] = [];
  
      // Collect selected days for updates
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
  
      const results = [];
  
      // Process each selected day update with a delay to prevent throttling
      for (let i = 0; i < updates.length; i++) {
        const { dayId } = updates[i];
        try {
          if (i > 0 && i % 3 === 0) {
            await new Promise(resolve => setTimeout(resolve, 300));
          }
  
          // Set focus to null for clearing it
          await updateDay(dayId, { focus: null }); 
          results.push({ dayId, success: true });
        } catch (error) {
          console.error(`Error clearing focus for day ${dayId}:`, error);
          results.push({ dayId, success: false, error });
        }
      }
  
      const successCount = results.filter(r => r.success).length;
      console.log(`Cleared focus for ${successCount} days successfully`);
  
      // Refresh the days data for all weeks or the active week
      if (applyToAllWeeks) {
        for (const weekId of Object.keys(daysMap)) {
          const freshDays = await getDays(weekId);
          setDaysMap(prev => ({
            ...prev,
            [weekId]: [...freshDays].sort((a, b) => a.day_number - b.day_number),
          }));
        }
      } else {
        const freshDays = await getDays(activeWeek!);
        setDaysMap(prev => ({
          ...prev,
          [activeWeek!]: [...freshDays].sort((a, b) => a.day_number - b.day_number),
        }));
      }
  
      setSelectedDays({});
      setBulkFocus('');
      setIsBulkEditing(false);
      setIsLoading(false);
      alert('Focus cleared successfully!');
    } catch (error) {
      setIsLoading(false);
      console.error('Error clearing focus:', error);
      alert('Some updates failed. Please try again with fewer days at once.');
    }
  };

  const toggleDay = (dayId: string) => {
    setSelectedDays(prev => ({
      ...prev,
      [dayId]: !prev[dayId]
    }));
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

            {/* Block Info Card Skeleton */}
            <div className="bg-white shadow rounded-lg p-6">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-4 animate-pulse"></div>
              
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <div className="h-3 bg-gray-200 rounded w-16 mb-2 animate-pulse"></div>
                  <div className="h-4 bg-gray-200 rounded w-24 animate-pulse"></div>
                </div>
                <div>
                  <div className="h-3 bg-gray-200 rounded w-16 mb-2 animate-pulse"></div>
                  <div className="h-4 bg-gray-200 rounded w-24 animate-pulse"></div>
                </div>
                <div>
                  <div className="h-3 bg-gray-200 rounded w-12 mb-2 animate-pulse"></div>
                  <div className="h-6 bg-gray-200 rounded w-20 animate-pulse"></div>
                </div>
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

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                  {[1, 2, 3, 4, 5, 6, 7].map((i) => (
                    <div key={i} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div className="h-5 bg-gray-200 rounded w-12 animate-pulse"></div>
                        <div className="h-5 bg-gray-200 rounded w-16 animate-pulse"></div>
                      </div>
                      <div className="h-3 bg-gray-200 rounded w-20 mb-2 animate-pulse"></div>
                      <div className="h-3 bg-gray-200 rounded w-full animate-pulse"></div>
                      <div className="mt-4 flex justify-between">
                        <div className="h-4 bg-gray-200 rounded w-16 animate-pulse"></div>
                        <div className="h-8 bg-gray-200 rounded w-24 animate-pulse"></div>
                      </div>
                    </div>
                  ))}
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

            <div className="bg-white shadow rounded-lg p-6">
              <p className="mb-4 text-gray-600">{block.description}</p>

              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Start Date</h3>
                  <p className="mt-1 text-sm text-gray-900">{formatDate(block.start_date)}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500">End Date</h3>
                  <p className="mt-1 text-sm text-gray-900">{formatDate(block.end_date)}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Status</h3>
                  <p className="mt-1 text-sm">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      block.status === 'active' 
                        ? 'bg-green-100 text-green-800' 
                        : block.status === 'completed'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {block.status.charAt(0).toUpperCase() + block.status.slice(1)}
                    </span>
                  </p>
                </div>
              </div>
            </div>

            {weeks.length > 0 ? (
              <div className="bg-white shadow rounded-lg overflow-hidden">
                <div className="border-b border-gray-200">
                  <nav className="flex overflow-x-auto">
                    {weeks.map((week) => (
                      <button
                        key={week.week_id}
                        onClick={() => setActiveWeek(week.week_id)}
                        className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${
                          activeWeek === week.week_id
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        }`}
                      >
                        Week {week.week_number}
                      </button>
                    ))}
                  </nav>
                </div>

                {activeWeek && daysMap[activeWeek] && (
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

                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                      {[...daysMap[activeWeek]]
                        .sort((a, b) => a.day_number - b.day_number)
                        .map((day) => (
                          <div
                            key={day.day_id}
                            className={`border rounded-lg p-4 hover:shadow-md transition-shadow ${
                              isBulkEditing && selectedDays[day.day_id] ? 'ring-2 ring-blue-500' : ''
                            }`}
                            onClick={isBulkEditing ? () => toggleDay(day.day_id) : undefined}
                            style={isBulkEditing ? { cursor: 'pointer' } : undefined}
                          >
                            <div className="flex justify-between items-start mb-2">
                              <h3 className="text-lg font-medium text-gray-900">Day {day.day_number}</h3>
                              {day.focus && <FocusTag focus={day.focus} />}
                            </div>
                            <p className="text-sm text-gray-500 mb-2">
                              {formatDate(day.date, {
                                weekday: 'short',
                                month: 'short',
                                day: 'numeric',
                              })}
                            </p>
                            {day.notes && <p className="mt-1 text-sm text-gray-500">{day.notes}</p>}

                            {!isBulkEditing && (
                              <div className="mt-4 flex justify-between">
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setEditingDay(day);
                                  }}
                                  className="text-sm text-blue-600 hover:text-blue-800"
                                >
                                  {day.focus ? 'Edit Focus' : 'Set Focus'}
                                </button>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    navigate(`/days/${day.day_id}?blockId=${blockId}`);
                                  }}
                                  className="px-3 py-2 text-sm text-blue-600 border border-blue-600 rounded-md hover:bg-blue-50"
                                >
                                  View Exercises
                                </button>
                              </div>
                            )}
                          </div>
                        ))}
                    </div>
                  </div>
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
                await updateDay(dayData.day_id, {
                  focus: dayData.focus,
                  notes: dayData.notes,
                });

                if (activeWeek) {
                  const updatedDays = await getDays(activeWeek);
                  setDaysMap(prev => ({
                    ...prev,
                    [activeWeek]: updatedDays,
                  }));
                }

                setEditingDay(null);
              } catch (error) {
                console.error('Error updating day:', error);
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
