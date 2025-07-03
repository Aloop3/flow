import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../../components/Layout';
import { 
  getMaxWeightProgression, 
  getVolumeData, 
  getFrequencyAnalysis,
  getBlocks,
  getCoachRelationships,
  getUser,
  get1RMAllTime,
  type MaxWeightData,
  type VolumeData,
  type FrequencyData,
  type Block
} from '../../services/api';
import { 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';

interface AnalyticsProps {
  user: any;
  signOut: () => void;
}

interface Athlete {
  athlete_id: string;
  name: string;
  relationship_id: string;
}

const Analytics = ({ user, signOut }: AnalyticsProps) => {
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingAthletes, setIsLoadingAthletes] = useState(false);
  const [maxWeightData, setMaxWeightData] = useState<{[key: string]: MaxWeightData[]}>({});
  const [volumeData, setVolumeData] = useState<VolumeData[]>([]);
  const [frequencyData, setFrequencyData] = useState<{[key: string]: FrequencyData[]}>({});
  const [blocks, setBlocks] = useState<Block[]>([]);
  const [selectedAthleteId, setSelectedAthleteId] = useState<string>('');
  const [athletes, setAthletes] = useState<Athlete[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [currentAthleteName, setCurrentAthleteName] = useState<string>('');
  const [volumeTimeRange, setVolumeTimeRange] = useState<'daily' | 'weekly' | 'monthly'>('monthly');
  const [sbdData, setSbdData] = useState<{
    exerciseType: string;
    exerciseName: string;
    latestData: { max_weight: number; unit: string } | null;
    weight: number;
    unit: string;
  }[]>([]);

  // Determine current athlete ID (self or selected athlete for coaches)
  const currentAthleteId = selectedAthleteId || user.user_id;

  // Load coach's athletes on component mount
  useEffect(() => {
    const loadAthletes = async () => {
      if (user.role !== 'coach') return;
      
      setIsLoadingAthletes(true);
      try {
        const relationships = await getCoachRelationships(user.user_id, 'active');
        console.log('Coach relationships loaded:', relationships);
        
        // Fetch athlete details for each relationship
        const athletesList = await Promise.all(
          relationships.map(async (rel) => {
            try {
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
        
        setAthletes(athletesList);
        console.log('Athletes loaded for coach:', athletesList);
      } catch (error) {
        console.error('Error loading coach athletes:', error);
        setAthletes([]);
      } finally {
        setIsLoadingAthletes(false);
      }
    };

    loadAthletes();
  }, [user.role, user.user_id]);

  // Main analytics loading effect - triggers on athlete changes
  useEffect(() => {
    const initializeAnalytics = async () => {
      setIsLoading(true);
      setError(null);

      try {
        // Set current athlete name for display
        if (selectedAthleteId) {
          const selectedAthlete = athletes.find(a => a.athlete_id === selectedAthleteId);
          setCurrentAthleteName(selectedAthlete?.name || 'Selected Athlete');
        } else {
          setCurrentAthleteName(user.role === 'coach' ? 'My Analytics' : '');
        }

        // Load blocks for date range context
        const blocksData = await getBlocks(currentAthleteId);
        setBlocks(blocksData || []);

        // Load analytics data
        await loadAnalyticsData(currentAthleteId);

      } catch (err) {
        console.error('Error loading analytics:', err);
        
        // Handle permission errors specifically
        if (err instanceof Error && err.message.includes('403')) {
          setError('You do not have permission to view this athlete\'s analytics.');
        } else if (err instanceof Error && err.message.includes('401')) {
          setError('Authentication required. Please log in again.');
        } else {
          setError('Failed to load analytics data. Please try again.');
        }
      } finally {
        setIsLoading(false);
      }
    };

    initializeAnalytics();
  }, [currentAthleteId, user.role, user.user_id, selectedAthleteId, athletes]);

  useEffect(() => {
    const reloadVolumeData = async () => {
      if (!currentAthleteId) return;
      
      try {
        console.log(`Reloading volume data for ${volumeTimeRange} view`);
        const callStartTime = performance.now();
        
        const volumeResult = await getVolumeData(
          currentAthleteId, 
          volumeTimeRange === 'daily' ? 'weekly' : volumeTimeRange
        );
        
        const callEndTime = performance.now();
        console.log(`Volume data reloaded in ${callEndTime - callStartTime}ms`);
        
        setVolumeData(volumeResult);
      } catch (error) {
        console.error('Error reloading volume data:', error);
      }
    };

    reloadVolumeData();
  }, [volumeTimeRange, currentAthleteId]); // Only depends on volume time range and athlete

  useEffect(() => {
  console.log('🔍 1RM useEffect triggered. currentAthleteId:', currentAthleteId);
  
  const load1RMData = async () => {
    if (!currentAthleteId) {
      console.log('❌ No currentAthleteId, skipping 1RM load');
      return;
    }
    
    console.log('🚀 Starting 1RM data load for:', currentAthleteId);
    
    try {
      const data = await Promise.all(['squat', 'bench press', 'deadlift'].map(async exerciseType => {
        console.log('📡 Calling getTime for:', exerciseType);
        const response = await get1RMAllTime(currentAthleteId, exerciseType);
        const weight = response.all_time_max_weight || 0;
        const unit = 'kg';

        const exerciseName = capitalizeExerciseName(exerciseType);
        
        return {
          exerciseType,
          exerciseName,
          latestData: weight > 0 ? { max_weight: weight, unit } : null,
          weight,
          unit
        };
      }));
      
      console.log('✅ 1RM data loaded:', data);
      setSbdData(data);
    } catch (error) {
      console.error('❌ Error loading 1RM data:', error);
    }
  };
  
  load1RMData();
}, [currentAthleteId]);
  // Handle athlete selection changes
  const handleAthleteChange = (athleteId: string) => {
    console.log('Athlete selection changed to:', athleteId);
    setSelectedAthleteId(athleteId);
    // Analytics will reload automatically via useEffect dependency
  };

  const SBD_EXERCISES = ['squat', 'bench press', 'deadlift'] as const;

  const loadAnalyticsData = async (athleteId: string) => {
    try {
      console.log('Loading analytics data for athlete:', athleteId);

      // Start timing
      const overallStartTime = performance.now();

      // Create all API calls in parallel - 7 calls total
      const apiCalls = [
        // Max weight progression calls (3 exercises)
        ...SBD_EXERCISES.map(exerciseType => {
          const callStartTime = performance.now();
          return getMaxWeightProgression(athleteId, exerciseType)
            .then(data => {
              const callEndTime = performance.now();
              console.log(`Max weight ${exerciseType} completed in ${callEndTime - callStartTime}ms`);
              return { type: 'maxWeight', exerciseType, data };
            })
            .catch(error => {
              const callEndTime = performance.now();
              console.error(`Max weight error for ${exerciseType} after ${callEndTime - callStartTime}ms:`, error);
              
              // Re-throw permission errors to be handled by parent
              if (error.message?.includes('403') || error.message?.includes('401')) {
                throw error;
              }
              return { type: 'maxWeight', exerciseType, data: [] };
            });
        }),
        
        // Frequency analysis calls (3 exercises)
        ...SBD_EXERCISES.map(exerciseType => {
          const callStartTime = performance.now();
          return getFrequencyAnalysis(athleteId, exerciseType)
            .then(data => {
              const callEndTime = performance.now();
              console.log(`Frequency ${exerciseType} completed in ${callEndTime - callStartTime}ms`);
              return { type: 'frequency', exerciseType, data };
            })
            .catch(error => {
              const callEndTime = performance.now();
              console.error(`Frequency error for ${exerciseType} after ${callEndTime - callStartTime}ms:`, error);
              
              // Re-throw permission errors to be handled by parent
              if (error.message?.includes('403') || error.message?.includes('401')) {
                throw error;
              }
              return { type: 'frequency', exerciseType, data: [] };
            });
        }),
        
        // Volume data call (1 call)
        (() => {
          const callStartTime = performance.now();
          return getVolumeData(athleteId, 'monthly')
            .then(data => {
              const callEndTime = performance.now();
              console.log(`Volume data completed in ${callEndTime - callStartTime}ms`);
              return { type: 'volume', data };
            })
            .catch(error => {
              const callEndTime = performance.now();
              console.error(`Volume data error after ${callEndTime - callStartTime}ms:`, error);
              
              // Re-throw permission errors to be handled by parent
              if (error.message?.includes('403') || error.message?.includes('401')) {
                throw error;
              }
              return { type: 'volume', data: [] };
            });
        })()
      ];

      console.log(`Starting ${apiCalls.length} parallel API calls...`);
      
      // Execute all calls in parallel
      const results = await Promise.all(apiCalls);
      
      const overallEndTime = performance.now();
      const totalTime = overallEndTime - overallStartTime;
      console.log(`🚀 ALL PARALLEL API CALLS COMPLETED IN ${totalTime}ms (${(totalTime/1000).toFixed(2)}s)`);
      console.log(`Performance improvement: Was ~9700ms, now ${totalTime}ms = ${((9700-totalTime)/9700*100).toFixed(1)}% faster`);
      
      // Process results
      const maxWeightResults: {[key: string]: MaxWeightData[]} = {};
      const frequencyResults: {[key: string]: FrequencyData[]} = {};
      let volumeResult: VolumeData[] = [];
      
      results.forEach(result => {
        if (result.type === 'maxWeight' && 'exerciseType' in result) {
          maxWeightResults[result.exerciseType] = result.data as MaxWeightData[];
          console.log(`Max weight result (${result.exerciseType}):`, result.data);
        } else if (result.type === 'frequency' && 'exerciseType' in result) {
          frequencyResults[result.exerciseType] = result.data as FrequencyData[];
          console.log(`Frequency result (${result.exerciseType}):`, result.data);
        } else if (result.type === 'volume') {
          volumeResult = result.data as VolumeData[];
          console.log('Volume data result (monthly):', result.data);
        }
      });

      // Update state
      setMaxWeightData(maxWeightResults);
      setFrequencyData(frequencyResults);
      setVolumeData(volumeResult);

      console.log('Analytics data loaded successfully with parallel calls');
      
    } catch (err) {
      console.error('Error loading analytics data:', err);
      throw err;
    }
  };

  // Helper function to format weight - backend already handles unit conversion
  const formatWeight = (weight: number, unit?: string) => {
    // Use the unit from the backend response, fallback to 'kg' for SBD
    return `${weight}${unit || 'kg'}`;
  };

  // Helper function to capitalize exercise names
  const capitalizeExerciseName = (exerciseType: string): string => {
    return exerciseType
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

    // Loading skeleton component
  const LoadingSkeleton = () => (
    <div className="animate-pulse space-y-6">
      <div className="h-8 bg-gray-200 rounded w-1/3"></div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="h-64 bg-gray-200 rounded-lg"></div>
        <div className="h-64 bg-gray-200 rounded-lg"></div>
        <div className="h-64 bg-gray-200 rounded-lg"></div>
        <div className="h-64 bg-gray-200 rounded-lg"></div>
      </div>
    </div>
  );

  // Error state component
  const ErrorState = () => (
    <div className="text-center py-12">
      <div className="text-red-600 mb-4">
        <svg className="w-16 h-16 mx-auto" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
      </div>
      <h3 className="text-lg font-medium text-gray-900 mb-2">Unable to Load Analytics</h3>
      <p className="text-gray-500 mb-4">{error}</p>
      {error?.includes('permission') && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4 max-w-md mx-auto">
          <p className="text-sm text-yellow-800">
            This athlete's data is not accessible. Please ensure you have an active coach-athlete relationship.
          </p>
        </div>
      )}
      <div className="space-x-2">
        <button
          onClick={() => {
            setSelectedAthleteId('');
            setError(null);
          }}
          className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
        >
          View My Analytics
        </button>
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Try Again
        </button>
      </div>
    </div>
  );

  // Empty state component
  const EmptyState = () => (
    <div className="text-center py-12">
      <div className="text-gray-400 mb-4">
        <svg className="w-16 h-16 mx-auto" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
        </svg>
      </div>
      <h3 className="text-lg font-medium text-gray-900 mb-2">No Analytics Data Available</h3>
      <p className="text-gray-500 mb-4">
        {selectedAthleteId ? 'This athlete hasn\'t logged any workouts yet.' : 'Start logging workouts to see your progress analytics.'}
      </p>
      <Link
        to="/blocks"
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        View Programs
      </Link>
    </div>
  );

  // Check if we have any data
  const hasData = Object.values(maxWeightData).some(data => data.length > 0) || 
                  volumeData.length > 0 || 
                  Object.values(frequencyData).some(data => data.length > 0);

  return (
    <Layout user={user} signOut={signOut}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Analytics {currentAthleteName && `- ${currentAthleteName}`}
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              {selectedAthleteId ? 'Track athlete progress and training insights' : 'Track your progress and training insights'}
            </p>
          </div>
          <div className="mt-4 sm:mt-0">
            <Link
              to="/"
              className="text-sm text-gray-600 hover:text-gray-800"
            >
              ← Back to Dashboard
            </Link>
          </div>
        </div>

        {/* Coach athlete selector */}
        {user.role === 'coach' && (
          <div className="bg-white shadow rounded-lg p-4">
            <label htmlFor="athlete-select" className="block text-sm font-medium text-gray-700 mb-2">
              Select Athlete
            </label>
            <div className="flex items-center space-x-2">
              <select
                id="athlete-select"
                value={selectedAthleteId}
                onChange={(e) => handleAthleteChange(e.target.value)}
                disabled={isLoadingAthletes}
                className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md disabled:bg-gray-100"
              >
                <option value="">View My Analytics</option>
                {athletes.map((athlete) => (
                  <option key={athlete.athlete_id} value={athlete.athlete_id}>
                    {athlete.name}
                  </option>
                ))}
              </select>
              {isLoadingAthletes && (
                <div className="text-sm text-gray-500">Loading athletes...</div>
              )}
            </div>
            {athletes.length === 0 && !isLoadingAthletes && (
              <p className="mt-2 text-sm text-gray-500">
                No active athletes found. Athletes will appear here once they accept your invitation.
              </p>
            )}
          </div>
        )}

        {/* Content */}
        {isLoading ? (
          <LoadingSkeleton />
        ) : error ? (
          <ErrorState />
        ) : !hasData ? (
          <div>
            {/* Debug info */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
              <h4 className="text-sm font-medium text-yellow-800 mb-2">Debug Information</h4>
              <div className="text-xs text-yellow-700 space-y-1">
                <p>User ID: {user.user_id}</p>
                <p>Current Athlete ID: {currentAthleteId}</p>
                <p>Selected Athlete: {selectedAthleteId || 'None (viewing own)'}</p>
                <p>Max Weight Data: {Object.values(maxWeightData).flat().length} total entries</p>
                <p>Volume Data: {volumeData.length} entries</p>
                <p>Frequency Data: {Object.values(frequencyData).flat().length} total entries</p>
                <p>Blocks: {blocks.length} total</p>
                <p>Athletes Available: {athletes.length}</p>
                <p>Check browser console for API responses</p>
              </div>
            </div>
            <EmptyState />
          </div>
        ) : (
          <div className="space-y-8">
            {/* Quick Stats Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Total Programs */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-sm font-medium text-gray-500">Total Programs</h3>
                <p className="text-2xl font-semibold text-gray-900">{blocks.length}</p>
              </div>

              {/* Active Program */}
              {blocks.find(b => b.status === 'active') && (
                <div className="bg-white shadow rounded-lg p-6">
                  <h3 className="text-sm font-medium text-gray-500">Active Program</h3>
                  <p className="text-2xl font-semibold text-gray-900 truncate">
                    {blocks.find(b => b.status === 'active')?.title}
                  </p>
                </div>
              )}
            </div>

            {/* 1RM with Total */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                1RM
              </h3>
              <div className="space-y-2">
                {(() => {
                  
                  // Calculate total (only if all three lifts have data)
                  const allHaveData = sbdData.every(data => data.latestData);
                  const total = allHaveData ? sbdData.reduce((sum, data) => sum + data.weight, 0) : 0;
                  const totalUnit = sbdData.find(data => data.latestData)?.unit || 'kg';
                  
                  return (
                    <>
                      {/* Individual 1RMs */}
                      {sbdData.map(({ exerciseType, exerciseName, latestData, weight, unit }) => (
                        latestData ? (
                          <div key={exerciseType} className="flex justify-between items-center gap-4">
                            <span className="text-sm text-gray-600 flex-shrink-0">{exerciseName}</span>
                            <span className="text-sm font-medium text-gray-900 text-right">
                              {formatWeight(weight, unit)}
                            </span>
                          </div>
                        ) : (
                          <div key={exerciseType} className="flex justify-between items-center gap-4">
                            <span className="text-sm text-gray-400 flex-shrink-0">{exerciseName}</span>
                            <span className="text-sm text-gray-400 text-right">No data</span>
                          </div>
                        )
                      ))}
                      
                      {/* Total Row */}
                      {allHaveData && (
                        <>
                          <div className="border-t border-gray-200 my-2"></div>
                          <div className="flex justify-between items-center gap-4">
                            <span className="text-sm font-semibold text-gray-900 flex-shrink-0">Total</span>
                            <span className="text-sm font-bold text-blue-600 text-right">
                              {formatWeight(total, totalUnit)}
                            </span>
                          </div>
                        </>
                      )}
                    </>
                  );
                })()}
              </div>
            </div>

            {/* Charts Grid - SBD Exercise Analytics */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Max Weight Progression Charts - One for each SBD exercise */}
              {['squat', 'bench press', 'deadlift'].map(exerciseType => {
                const exerciseData = maxWeightData[exerciseType] || [];
                const exerciseName = capitalizeExerciseName(exerciseType);
                
                // Format data for Recharts
                const chartData = exerciseData.map(item => ({
                  date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                  weight: item.max_weight,
                  fullDate: item.date,
                  unit: item.unit
                }));
                
                return exerciseData.length > 0 ? (
                  <div key={`max-weight-${exerciseType}`} className="bg-white shadow rounded-lg p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">
                      {exerciseName} Max Weight Progression
                    </h3>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                          <XAxis 
                            dataKey="date" 
                            tick={{ fontSize: 12 }}
                            stroke="#6b7280"
                          />
                          <YAxis 
                            tick={{ fontSize: 12 }}
                            stroke="#6b7280"
                            label={{ 
                              value: `Weight (${chartData[0]?.unit || 'kg'})`, 
                              angle: -90, 
                              position: 'insideLeft',
                              style: { textAnchor: 'middle' }
                            }}
                          />
                          <Tooltip 
                            formatter={(value: any) => [`${value}${chartData[0]?.unit || 'kg'}`, 'Max Weight']}
                            labelFormatter={(label: string) => `Date: ${label}`}
                            contentStyle={{ 
                              backgroundColor: '#fff', 
                              border: '1px solid #e5e7eb',
                              borderRadius: '6px',
                              fontSize: '12px'
                            }}
                          />
                          <Line 
                            type="monotone" 
                            dataKey="weight" 
                            stroke="#3b82f6" 
                            strokeWidth={2}
                            dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                            activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2 }}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                ) : null;
              })}

              {/* Volume Chart with Toggle */}
              {volumeData.length > 0 && (
                <div className="bg-white shadow rounded-lg p-6">
                  {/* Toggle Header */}
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-medium text-gray-900">
                      Training Volume
                    </h3>
                    
                    {/* Time Range Toggle Buttons */}
                    <div className="flex bg-gray-100 rounded-lg p-1">
                      {(['daily', 'weekly', 'monthly'] as const).map((range) => (
                        <button
                          key={range}
                          onClick={() => setVolumeTimeRange(range)}
                          className={`px-3 py-1 text-sm font-medium rounded-md transition-colors duration-200 ${
                            volumeTimeRange === range
                              ? 'bg-white text-blue-600 shadow-sm'
                              : 'text-gray-600 hover:text-gray-900'
                          }`}
                        >
                          {range.charAt(0).toUpperCase() + range.slice(1)}
                        </button>
                      ))}
                    </div>
                  </div>
                  
                  {/* Volume Chart with Dynamic Processing */}
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart 
                        data={(() => {
                          console.log(`Volume data for ${volumeTimeRange} chart:`, volumeData);
                          
                          if (volumeTimeRange === 'daily') {
                            // Daily: Show each date as-is (last 7 days from backend)
                            return volumeData
                              .map(item => ({
                                date: new Date(item.date).toLocaleDateString('en-US', { 
                                  month: 'short', 
                                  day: 'numeric' 
                                }),
                                volume: (item as any).volume || item.total_volume || 0,
                                fullDate: item.date
                              }))
                              .sort((a, b) => new Date(a.fullDate).getTime() - new Date(b.fullDate).getTime());
                          
                          } else if (volumeTimeRange === 'weekly') {
                            // Weekly: Group by week (last 30 days from backend)
                            const weeklyData = volumeData.reduce((acc, item) => {
                              const date = new Date(item.date);
                              const weekStart = new Date(date);
                              weekStart.setDate(date.getDate() - date.getDay()); // Start of week (Sunday)
                              const weekKey = weekStart.toLocaleDateString('en-US', { 
                                month: 'short', 
                                day: 'numeric' 
                              });
                              
                              const volume = (item as any).volume || item.total_volume || 0;
                              
                              if (acc[weekKey]) {
                                acc[weekKey].volume += volume;
                              } else {
                                acc[weekKey] = {
                                  date: weekKey,
                                  volume: volume,
                                  weekStart: weekStart.getTime()
                                };
                              }
                              return acc;
                            }, {} as Record<string, any>);
                            
                            return Object.values(weeklyData)
                              .sort((a: any, b: any) => a.weekStart - b.weekStart);
                          
                          } else {
                            // Monthly: Group by month (existing logic)
                            const groupedData = volumeData.reduce((acc, item) => {
                              const dateKey = new Date(item.date).toLocaleDateString('en-US', { 
                                month: 'short', 
                                year: '2-digit' 
                              });
                              const volume = (item as any).volume || item.total_volume || 0;
                              
                              if (acc[dateKey]) {
                                acc[dateKey].volume += volume;
                              } else {
                                acc[dateKey] = {
                                  date: dateKey,
                                  volume: volume,
                                  fullDate: item.date
                                };
                              }
                              return acc;
                            }, {} as Record<string, any>);
                            
                            return Object.values(groupedData)
                              .sort((a: any, b: any) => new Date(a.fullDate).getTime() - new Date(b.fullDate).getTime());
                          }
                        })()} 
                        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                        <XAxis 
                          dataKey="date" 
                          tick={{ fontSize: 12 }}
                          stroke="#6b7280"
                        />
                        <YAxis 
                          tick={{ fontSize: 12 }}
                          stroke="#6b7280"
                          label={{ 
                            value: 'Volume (kg)', 
                            angle: -90, 
                            position: 'insideLeft',
                            style: { textAnchor: 'middle' }
                          }}
                        />
                        <Tooltip 
                          formatter={(value: any) => [`${value.toLocaleString()}kg`, 'Total Volume']}
                          labelFormatter={(label: string) => `Period: ${label}`}
                          contentStyle={{ 
                            backgroundColor: '#fff', 
                            border: '1px solid #e5e7eb',
                            borderRadius: '6px',
                            fontSize: '12px'
                          }}
                        />
                        <Bar 
                          dataKey="volume" 
                          fill="#10b981"
                          radius={[2, 2, 0, 0]}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}

              {/* Frequency Analysis - One for each SBD exercise */}
              {['squat', 'bench press', 'deadlift'].map(exerciseType => {
                const exerciseData = frequencyData[exerciseType] || [];
                const exerciseName = capitalizeExerciseName(exerciseType);
                
                // Format frequency data with meaningful time labels
                const chartData = exerciseData.map((item, index) => {
                  // Create meaningful labels based on the exercise data
                  const date = new Date();
                  date.setMonth(date.getMonth() - (exerciseData.length - index - 1));
                  
                  return {
                    month: date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' }),
                    weekly: parseFloat((item.frequency_per_week || 0).toFixed(1)),
                    monthly: parseFloat((item.frequency_per_month || 0).toFixed(1)),
                    sessions: item.total_sessions || 0
                  };
                });
                
                return exerciseData.length > 0 ? (
                  <div key={`frequency-${exerciseType}`} className="bg-white shadow rounded-lg p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">
                      {exerciseName} Training Frequency
                    </h3>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                          <XAxis 
                            dataKey="month" 
                            tick={{ fontSize: 12 }}
                            stroke="#6b7280"
                          />
                          <YAxis 
                            tick={{ fontSize: 12 }}
                            stroke="#6b7280"
                            label={{ 
                              value: 'Sessions/Week', 
                              angle: -90, 
                              position: 'insideLeft',
                              style: { textAnchor: 'middle' }
                            }}
                          />
                          <Tooltip 
                            formatter={(value: any, name: string) => {
                              const labels = {
                                weekly: 'Sessions/Week',
                                monthly: 'Sessions/Month', 
                                sessions: 'Total Sessions'
                              };
                              return [value, labels[name as keyof typeof labels] || name];
                            }}
                            labelFormatter={(label: string) => `Month: ${label}`}
                            contentStyle={{ 
                              backgroundColor: '#fff', 
                              border: '1px solid #e5e7eb',
                              borderRadius: '6px',
                              fontSize: '12px'
                            }}
                          />
                          <Area 
                            type="monotone" 
                            dataKey="weekly" 
                            stackId="1"
                            stroke="#f59e0b" 
                            fill="#f59e0b"
                            fillOpacity={0.6}
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                ) : null;
              })}
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Analytics;