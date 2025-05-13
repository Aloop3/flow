import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import WorkoutForm from '../components/WorkoutForm';
import DaySelector from '../components/DaySelector';
import { getDay, getWorkoutByDay, copyWorkout, ApiError } from '../services/api';
import type { Day, Workout } from '../services/api';
import { formatDate } from '../utils/dateUtils';
import FocusTag from '../components/FocusTag';
import { toast } from 'react-toastify';
import ExerciseList from '../components/ExerciseList';

interface DayDetailProps {
  user: any;
  signOut: () => void;
}

const DayDetail = ({ user, signOut }: DayDetailProps) => {
  const { dayId, blockId } = useParams<{ dayId: string; blockId: string }>();
  const [day, setDay] = useState<Day | null>(null);
  const [workout, setWorkout] = useState<Workout | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showWorkoutForm, setShowWorkoutForm] = useState(false);
  const [showCopyModal, setShowCopyModal] = useState(false);
  const [isCopying, setIsCopying] = useState(false);
  const [copyError, setCopyError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!dayId) return;

    const fetchDayData = async () => {
      setIsLoading(true);
      try {
        const dayData = await getDay(dayId);
        setDay(dayData);

        // Try to load existing workout with consistent ID property
        try {
          // Ensure we're using the correct user ID property consistently
          const workoutData = await getWorkoutByDay(user.user_id, dayId);
          setWorkout(workoutData);
        } catch (err) {
          console.log('No workout yet or error loading it');
          setWorkout(null);
        }
      } catch (err) {
        console.error('Error loading day data:', err);
        toast.error('Error loading day data');
      } finally {
        setIsLoading(false);
      }
    };

    fetchDayData();
  }, [dayId, user.user_id]);

  const handleWorkoutSaved = async (workoutId: string) => {
    // Refresh the workout data after saving
    if (!workoutId || !dayId) {
      console.error('No workout ID or day ID');
      return;
    }

    try {
      const workoutData = await getWorkoutByDay(user.user_id, dayId);
      setWorkout(workoutData);
      setShowWorkoutForm(false);
      toast.success('Workout saved successfully!');
    } catch (err) {
      console.error('Error refreshing workout:', err);
      toast.error('Error loading workout after save');
    }
  };

  const refreshWorkoutData = async () => {
    if (!dayId || !user.user_id) {
      return;
    }

    try {
      console.log('Refreshing workout data');
      const workoutData = await getWorkoutByDay(user.user_id, dayId);

      if (workoutData) {
        console.log('Updated workout data:', workoutData);
        setWorkout(workoutData);
      }
    } catch (err) {
      console.error('Error refreshing workout data:', err);
    }
  };

  const handleCopyWorkout = async (targetDayId: string) => {
    if (!dayId) return;

    setIsCopying(true);
    setCopyError(null);

    try {
      console.log('Starting workout copy from day', dayId, 'to day', targetDayId);
      await copyWorkout(dayId, targetDayId);

      // Show success message and close modal
      toast.success('Workout copied successfully!');
      setShowCopyModal(false);
    } catch (error) {
      console.error('Error copying workout:', error);

      // Display specific error message if available from API
      if (ApiError.isConflict(error)) {
        setCopyError('Target day already has a workout. Please delete it first.');
      } else {
        setCopyError('Failed to copy workout. Please try again.');
      }
    } finally {
      setIsCopying(false);
    }
  };

  const navigateBack = () => {
    const urlParams = new URLSearchParams(window.location.search);
    const blockId = urlParams.get('blockId'); // Retrieve blockId from query params

    if (blockId) {
      // Navigate to the path including the blockId
      navigate(`/blocks/${blockId}`);
    } else {
      // If no blockId, navigate to the general blocks path
      navigate('/blocks');
    }
  };

  return (
    <Layout user={user} signOut={signOut}>
      {isLoading ? (
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
        </div>
      ) : day ? (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">
              Day {day.day_number} - {formatDate(day.date)}
            </h1>
            <button onClick={navigateBack} className="text-sm text-gray-600 hover:text-gray-800">
              Back to Block
            </button>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            {day.focus ? (
              <div className="mb-4">
                <h2 className="text-sm font-medium text-gray-500">Focus</h2>
                <div className="mt-1">
                  <FocusTag focus={day.focus} size="lg" />
                </div>
              </div>
            ) : (
              <div className="mb-4">
                <h2 className="text-sm font-medium text-gray-500">Focus</h2>
                <p className="mt-1 text-gray-400 italic">No focus set</p>
              </div>
            )}

            {day.notes ? (
              <div>
                <h2 className="text-sm font-medium text-gray-500">Notes</h2>
                <p className="mt-1">{day.notes}</p>
              </div>
            ) : (
              <div>
                <h2 className="text-sm font-medium text-gray-500">Notes</h2>
                <p className="mt-1 text-gray-400 italic">No notes</p>
              </div>
            )}
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            {copyError && (
              <div className="mb-4 bg-red-50 border border-red-200 text-red-700 rounded p-3">
                {copyError}
              </div>
            )}

            {workout ? (
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-lg font-medium">
                    Workout Plan
                    <span className="ml-2 text-sm text-gray-500">{/* ({workout.status}) */}</span>
                  </h2>
                  <div className="flex space-x-2">
                    {/* <button
                      onClick={() => setShowCopyModal(true)}
                      disabled={isCopying}
                      className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 disabled:opacity-50"
                    >
                      {isCopying ? 'Copying...' : 'Copy to Another Day'}
                    </button>
                    <button
                      onClick={() => setShowWorkoutForm(true)}
                      className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                    >
                      Edit Workout
                    </button> */}
                  </div>
                </div>

                <ExerciseList
                  exercises={workout.exercises}
                  onExerciseComplete={refreshWorkoutData}
                  readOnly={false}
                />
              </div>
            ) : showWorkoutForm ? (
              <WorkoutForm dayId={dayId || ''} onSave={handleWorkoutSaved} />
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500 mb-4">No workout planned yet</p>
                <button
                  onClick={() => setShowWorkoutForm(true)}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Create Workout
                </button>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <p className="text-gray-500">Day not found</p>
          <button
            onClick={navigateBack}
            className="mt-4 px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
          >
            Back to Block
          </button>
        </div>
      )}

      {/* Day Selector Modal for copying workout */}
      <DaySelector
        isOpen={showCopyModal}
        onClose={() => setShowCopyModal(false)}
        onDaySelected={handleCopyWorkout}
        blockId={blockId || ''}
        title="Copy Workout to Day"
        excludeDayId={dayId}
      />
    </Layout>
  );
};

export default DayDetail;
