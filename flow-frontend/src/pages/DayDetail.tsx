import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import Layout from '../components/Layout';
import WorkoutForm from '../components/WorkoutForm';
import DaySelector from '../components/DaySelector';
import { getDay, getWorkoutByDay, getBlock, copyWorkout, ApiError } from '../services/api';
import type { Day, Workout } from '../services/api';
import { formatDate } from '../utils/dateUtils';
import FocusTag from '../components/FocusTag';
import { toast } from 'react-toastify';
import ExerciseList from '../components/ExerciseList';
import { updateDay } from '../services/api';
import WorkoutTimer from '../components/WorkoutTimer';
import WorkoutSummary from '../components/WorkoutSummary';
import WorkoutCompletion from '../components/WorkoutCompletion';


interface DayDetailProps {
  user: any;
  signOut: () => void;
}

const DayDetail = ({ user, signOut }: DayDetailProps) => {
  const { dayId } = useParams<{ dayId: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Extract blockId from query parameters
  const queryParams = new URLSearchParams(location.search);
  const blockId = queryParams.get('blockId');
  
  const [day, setDay] = useState<Day | null>(null);
  const [workout, setWorkout] = useState<Workout | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showWorkoutForm, setShowWorkoutForm] = useState(false);
  const [showCopyModal, setShowCopyModal] = useState(false);
  const [copyError, setCopyError] = useState<string | null>(null);
  const [athleteId, setAthleteId] = useState<string | undefined>(undefined);
  const [isEditingNotes, setIsEditingNotes] = useState(false);
  const [isSavingNotes, setIsSavingNotes] = useState(false);
  const [notesContent, setNotesContent] = useState('');
  const [isEditingFocus, setIsEditingFocus] = useState(false);
  const [isSavingFocus, setIsSavingFocus] = useState(false);
  const [isCopying, setIsCopying] = useState(false);
  const handleWorkoutTimerUpdated = (updatedWorkout: Workout) => {
    setWorkout(updatedWorkout);
  };

  const getWorkoutFlowStage = (workout: Workout | null): 'pre_workout' | 'during_workout' | 'post_workout' => {
    if (!workout) return 'pre_workout';
    
    // If workout has finished timing, show completion
    if (workout.finish_time) return 'post_workout';
    
    // If workout has started timing, show during workout
    if (workout.start_time) return 'during_workout';
    
    // If no timing but exercises exist, show pre-workout
    return 'pre_workout';
  };

  useEffect(() => {
    if (!dayId) return;

    const fetchDayData = async () => {
      setIsLoading(true);
      try {
        // Log current operation
        console.log('Fetching day data for dayId:', dayId);
        const dayData = await getDay(dayId);
        setDay(dayData);

        // Determine the correct athlete ID for workout lookup
        let athleteId = user.user_id;
        
        console.log('Current user ID:', user.user_id);
        console.log('Current user role:', user.role);
        console.log('Block ID from query params:', blockId);
        
        if (blockId && user.role === 'coach') {
          try {
            console.log('Fetching block data for ID:', blockId);
            const blockData = await getBlock(blockId);
            console.log('Block data received:', blockData);
            
            if (blockData && blockData.athlete_id) {
              athleteId = blockData.athlete_id;
              console.log('Using athlete ID from block:', athleteId);
            }
          } catch (blockErr) {
            console.error('Error fetching block data:', blockErr);
          }
        }

        // Try to load existing workout with the appropriate athlete ID
        console.log('Fetching workout with athlete ID:', athleteId, 'day ID:', dayId);
        try {
          const workoutData = await getWorkoutByDay(athleteId, dayId);
          console.log('Workout data received:', workoutData);
          setWorkout(workoutData);
        } catch (err) {
          console.log('No workout yet or error loading it:', err);
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
  }, [dayId, user.user_id, user.role, blockId]);

  useEffect(() => {
    if (day) {
      setNotesContent(day.notes || '');
    }
  }, [day]);

  useEffect(() => {
    if (contentEditableRef.current && !isEditingNotes) {
      contentEditableRef.current.textContent = notesContent;
    }
  }, [notesContent, isEditingNotes]);


  const handleWorkoutSaved = async () => {
    if (!user || !dayId) {
      console.error('Missing user or dayId');
      return;
    }
    try {
      // Determine the correct athlete ID
      let currentAthleteId = user.user_id;
      
      if (blockId && user.role === 'coach') {
        try {
          const blockData = await getBlock(blockId);
          if (blockData && blockData.athlete_id) {
            currentAthleteId = blockData.athlete_id;
            console.log('Using athlete ID for workout refresh:', currentAthleteId);
          }
        } catch (blockErr) {
          console.error('Error fetching block data:', blockErr);
        }
      }
      
      // UPDATE STATE:
      setAthleteId(currentAthleteId);
      
      const workoutData = await getWorkoutByDay(currentAthleteId, dayId);
      setWorkout(workoutData);
      setShowWorkoutForm(false);
      toast.success('Workout saved successfully!');
    } catch (err) {
      console.error('Error refreshing workout:', err);
      toast.error('Error loading workout data');
    }
  };

  const refreshWorkoutData = async () => {
    if (!user || !dayId) {
      console.error('Missing user or dayId for refresh');
      return;
    }
    
    try {
      console.log('Refreshing workout data');
      
      // Determine the correct athlete ID
      let currentAthleteId = user.user_id;
      
      if (blockId && user.role === 'coach') {
        try {
          const blockData = await getBlock(blockId);
          if (blockData && blockData.athlete_id) {
            currentAthleteId = blockData.athlete_id;
            console.log('Refreshing with athlete ID:', currentAthleteId);
          }
        } catch (blockErr) {
          console.error('Error fetching block data:', blockErr);
        }
      }
      
      // UPDATE STATE:
      setAthleteId(currentAthleteId);
      
      console.log('Refreshing workout with athlete ID:', currentAthleteId, 'day ID:', dayId);
      const workoutData = await getWorkoutByDay(currentAthleteId, dayId);  
      if (workoutData) {
        console.log('Updated workout data:', workoutData);
        setWorkout(workoutData);
      }
    } catch (err) {
      console.error('Error refreshing workout data:', err);
      toast.error('Error refreshing workout');
    }
  };

  const handleCopyWorkout = async (targetDayId: string) => {
    if (!dayId) return;

    setCopyError(null);
    setIsCopying(true);

    try {
      console.log('Starting workout copy from day', dayId, 'to day', targetDayId);
      await copyWorkout(dayId, targetDayId);

      // Show success message and close modal
      toast.success('Workout copied successfully!');
      setShowCopyModal(false);
    } catch (error) {
      console.error('Error copying workout:', error);

      // Display specific error message if available from API
      if (error instanceof ApiError) {
        setCopyError(error.message);
      } else {
        setCopyError('Failed to copy workout. Please try again.');
      }
    } finally {
      setIsCopying(false);
    }
  };

  const navigateBack = () => {
    if (blockId) {
      // Navigate to the path including the blockId
      navigate(`/blocks/${blockId}`);
    } else {
      // If no blockId, navigate to the general blocks path
      navigate('/blocks');
    }
  };

  const handleNotesClick = () => {
    setIsEditingNotes(true);
    requestAnimationFrame(() => {
      if (contentEditableRef.current) {
        contentEditableRef.current.textContent = notesContent;
        contentEditableRef.current.focus();
      }
    });
  }

  const handleNotesBlur = async () => {
    if (!contentEditableRef.current) return;
    const newText = contentEditableRef.current.textContent?.trim() || '';
    setNotesContent(newText);

    if (!day || newText === (day.notes || '')) {
      setIsEditingNotes(false);
      return;
    }

    setIsSavingNotes(true);
    try {
      await updateDay(day.day_id, { notes: newText });
      setDay(d => d ? { ...d, notes: newText } : null);
      toast.success('Notes saved successfully!');
    } catch {
      toast.error('Failed to save notes');
      setNotesContent(day.notes || '');
    } finally {
      setIsEditingNotes(false);
      setIsSavingNotes(false);
    }
  }

  const handleNotesKeyDown = (e: React.KeyboardEvent) => {
    // Save on Enter key (optional UX enhancement)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      (e.target as HTMLElement).blur();
    }
    // Cancel on Escape
    if (e.key === 'Escape') {
      setNotesContent(day?.notes || '');
      setIsEditingNotes(false);
    }
  };

  const handleNotesChange = (e: React.FormEvent<HTMLDivElement>) => {
    setNotesContent(e.currentTarget.textContent || '');
  };

  const contentEditableRef = useRef<HTMLDivElement>(null);

  // Focus editing handlers
  const focusOptions = [
    { value: '', label: 'No focus' },
    { value: 'squat', label: 'Squat' },
    { value: 'bench', label: 'Bench' },
    { value: 'deadlift', label: 'Deadlift' },
    { value: 'cardio', label: 'Cardio' },
    { value: 'rest', label: 'Rest' }
  ];

  const handleFocusClick = () => {
    setIsEditingFocus(true);
  };

  const handleFocusChange = async (newFocus: string) => {
    if (!day || newFocus === (day.focus || '')) {
      setIsEditingFocus(false);
      return;
    }

    setIsSavingFocus(true);
    try {
      await updateDay(day.day_id, { focus: newFocus || null });
      // Update only the focus field
      setDay(prev => prev ? { ...prev, focus: newFocus || null } : null);
      toast.success('Focus updated successfully!');
    } catch (error) {
      console.error('Error saving focus:', error);
      toast.error('Failed to update focus');
    } finally {
      setIsEditingFocus(false);
      setIsSavingFocus(false);
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
            {/* Side-by-Side Focus/Notes, Workout Overview Below */}
            <div className="space-y-4 mb-6">
              {/* Focus and Notes - Side by Side */}
              <div className="grid grid-cols-2 gap-4">
                {/* Focus Section */}
                <div className="space-y-2">
                  <h2 className="text-xs font-medium text-gray-500 uppercase tracking-wide">Focus</h2>
                  {day.focus || isEditingFocus ? (
                    <div className="relative">
                      {isEditingFocus ? (
                        <div className="relative">
                          <div className="bg-white border border-gray-300 rounded-md shadow-lg py-1 z-10 absolute top-0 left-0 min-w-[120px]">
                            {focusOptions.map(option => (
                              <button
                                key={option.value}
                                onClick={() => handleFocusChange(option.value)}
                                className="w-full text-left px-3 py-2 hover:bg-gray-100 flex items-center space-x-2"
                                disabled={isSavingFocus}
                              >
                                {option.value ? (
                                  <FocusTag focus={option.value} size="sm" />
                                ) : (
                                  <span className="text-gray-500 italic text-sm">No focus</span>
                                )}
                              </button>
                            ))}
                          </div>
                          <div className="fixed inset-0 z-0" onClick={() => setIsEditingFocus(false)} />
                        </div>
                      ) : (
                        <div 
                          onClick={handleFocusClick}
                          className={`inline-block cursor-pointer p-1 rounded transition-all duration-200 hover:bg-gray-100 ${isSavingFocus ? 'opacity-50' : ''}`}
                        >
                          <FocusTag focus={day.focus || ''} size="sm" />
                          {isSavingFocus && (
                            <div className="inline-block ml-2">
                              <div className="animate-spin h-3 w-3 border-2 border-blue-500 border-t-transparent rounded-full"></div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ) : (
                    <div 
                      onClick={handleFocusClick}
                      className="cursor-pointer p-1 rounded transition-all duration-200 hover:bg-gray-100"
                    >
                      <span className="text-gray-400 italic text-xs px-2 py-1 border border-gray-200 rounded">
                        Set focus...
                      </span>
                    </div>
                  )}
                </div>

                {/* Notes Section */}
                <div className="space-y-2">
                  <h2 className="text-xs font-medium text-gray-500 uppercase tracking-wide">Notes</h2>
                  {notesContent || isEditingNotes ? (
                    <div className="relative">
                      <div
                        ref={contentEditableRef}
                        contentEditable
                        suppressContentEditableWarning={true}
                        onFocus={handleNotesClick}
                        onBlur={handleNotesBlur}
                        onKeyDown={handleNotesKeyDown}
                        onInput={handleNotesChange}
                        className={`min-h-[2rem] p-2 text-sm rounded border-2 transition-all duration-200 outline-none ${
                          isEditingNotes 
                            ? 'border-blue-300 bg-blue-50 shadow-sm' 
                            : 'border-transparent hover:border-gray-200 hover:bg-gray-50 cursor-text'
                        } ${isSavingNotes ? 'opacity-50' : ''}`}
                        style={{
                          whiteSpace: 'pre-wrap',
                          wordBreak: 'break-word'
                        }}
                      >
                        {!isEditingNotes && notesContent}
                      </div>
                      {isSavingNotes && (
                        <div className="absolute right-2 top-2">
                          <div className="animate-spin h-3 w-3 border-2 border-blue-500 border-t-transparent rounded-full"></div>
                        </div>
                      )}
                      {!isEditingNotes && !day.notes && (
                        <div 
                          onClick={handleNotesClick}
                          className="absolute inset-0 flex items-center text-gray-400 italic cursor-text p-2 text-sm"
                        >
                          Click to add notes...
                        </div>
                      )}
                    </div>
                  ) : (
                    <div 
                      onClick={handleNotesClick}
                      className="min-h-[2rem] p-2 cursor-pointer rounded transition-all duration-200 hover:bg-gray-100 border border-gray-200"
                    >
                      <span className="text-gray-400 italic text-sm">Click to add notes...</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Workout Overview - Full Width Below Focus/Notes */}
              {workout && (getWorkoutFlowStage(workout) === 'pre_workout' || getWorkoutFlowStage(workout) === 'post_workout') && (
                <div className="w-full">
                  {getWorkoutFlowStage(workout) === 'pre_workout' && (
                    <WorkoutSummary workout={workout} />
                  )}
                  {getWorkoutFlowStage(workout) === 'post_workout' && (
                    <WorkoutCompletion 
                      key={`${workout.workout_id}-${workout.exercises.length}-${JSON.stringify(workout.exercises.map(ex => ex.sets_data?.length || 0))}`}
                      workout={workout} 
                    />
                  )}
                </div>
              )}
            </div>
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
                    <button
                      onClick={() => setShowCopyModal(true)}
                      disabled={isCopying}
                      className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 disabled:opacity-50"
                    >
                      {isCopying ? 'Copying...' : 'Copy to Another Day'}
                    </button>
                  </div>
                </div>

                {/* Enhanced Workout Flow Components - Only WorkoutTimer */}
                <div className="space-y-4">
                  {/* Workout Timer */}
                  <WorkoutTimer
                    workout={workout}
                    onWorkoutUpdated={handleWorkoutTimerUpdated}
                    readOnly={user?.role !== 'athlete' && workout.athlete_id !== user?.user_id}
                  />
                </div>
                
                <ExerciseList
                  exercises={workout.exercises}
                  workoutId={workout.workout_id}
                  dayId={dayId}
                  athleteId={athleteId}
                  onExerciseComplete={refreshWorkoutData}
                  readOnly={false}
                />
              </div>
            ) : showWorkoutForm ? (
              <WorkoutForm 
                dayId={dayId || ''} 
                onSave={handleWorkoutSaved}
                athleteId={athleteId}
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