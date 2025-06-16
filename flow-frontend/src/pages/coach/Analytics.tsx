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
import { useWeightUnit } from '../../contexts/UserContext';

interface AnalyticsProps {
  user: any;
  signOut: () => void;
}

const Analytics = ({ user, signOut }: AnalyticsProps) => {
  const [isLoading, setIsLoading] = useState(true);
  const [maxWeightData, setMaxWeightData] = useState<MaxWeightData[]>([]);
  const [volumeData, setVolumeData] = useState<VolumeData[]>([]);
  const [frequencyData, setFrequencyData] = useState<FrequencyData[]>([]);
  const [blocks, setBlocks] = useState<Block[]>([]);
  const [selectedAthleteId, setSelectedAthleteId] = useState<string>('');
  const [athletes, setAthletes] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  
  const { weightPreference, getDisplayUnit } = useWeightUnit();

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

  const loadAnalyticsData = async (athleteId: string) => {
    try {
      // Calculate date range - last 6 months for initial view
      const endDate = new Date().toISOString().split('T')[0];
      const startDate = new Date(Date.now() - 6 * 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];

      console.log('Loading analytics data for athlete:', athleteId);
      console.log('Date range:', startDate, 'to', endDate);

      console.log('Testing max weight progression...');
      try {
        // Test with default squat exercise type
        const maxWeight = await getMaxWeightProgression(athleteId, 'squat');
        console.log('Max weight progression result (squat):', maxWeight);
        setMaxWeightData(maxWeight);
      } catch (error) {
        console.error('Max weight progression error:', error);
        setMaxWeightData([]);
      }

      console.log('Testing volume data...');
      try {
        // Use monthly grouping (maps to backend's time_period=month)
        const volume = await getVolumeData(athleteId, 'monthly');
        console.log('Volume data result (monthly):', volume);
        setVolumeData(volume);
      } catch (error) {
        console.error('Volume data error:', error);
        setVolumeData([]);
      }

      console.log('Testing frequency analysis...');
      try {
        // Test with default squat exercise type
        const frequency = await getFrequencyAnalysis(athleteId, 'squat');
        console.log('Frequency analysis result (squat):', frequency);
        setFrequencyData(frequency);
      } catch (error) {
        console.error('Frequency analysis error:', error);
        setFrequencyData([]);
      }
    } catch (err) {
      console.error('Error loading analytics data:', err);
      throw err;
    }
  };

  // Helper function to format weight with user's preferred unit
  const formatWeight = (weight: number, exerciseType: string) => {
    const displayUnit = getDisplayUnit(exerciseType);
    return `${weight}${displayUnit}`;
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
  const hasData = maxWeightData.length > 0 || volumeData.length > 0 || frequencyData.length > 0;

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
                <p>Max Weight Data: {maxWeightData.length} entries</p>
                <p>Volume Data: {volumeData.length} entries</p>
                <p>Frequency Data: {frequencyData.length} entries</p>
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

              {/* Weight Preference */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-sm font-medium text-gray-500">Weight Display</h3>
                <p className="text-2xl font-semibold text-gray-900">
                  {weightPreference === 'auto' ? 'Auto (kg/lb)' : weightPreference.toUpperCase()}
                </p>
              </div>
            </div>

            {/* Charts Grid - Placeholder for Phase 3 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Max Weight Progression Chart */}
              {maxWeightData.length > 0 && (
                <div className="bg-white shadow rounded-lg p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">
                    Max Weight Progression
                  </h3>
                  <div className="h-64 flex items-center justify-center border-2 border-dashed border-gray-300 rounded">
                    <div className="text-center">
                      <p className="text-gray-500 mb-2">Chart Coming Soon</p>
                      <p className="text-sm text-gray-400">
                        {maxWeightData.length} data points available
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Volume Chart */}
              {volumeData.length > 0 && (
                <div className="bg-white shadow rounded-lg p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">
                    Training Volume
                  </h3>
                  <div className="h-64 flex items-center justify-center border-2 border-dashed border-gray-300 rounded">
                    <div className="text-center">
                      <p className="text-gray-500 mb-2">Chart Coming Soon</p>
                      <p className="text-sm text-gray-400">
                        {volumeData.length} weeks of data
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Frequency Analysis */}
              {frequencyData.length > 0 && (
                <div className="bg-white shadow rounded-lg p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">
                    Exercise Frequency
                  </h3>
                  <div className="h-64 flex items-center justify-center border-2 border-dashed border-gray-300 rounded">
                    <div className="text-center">
                      <p className="text-gray-500 mb-2">Chart Coming Soon</p>
                      <p className="text-sm text-gray-400">
                        {frequencyData.length} exercises tracked
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Recent Progress Summary */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Recent Progress
                </h3>
                <div className="space-y-3">
                  {maxWeightData.slice(-3).map((data, index) => (
                    <div key={index} className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">{data.exercise_name}</span>
                      <span className="text-sm font-medium text-gray-900">
                        {formatWeight(data.max_weight, data.exercise_type)}
                      </span>
                    </div>
                  ))}
                  {maxWeightData.length === 0 && (
                    <p className="text-sm text-gray-500">No recent max weights recorded</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Analytics;