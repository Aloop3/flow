import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { Button } from '@/components/ui/button';
import { startWorkoutSession, finishWorkoutSession, cancelWorkoutSession, ApiError } from '../services/api';
import type { Workout } from '../services/api';

interface WorkoutTimerProps {
  workout: Workout;
  onWorkoutUpdated: (updatedWorkout: Workout) => void;
  readOnly?: boolean;
}

const WorkoutTimer: React.FC<WorkoutTimerProps> = ({
  workout,
  onWorkoutUpdated,
  readOnly = false,
}) => {
  const [isStarting, setIsStarting] = useState(false);
  const [isFinishing, setIsFinishing] = useState(false);
  const [isCancelling, setIsCancelling] = useState(false);
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());

  // Update current time every second for live duration counter
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // Check if all exercises are completed
  const allExercisesCompleted = (): boolean => {
    if (!workout.exercises || workout.exercises.length === 0) {
      return false;
    }
    return workout.exercises.every(exercise => exercise.status === 'completed');
  };

  // Get exercise completion status for UI feedback
  const getExerciseCompletionStatus = (): { completed: number; total: number } => {
    if (!workout.exercises || workout.exercises.length === 0) {
      return { completed: 0, total: 0 };
    }
    const completed = workout.exercises.filter(ex => ex.status === 'completed').length;
    return { completed, total: workout.exercises.length };
  };

  const handleStartSession = async () => {
    if (isStarting || readOnly) return;

    setIsStarting(true);
    try {
      const updatedWorkout = await startWorkoutSession(workout.workout_id);
      onWorkoutUpdated(updatedWorkout);
      toast.success('Workout timer started!');
    } catch (error) {
      console.error('Error starting workout session:', error);
      
      if (error instanceof ApiError && error.statusCode === 403) {
        toast.error('You do not have permission to start this workout');
      } else {
        toast.error('Failed to start workout timer');
      }
    } finally {
      setIsStarting(false);
    }
  };

  const handleCancelClick = () => {
    setShowCancelConfirm(true);
  };

  const handleCancelConfirm = async () => {
    if (isCancelling || readOnly) return;

    setIsCancelling(true);
    setShowCancelConfirm(false);
    try {
      const updatedWorkout = await cancelWorkoutSession(workout.workout_id);
      onWorkoutUpdated(updatedWorkout);
      toast.success('Workout cancelled');
    } catch (error) {
      console.error('Error cancelling workout session:', error);
      toast.error('Failed to cancel workout');
    } finally {
      setIsCancelling(false);
    }
  };

  const handleFinishSession = async () => {
    if (isFinishing || readOnly) return;

    // Check if all exercises are completed before allowing finish
    if (!allExercisesCompleted()) {
      const { completed, total } = getExerciseCompletionStatus();
      toast.error(`Complete all exercises before finishing workout (${completed}/${total} completed)`);
      return;
    }

    setIsFinishing(true);
    try {
      const updatedWorkout = await finishWorkoutSession(workout.workout_id);
      onWorkoutUpdated(updatedWorkout);
      toast.success('Workout completed! 🎉');
    } catch (error) {
      console.error('Error finishing workout session:', error);
      
      if (error instanceof ApiError && error.statusCode === 400) {
        toast.error('Cannot finish workout - timer not started or already finished');
      } else if (error instanceof ApiError && error.statusCode === 403) {
        toast.error('You do not have permission to finish this workout');
      } else {
        toast.error('Failed to finish workout timer');
      }
    } finally {
      setIsFinishing(false);
    }
  };
  
  const calculateDuration = (): string | null => {
    if (!workout.start_time) return null;

    // Parse times and handle timezone consistently
    const startTime = new Date(workout.start_time);
    const endTime = workout.finish_time ? new Date(workout.finish_time) : currentTime;
    
    const durationMs = endTime.getTime() - startTime.getTime();
    const durationMinutes = Math.floor(durationMs / (1000 * 60));
    const durationSeconds = Math.floor((durationMs % (1000 * 60)) / 1000);
    
    const hours = Math.floor(durationMinutes / 60);
    const minutes = durationMinutes % 60;
    
    // Handle different time formats based on duration
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}`;
    } else if (minutes > 0) {
      return `${minutes}m`;
    } else {
      // Show seconds for workouts under 1 minute
      return `${durationSeconds}s`;
    }
  };

  const getTimerStatus = (): 'not_started' | 'in_progress' | 'finished' => {
    if (!workout.start_time) return 'not_started';
    if (!workout.finish_time) return 'in_progress';
    return 'finished';
  };

  const timerStatus = getTimerStatus();
  const duration = calculateDuration();
  const exerciseStatus = getExerciseCompletionStatus();

  return (
    <>
      <div className="sticky top-0 z-10 bg-white border-b border-gray-200 px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Left: Cancel button (when in progress) or empty space */}
          <div className="w-20">
            {!readOnly && timerStatus === 'in_progress' && (
              <Button
                type="button"
                variant="ghost"
                onClick={handleCancelClick}
                disabled={isCancelling}
                className="text-gray-500 -ml-2"
              >
                {isCancelling ? '...' : 'Cancel'}
              </Button>
            )}
          </div>

          {/* Center: Duration + exercise progress */}
          <div className="flex flex-col items-center">
            {duration && (
              <span className="text-lg font-semibold text-gray-900">{duration}</span>
            )}
            {workout.exercises && workout.exercises.length > 0 && timerStatus !== 'not_started' && (
              <span className={`text-xs ${
                exerciseStatus.completed === exerciseStatus.total ? 'text-green-600' : 'text-gray-500'
              }`}>
                {exerciseStatus.completed} of {exerciseStatus.total} exercises
              </span>
            )}
          </div>

          {/* Right: Start/Finish button */}
          <div className="w-20 flex justify-end">
            {!readOnly && timerStatus === 'not_started' && (
              <Button
                type="button"
                onClick={handleStartSession}
                disabled={isStarting}
                className="px-8"
              >
                {isStarting ? '...' : 'Start'}
              </Button>
            )}
            {!readOnly && timerStatus === 'in_progress' && (
              <Button
                type="button"
                onClick={handleFinishSession}
                disabled={isFinishing || !allExercisesCompleted()}
                className={!allExercisesCompleted() ? 'opacity-50' : ''}
              >
                {isFinishing ? '...' : 'Finish'}
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Cancel Confirmation Modal */}
      {showCancelConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-lg p-6 mx-4 max-w-sm w-full shadow-xl">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Cancel Workout?</h3>
            <p className="text-sm text-gray-600 mb-4">
              This will reset the timer and clear your progress.
            </p>
            <div className="flex space-x-3">
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => setShowCancelConfirm(false)}
              >
                Keep Going
              </Button>
              <Button
                variant="destructive"
                className="flex-1"
                onClick={handleCancelConfirm}
                disabled={isCancelling}
              >
                {isCancelling ? '...' : 'Cancel Workout'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default WorkoutTimer;