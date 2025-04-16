import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import WorkoutForm from '../components/WorkoutForm';
import DaySelector from '../components/DaySelector';
import { getDay, getExercisesForDay, copyWorkout, getExercisesForWorkout, ApiError } from '../services/api';
import type { Day, Exercise } from '../services/api';
import { formatDate } from '../utils/dateUtils';
import FocusTag from '../components/FocusTag';
import { toast } from 'react-toastify';


interface DayDetailProps {
  user: any;
  signOut: () => void;
}

const DayDetail = ({ user, signOut }: DayDetailProps) => {
  const { dayId, blockId } = useParams<{ dayId: string; blockId: string }>();
  const [day, setDay] = useState<Day | null>(null);
  const [exercises, setExercises] = useState<Exercise[]>([]);
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
        
        // Try to load existing exercises
        try {
          const exercisesData = await getExercisesForDay(dayId);
          setExercises(exercisesData);
        } catch (err) {
          console.log('No exercises yet or error loading them');
          setExercises([]);
        }
      } catch (err) {
        console.error('Error loading day data:', err);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchDayData();
  }, [dayId]);

  const handleWorkoutSaved = async (workoutId: string) => {
    // Use the workoutId returned from saving the workout
    if (!workoutId) {
        console.error('No workout ID received');
        return;
      }
    
    try {
      // Call existing API endpoint
      const exercisesData = await getExercisesForWorkout(workoutId);
      setExercises(exercisesData);
      setShowWorkoutForm(false);
    } catch (err) {
      console.error('Error refreshing exercises:', err);
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
      if (error instanceof ApiError && error.statusCode === 409) {
        setCopyError('Target day already has a workout. Please delete it first.');
      } else {
        setCopyError('Failed to copy workout. Please try again.');
      }
    } finally {
      setIsCopying(false);
    }
  };
  
  const navigateBack = () => {
    if (blockId) {
      navigate(`/blocks/${blockId}`);
    } else {
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
            <button
              onClick={navigateBack}
              className="text-sm text-gray-600 hover:text-gray-800"
            >
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
            
            {exercises.length > 0 ? (
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-lg font-medium">Workout Plan</h2>
                  <div className="flex space-x-2">
                    <button
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
                    </button>
                  </div>
                </div>
                
                <ul className="divide-y">
                  {exercises.map((exercise) => (
                    <li key={exercise.exercise_id} className="py-3">
                      <h3 className="font-medium">{exercise.exercise_type}</h3>
                      <p className="text-sm text-gray-600">
                        {exercise.sets} sets × {exercise.reps} reps @ {exercise.weight} lbs
                        {exercise.rpe && ` @ RPE ${exercise.rpe}`}
                      </p>
                      {exercise.notes && (
                        <p className="mt-1 text-xs text-gray-500">{exercise.notes}</p>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            ) : showWorkoutForm ? (
              <WorkoutForm 
                dayId={dayId || ''} 
                onSave={handleWorkoutSaved} 
              />
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