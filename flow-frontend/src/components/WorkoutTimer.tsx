import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import FormButton from './FormButton';
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

    setIsFinishing(true);
    try {
      const updatedWorkout = await finishWorkoutSession(workout.workout_id);
      onWorkoutUpdated(updatedWorkout);
      toast.success('Workout timer finished!');
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
    
    // Ensure minimum 1 minute for active sessions, handle negative durations
    let durationMinutes = Math.floor(durationMs / (1000 * 60));
    
    // Handle negative durations (timezone issues)
    if (durationMinutes < 0) {
      durationMinutes = Math.abs(durationMinutes);
    }
    
    // Show minimum 1 minute for completed sessions > 0
    if (workout.finish_time && durationMinutes === 0 && durationMs > 0) {
      durationMinutes = 1;
    }
    
    if (durationMinutes < 60) {
      return `${durationMinutes}m`;
    } else {
      const hours = Math.floor(durationMinutes / 60);
      const minutes = durationMinutes % 60;
      return `${hours}h ${minutes}m`;
    }
  };

  const formatTime = (timeString: string): string => {
    const date = new Date(timeString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getTimerStatus = (): 'not_started' | 'in_progress' | 'finished' => {
    if (!workout.start_time) return 'not_started';
    if (workout.finish_time) return 'finished';
    return 'in_progress';
  };

  const timerStatus = getTimerStatus();
  const duration = calculateDuration();

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h3 className="text-lg font-medium text-gray-900">Workout Timer</h3>
          
          {/* Timer Status Indicator */}
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${
              timerStatus === 'not_started' ? 'bg-gray-400' :
              timerStatus === 'in_progress' ? 'bg-green-400 animate-pulse' :
              'bg-blue-400'
            }`} />
            <span className="text-sm text-gray-600 capitalize">
              {timerStatus === 'not_started' ? 'Ready to start' :
               timerStatus === 'in_progress' ? 'In progress' :
               'Completed'}
            </span>
          </div>
        </div>

        {/* Duration Display */}
        {duration && (
          <div className="text-right">
            <div className="text-xl font-mono font-bold text-gray-900">
              {duration}
            </div>
            {timerStatus === 'in_progress' && (
              <div className="text-xs text-gray-500">Live</div>
            )}
          </div>
        )}
      </div>

      {/* Timer Details */}
      {(workout.start_time || workout.finish_time) && (
        <div className="mt-3 grid grid-cols-2 gap-4 text-sm">
          {workout.start_time && (
            <div>
              <span className="text-gray-500">Started:</span>
              <div className="font-medium">{formatTime(workout.start_time)}</div>
            </div>
          )}
          {workout.finish_time && (
            <div>
              <span className="text-gray-500">Finished:</span>
              <div className="font-medium">{formatTime(workout.finish_time)}</div>
            </div>
          )}
        </div>
      )}

      {/* Control Buttons */}
      {!readOnly && (
        <div className="mt-4 flex space-x-2">
          {timerStatus === 'not_started' && (
            <FormButton
              type="button"
              variant="primary"
              onClick={handleStartSession}
              disabled={isStarting}
              isLoading={isStarting}
            >
              Start Workout
            </FormButton>
          )}
          
          {timerStatus === 'in_progress' && (
            <FormButton
              type="button"
              variant="secondary"
              onClick={handleFinishSession}
              disabled={isFinishing}
              isLoading={isFinishing}
            >
              Finish Workout
            </FormButton>
          )}
          
          {timerStatus === 'finished' && (
            <div className="text-sm text-gray-500 py-2">
              ✅ Workout timing completed
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default WorkoutTimer;