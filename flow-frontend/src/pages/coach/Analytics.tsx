import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../../components/Layout';
import { 
  getMaxWeightProgression, 
  getVolumeData, 
  getFrequencyAnalysis,
  getBlocks,
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

const Analytics = ({ user, signOut }: AnalyticsProps) => {
  const [isLoading, setIsLoading] = useState(true);
  const [maxWeightData, setMaxWeightData] = useState<{[key: string]: MaxWeightData[]}>({});
  const [volumeData, setVolumeData] = useState<VolumeData[]>([]);
  const [frequencyData, setFrequencyData] = useState<{[key: string]: FrequencyData[]}>({});
  const [blocks, setBlocks] = useState<Block[]>([]);
  const [selectedAthleteId, setSelectedAthleteId] = useState<string>('');
  const [athletes, setAthletes] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Determine current athlete ID (self or selected athlete for coaches)
  const currentAthleteId = selectedAthleteId || user.user_id;

  useEffect(() => {
    const initializeAnalytics = async () => {
      setIsLoading(true);
      setError(null);

      try {
        // For coaches, load athlete list for selection
        if (user.role === 'coach') {
          // TODO: Load coach's athletes when we implement athlete selection
          // For now, just use coach's own data
          setAthletes([]);
        }

        // Load blocks for date range context
        const blocksData = await getBlocks(currentAthleteId);
        setBlocks(blocksData || []);

        // Load analytics data
        await loadAnalyticsData(currentAthleteId);

      } catch (err) {
        console.error('Error loading analytics:', err);
        setError('Failed to load analytics data. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    initializeAnalytics();
  }, [currentAthleteId, user.role, user.user_id]);

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
      <button
        onClick={() => window.location.reload()}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Try Again
      </button>
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
        Start logging workouts to see your progress analytics.
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
            <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
            <p className="mt-1 text-sm text-gray-500">
              Track your progress and training insights
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

        {/* Coach athlete selector - placeholder for future implementation */}
        {user.role === 'coach' && athletes.length > 0 && (
          <div className="bg-white shadow rounded-lg p-4">
            <label htmlFor="athlete-select" className="block text-sm font-medium text-gray-700 mb-2">
              Select Athlete
            </label>
            <select
              id="athlete-select"
              value={selectedAthleteId}
              onChange={(e) => setSelectedAthleteId(e.target.value)}
              className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            >
              <option value="">View My Analytics</option>
              {athletes.map((athlete) => (
                <option key={athlete.athlete_id} value={athlete.athlete_id}>
                  {athlete.name}
                </option>
              ))}
            </select>
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
                <p>Max Weight Data: {Object.values(maxWeightData).flat().length} total entries</p>
                <p>Volume Data: {volumeData.length} entries</p>
                <p>Frequency Data: {Object.values(frequencyData).flat().length} total entries</p>
                <p>Blocks: {blocks.length} total</p>
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

            {/* 1RM - Now appears before charts */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                1RM
              </h3>
              <div className="space-y-2">
                {['squat', 'bench press', 'deadlift'].map(exerciseType => {
                  const exerciseData = maxWeightData[exerciseType] || [];
                  const latestData = exerciseData[exerciseData.length - 1];
                  const exerciseName = capitalizeExerciseName(exerciseType);
                  
                  return latestData ? (
                    <div key={exerciseType} className="flex justify-between items-center gap-4">
                      <span className="text-sm text-gray-600 flex-shrink-0">{exerciseName}</span>
                      <span className="text-sm font-medium text-gray-900 text-right">
                        {formatWeight(latestData.max_weight, latestData.unit)}
                      </span>
                    </div>
                  ) : (
                    <div key={exerciseType} className="flex justify-between items-center gap-4">
                      <span className="text-sm text-gray-400 flex-shrink-0">{exerciseName}</span>
                      <span className="text-sm text-gray-400 text-right">No data</span>
                    </div>
                  );
                })}
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

              {/* Volume Chart */}
              {volumeData.length > 0 && (
                <div className="bg-white shadow rounded-lg p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">
                    Monthly Training Volume
                  </h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart 
                        data={(() => {
                          console.log('Volume data for chart:', volumeData);
                          // Group by date and sum volumes to handle duplicate dates
                          const groupedData = volumeData.reduce((acc, item) => {
                            console.log('Processing volume item:', item);
                            const dateKey = new Date(item.date).toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
                            // Backend returns 'volume' not 'total_volume'
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
                          
                          const result = Object.values(groupedData).sort((a: any, b: any) => 
                            new Date(a.fullDate).getTime() - new Date(b.fullDate).getTime()
                          );
                          console.log('Chart data result:', result);
                          return result;
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