import { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import Layout from '../components/Layout';
import WorkoutForm from '../components/WorkoutForm';
import DaySelector from '../components/DaySelector';
import { getDay, getWorkoutByDay, getEffectiveAthleteId, copyWorkout, ApiError } from '../services/api';
import type { Day, Workout } from '../services/api';
import { formatDate } from '../utils/dateUtils';
import FocusTag from '../components/FocusTag';
import { FOCUS_OPTIONS, MAX_FOCUS_SELECTIONS, parseFocusTags, formatFocusTags } from '../constants/focusOptions';
import { toast } from 'react-toastify';
import ExerciseList from '../components/ExerciseList';
import { updateDay } from '../services/api';
import WorkoutTimer from '../components/WorkoutTimer';
import WorkoutSummary from '../components/WorkoutSummary';
import WorkoutCompletion from '../components/WorkoutCompletion';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { MoreVertical, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';


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
  const [showNotesModal, setShowNotesModal] = useState(false);
  const [isSavingNotes, setIsSavingNotes] = useState(false);
  const [notesContent, setNotesContent] = useState('');
  const [editingNotesValue, setEditingNotesValue] = useState('');
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
        const dayData = await getDay(dayId);
        setDay(dayData);

        // Get effective athlete ID (handles coach viewing athlete's block)
        const effectiveAthleteId = await getEffectiveAthleteId(user.user_id, user.role, blockId);
        setAthleteId(effectiveAthleteId);

        // Load workout with the appropriate athlete ID
        try {
          const workoutData = await getWorkoutByDay(effectiveAthleteId, dayId);
          setWorkout(workoutData);
        } catch {
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



  const handleWorkoutSaved = async () => {
    if (!user || !dayId) return;

    try {
      const effectiveAthleteId = await getEffectiveAthleteId(user.user_id, user.role, blockId);
      setAthleteId(effectiveAthleteId);

      const workoutData = await getWorkoutByDay(effectiveAthleteId, dayId);
      setWorkout(workoutData);
      setShowWorkoutForm(false);
      toast.success('Workout saved successfully!');
    } catch (err) {
      console.error('Error refreshing workout:', err);
      toast.error('Error loading workout data');
    }
  };

  const refreshWorkoutData = async () => {
    if (!user || !dayId) return;

    try {
      const effectiveAthleteId = await getEffectiveAthleteId(user.user_id, user.role, blockId);
      setAthleteId(effectiveAthleteId);

      const workoutData = await getWorkoutByDay(effectiveAthleteId, dayId);
      if (workoutData) {
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

  const handleOpenNotesModal = () => {
    setEditingNotesValue(notesContent);
    setShowNotesModal(true);
  };

  const handleSaveNotes = async () => {
    const newText = editingNotesValue.trim();

    if (!day || newText === (day.notes || '')) {
      setShowNotesModal(false);
      return;
    }

    setIsSavingNotes(true);
    try {
      await updateDay(day.day_id, { notes: newText });
      setDay(d => d ? { ...d, notes: newText } : null);
      setNotesContent(newText);
      toast.success('Notes saved!');
      setShowNotesModal(false);
    } catch {
      toast.error('Failed to save notes');
    } finally {
      setIsSavingNotes(false);
    }
  };

  // Focus editing handled via imported constants

  const handleFocusClick = () => {
    setIsEditingFocus(true);
  };

  const handleFocusToggle = (value: string) => {
    if (!day) return;

    const currentTags = parseFocusTags(day.focus);
    const index = currentTags.indexOf(value);

    if (index >= 0) {
      currentTags.splice(index, 1);
    } else if (currentTags.length < MAX_FOCUS_SELECTIONS) {
      currentTags.push(value);
    }

    const newFocus = formatFocusTags(currentTags);
    handleFocusSave(newFocus);
  };

  const handleFocusSave = async (newFocus: string) => {
    if (!day || newFocus === (day.focus || '')) {
      return;
    }

    setIsSavingFocus(true);
    try {
      await updateDay(day.day_id, { focus: newFocus || null });
      setDay(prev => prev ? { ...prev, focus: newFocus || null } : null);
    } catch (error) {
      console.error('Error saving focus:', error);
      toast.error('Failed to update focus');
    } finally {
      setIsSavingFocus(false);
    }
  };

  const handleClearFocus = async () => {
    setIsSavingFocus(true);
    try {
      await updateDay(day!.day_id, { focus: null });
      setDay(prev => prev ? { ...prev, focus: null } : null);
      setIsEditingFocus(false);
    } catch (error) {
      console.error('Error clearing focus:', error);
      toast.error('Failed to clear focus');
    } finally {
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
          <div className="flex items-center justify-between">
            {/* Left: Back button */}
            <button onClick={navigateBack} className="text-xs text-gray-500 hover:text-ocean-teal w-24">
              ← Back to Block
            </button>

            {/* Center: Day title */}
            <h1 className="text-xl font-semibold text-ocean-navy-dark">
              Day {day.day_number} - {formatDate(day.date)}
            </h1>

            {/* Right: Overflow menu */}
            <div className="w-24 flex justify-end">
              {workout && (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <button className="p-1.5 rounded hover:bg-gray-100 text-gray-500">
                      <MoreVertical className="h-5 w-5" />
                    </button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem
                      onClick={() => setShowCopyModal(true)}
                      disabled={isCopying}
                    >
                      {isCopying ? 'Copying...' : 'Copy to Another Day'}
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              )}
            </div>
          </div>

          {/* Focus and Notes - Inline Row */}
          <div className="flex items-center justify-between mb-4">
            {/* Focus Trigger */}
            <button
              onClick={handleFocusClick}
              className={`cursor-pointer rounded transition-all duration-200 hover:bg-gray-100 ${isSavingFocus ? 'opacity-50' : ''}`}
            >
              {day.focus ? (
                <div className="flex gap-1">
                  {parseFocusTags(day.focus).map(tag => (
                    <FocusTag key={tag} focus={tag} size="sm" />
                  ))}
                </div>
              ) : (
                <span className="text-gray-400 text-sm px-2 py-1 border border-dashed border-gray-300 rounded">
                  + Focus
                </span>
              )}
            </button>

            {/* Notes Button/Preview */}
            <button
              onClick={handleOpenNotesModal}
              className="flex items-center space-x-1.5 text-sm text-gray-500 hover:text-ocean-teal transition-colors max-w-[200px]"
            >
              <FileText className="h-4 w-4 flex-shrink-0" />
              {notesContent ? (
                <span className="truncate">{notesContent}</span>
              ) : (
                <span className="text-gray-400">Notes</span>
              )}
            </button>
          </div>

          {/* Workout Overview */}
          {workout && (getWorkoutFlowStage(workout) === 'pre_workout' || getWorkoutFlowStage(workout) === 'post_workout') && (
            <div className="mb-4">
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

          <div className="bg-white shadow rounded-lg overflow-hidden">
            {copyError && (
              <div className="mx-4 mt-4 bg-red-50 border border-red-200 text-red-700 rounded p-3">
                {copyError}
              </div>
            )}

            {workout ? (
              <div>
                <WorkoutTimer
                  workout={workout}
                  onWorkoutUpdated={handleWorkoutTimerUpdated}
                  readOnly={user?.role !== 'athlete' && workout.athlete_id !== user?.user_id}
                />

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
              <div className="p-4">
                <WorkoutForm
                  dayId={dayId || ''}
                  onSave={handleWorkoutSaved}
                  athleteId={athleteId}
                />
              </div>
            ) : (
              <div className="text-center py-8 px-4">
                <p className="text-ocean-slate mb-2">Ready to plan this session?</p>
                <p className="text-sm text-ocean-slate-light mb-4">Add exercises to build your workout.</p>
                <button
                  onClick={() => setShowWorkoutForm(true)}
                  className="px-4 py-2 bg-ocean-teal text-white rounded hover:bg-ocean-navy transition-colors"
                >
                  Create Workout
                </button>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <p className="text-ocean-slate">Day not found</p>
          <button
            onClick={navigateBack}
            className="mt-4 px-4 py-2 bg-ocean-mist text-ocean-navy rounded hover:bg-ocean-slate-light transition-colors"
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

      {/* Notes Modal */}
      {showNotesModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-4">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-lg font-medium text-gray-900">Day Notes</h3>
              <button
                onClick={() => setShowNotesModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            <textarea
              value={editingNotesValue}
              onChange={(e) => setEditingNotesValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Escape') setShowNotesModal(false);
              }}
              className="w-full px-3 py-2 text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-ocean-teal"
              rows={4}
              placeholder="Add notes for this day..."
              autoFocus
            />
            <div className="flex justify-end space-x-2 mt-3">
              <Button
                variant="outline"
                onClick={() => setShowNotesModal(false)}
              >
                Cancel
              </Button>
              <Button
                onClick={handleSaveNotes}
                disabled={isSavingNotes}
              >
                {isSavingNotes ? 'Saving...' : 'Save'}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Focus Modal */}
      {isEditingFocus && day && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-sm p-4">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-lg font-medium text-gray-900">Training Focus</h3>
              <button
                onClick={() => setIsEditingFocus(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            <p className="text-sm text-gray-500 mb-3">Select up to {MAX_FOCUS_SELECTIONS}</p>
            <div className="grid grid-cols-3 gap-2">
              {FOCUS_OPTIONS.map(option => {
                const currentTags = parseFocusTags(day.focus);
                const isSelected = currentTags.includes(option.value);
                const isDisabled = !isSelected && currentTags.length >= MAX_FOCUS_SELECTIONS;
                return (
                  <button
                    key={option.value}
                    onClick={() => handleFocusToggle(option.value)}
                    disabled={isSavingFocus || isDisabled}
                    className={`p-2 rounded border transition-all ${
                      isSelected
                        ? 'ring-2 ring-ocean-teal ring-offset-1 bg-ocean-seafoam-light'
                        : isDisabled
                        ? 'opacity-40 cursor-not-allowed'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <FocusTag focus={option.value} size="sm" />
                  </button>
                );
              })}
            </div>
            <div className="flex justify-between items-center mt-4">
              {parseFocusTags(day.focus).length > 0 ? (
                <button
                  onClick={handleClearFocus}
                  className="text-sm text-gray-400 hover:text-red-500"
                  disabled={isSavingFocus}
                >
                  Clear all
                </button>
              ) : (
                <div />
              )}
              <Button
                onClick={() => setIsEditingFocus(false)}
                disabled={isSavingFocus}
              >
                Done
              </Button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
};

export default DayDetail;