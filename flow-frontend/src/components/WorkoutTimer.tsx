import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { Button } from '@/components/ui/button';
import { startWorkoutSession, finishWorkoutSession, ApiError } from '../services/api';
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
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
      {/* Compact timer layout */}
      <div className="flex items-center justify-between">
        {/* Status indicator and exercise progress */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${
              timerStatus === 'not_started' ? 'bg-ocean-slate' :
              timerStatus === 'in_progress' ? 'bg-state-active animate-pulse' :
              'bg-state-completed'
            }`} />
            <span className="text-sm text-gray-600 capitalize">
              {timerStatus === 'not_started' ? 'Ready to start' :
               timerStatus === 'in_progress' ? 'In progress' :
               'Completed'}
            </span>
          </div>

          {/* Exercise completion status - compact */}
          {workout.exercises && workout.exercises.length > 0 && (
            <div className="text-sm text-gray-500">
              <span className={`font-medium ${
                exerciseStatus.completed === exerciseStatus.total ? 'text-green-600' : 'text-orange-600'
              }`}>
                {exerciseStatus.completed}/{exerciseStatus.total} exercises
                {exerciseStatus.completed === exerciseStatus.total && ' ✅'}
              </span>
            </div>
          )}
        </div>

        {/* Duration display - smaller and inline */}
        {duration && (
          <div className="text-sm font-medium text-gray-700">
            {duration}
          </div>
        )}
      </div>

      {/* Control Buttons - more compact */}
      {!readOnly && (
        <div className="mt-3 flex items-center space-x-2">
          {timerStatus === 'not_started' && (
            <Button
              type="button"
              onClick={handleStartSession}
              disabled={isStarting}
            >
              {isStarting ? 'Starting...' : 'Start Workout'}
            </Button>
          )}
          
          {timerStatus === 'in_progress' && (
            <div className="flex items-center space-x-2">
              <Button
                type="button"
                variant="secondary"
                onClick={handleFinishSession}
                disabled={isFinishing || !allExercisesCompleted()}
              >
                {isFinishing ? 'Finishing...' : 'Finish Workout'}
              </Button>
              {!allExercisesCompleted() && (
                <span className="text-xs text-orange-600">
                  Complete all exercises first
                </span>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default WorkoutTimer;